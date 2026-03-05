"""
Handlers for IOU commands:
  /eda                — Start IOU flow: direction → who → amount → reason → deadline
  /edawoch            — List active IOUs
  /kefel [ID]         — Mark IOU as paid (or pick from buttons)

All steps use InlineKeyboardMarkup (inline buttons) instead of ReplyKeyboardMarkup
so the experience is fully button-driven. Each state accepts both CallbackQueryHandler
(button taps) and MessageHandler (typed fallback).
"""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import Forbidden

from bot.strings.lang import s
from bot.db.models import (
    upsert_user, get_user_by_username, create_iou, get_iou,
    get_active_ious_for_user, get_user_by_id,
)
from bot.db.supabase_client import run_sync
from bot.utils.formatting import (
    birr, get_name, get_name_from_record, parse_iou_command, format_date,
    parse_amount, parse_relative_deadline,
)

# Conversation states
DIRECTION, WHO, AMOUNT, REASON, DEADLINE = range(5)

# Context keys used by the /eda conversation
_CONTEXT_KEYS = ("iou_direction", "iou_other", "iou_other_name", "iou_amount", "iou_reason")


def _cleanup_conv(context):
    """Remove all /eda conversation keys from user_data."""
    for key in _CONTEXT_KEYS:
        context.user_data.pop(key, None)


def _nav_buttons(t):
    """Return standard navigation buttons row."""
    return [
        InlineKeyboardButton(t.BTN_MY_IOUS, callback_data="go_edawoch"),
        InlineKeyboardButton(t.BTN_GO_HOME, callback_data="go_home"),
    ]


# ── Shared finalization ──────────────────────────────────────

async def _finalize_iou(user, context, chat_id):
    """Create IOU from context.user_data and notify both parties.

    Works from both message and callback contexts by using chat_id directly.
    """
    t = s(user.id)
    other = context.user_data["iou_other"]
    amount = context.user_data["iou_amount"]
    reason = context.user_data.get("iou_reason")
    direction = context.user_data.get("iou_direction", "lent")
    due_date = context.user_data.get("iou_due_date")

    if direction == "lent":
        lender_id = user.id
        lender_name = get_name(user)
        borrower = other
    else:
        lender_id = other["user_id"]
        lender_name = get_name_from_record(other)
        borrower = {"user_id": user.id, "username": user.username, "first_name": user.first_name}

    iou = await run_sync(
        create_iou,
        lender_id=lender_id,
        borrower_id=borrower["user_id"],
        amount=amount,
        description=reason,
        due_date=due_date,
    )

    borrower_name = get_name_from_record(borrower)
    lines = [
        t.IOU_NEW.format(id=iou["id"]),
        t.IOU_LENT.format(lender=lender_name, borrower=borrower_name),
        t.IOU_AMOUNT.format(amount=birr(amount)),
    ]
    if reason:
        lines.append(t.IOU_REASON.format(desc=reason))
    if due_date:
        lines.append(t.IOU_DUE.format(date=format_date(due_date)))
    lines.append("")
    lines.append(t.IOU_WAITING.format(name=borrower_name))

    # Navigation buttons after IOU creation
    keyboard = InlineKeyboardMarkup([_nav_buttons(t)])
    await context.bot.send_message(
        chat_id=chat_id, text="\n".join(lines), reply_markup=keyboard,
    )

    # DM the OTHER party for confirmation
    initiator_id = user.id
    other_id = borrower["user_id"] if initiator_id == lender_id else lender_id
    ot = s(other_id)

    if initiator_id == lender_id:
        confirm_text = ot.IOU_CONFIRM_REQUEST.format(
            lender=lender_name, amount=birr(amount), desc=reason or "-",
        )
    else:
        confirm_text = ot.IOU_CONFIRM_LENDER_REQUEST.format(
            borrower=borrower_name, amount=birr(amount), desc=reason or "-",
        )

    confirm_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(ot.BTN_CONFIRM, callback_data=f"iou_confirm_{iou['id']}"),
            InlineKeyboardButton(ot.BTN_DISPUTE, callback_data=f"iou_dispute_{iou['id']}"),
        ]
    ])

    try:
        await context.bot.send_message(
            chat_id=other_id, text=confirm_text, reply_markup=confirm_kb,
        )
    except Forbidden:
        bot_me = await context.bot.get_me()
        other_username = borrower.get("username", "?") if other_id == borrower["user_id"] else "?"
        await context.bot.send_message(
            chat_id=chat_id,
            text=t.ERR_DM_FAILED.format(username=other_username)
            + "\n\n" + t.INVITE_MESSAGE.format(bot_username=bot_me.username),
        )

    _cleanup_conv(context)


# ── Conversational flow ──────────────────────────────────────

async def eda_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /eda — show direction buttons (inline)."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t.BTN_I_LENT, callback_data="iou_dir_lent"),
            InlineKeyboardButton(t.BTN_I_BORROWED, callback_data="iou_dir_borrowed"),
        ]
    ])
    await update.message.reply_text(t.CONV_DIRECTION, reply_markup=keyboard)
    return DIRECTION


# ── DIRECTION step (callback) ──

async def conv_direction_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 1 (callback): User taps 'I lent' or 'I borrowed' inline button."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    if query.data == "iou_dir_lent":
        context.user_data["iou_direction"] = "lent"
        await query.edit_message_text(t.CONV_WHO_BORROWED)
    else:
        context.user_data["iou_direction"] = "borrowed"
        await query.edit_message_text(t.CONV_WHO_LENT)

    return WHO


async def conv_direction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 1 (text fallback): User types direction."""
    user = update.effective_user
    t = s(user.id)
    text = update.message.text.strip()

    if text == t.BTN_I_LENT or text.lower() in ("i lent", "lent", "አበድሬያለሁ"):
        context.user_data["iou_direction"] = "lent"
        await update.message.reply_text(t.CONV_WHO_BORROWED)
    elif text == t.BTN_I_BORROWED or text.lower() in ("i borrowed", "borrowed", "ተበድሬያለሁ"):
        context.user_data["iou_direction"] = "borrowed"
        await update.message.reply_text(t.CONV_WHO_LENT)
    else:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(t.BTN_I_LENT, callback_data="iou_dir_lent"),
                InlineKeyboardButton(t.BTN_I_BORROWED, callback_data="iou_dir_borrowed"),
            ]
        ])
        await update.message.reply_text(t.CONV_DIRECTION, reply_markup=keyboard)
        return DIRECTION

    return WHO


# ── WHO step (text only — must type @username) ──

async def conv_who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 2: User sends @username of the other party."""
    user = update.effective_user
    t = s(user.id)
    text = update.message.text.strip()

    username = text.lstrip("@").strip()
    if not username:
        if context.user_data.get("iou_direction") == "lent":
            await update.message.reply_text(t.CONV_WHO_BORROWED)
        else:
            await update.message.reply_text(t.CONV_WHO_LENT)
        return WHO

    if username.lower() == (user.username or "").lower():
        await update.message.reply_text(t.ERR_SELF_IOU)
        return WHO

    other_user = await run_sync(get_user_by_username, username)
    if not other_user:
        # Stay in WHO state — let user try again (don't end conversation)
        bot_me = await context.bot.get_me()
        await update.message.reply_text(
            t.CONV_WHO_RETRY.format(username=username)
            + "\n\n" + t.INVITE_MESSAGE.format(bot_username=bot_me.username)
        )
        return WHO

    context.user_data["iou_other"] = other_user
    context.user_data["iou_other_name"] = get_name_from_record(other_user)

    # Show amount quick-pick buttons
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1,000", callback_data="iou_amt_1000"),
            InlineKeyboardButton("5,000", callback_data="iou_amt_5000"),
        ],
        [
            InlineKeyboardButton("10,000", callback_data="iou_amt_10000"),
            InlineKeyboardButton("50,000", callback_data="iou_amt_50000"),
        ],
        [InlineKeyboardButton(t.BTN_AMT_OTHER, callback_data="iou_amt_other")],
    ])
    await update.message.reply_text(t.CONV_AMOUNT_PICK, reply_markup=keyboard)
    return AMOUNT


# ── AMOUNT step ──

async def conv_amount_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 3 (callback): User taps amount button."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    t = s(user.id)

    data = query.data  # iou_amt_1000, iou_amt_other, etc.

    if data == "iou_amt_other":
        await query.edit_message_text(t.CONV_AMOUNT_CUSTOM)
        return AMOUNT  # Wait for typed amount

    amount_str = data.replace("iou_amt_", "")
    amount = parse_amount(amount_str)
    if amount is None:
        await query.edit_message_text(t.ERR_INVALID_AMOUNT)
        return AMOUNT

    context.user_data["iou_amount"] = amount

    # Show reason step with skip button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t.BTN_SKIP, callback_data="iou_reason_skip")]
    ])
    await query.edit_message_text(t.CONV_REASON, reply_markup=keyboard)
    return REASON


async def conv_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 3 (text fallback): User types amount."""
    user = update.effective_user
    t = s(user.id)

    amount = parse_amount(update.message.text.strip())
    if amount is None:
        await update.message.reply_text(t.ERR_INVALID_AMOUNT + "\n" + t.CONV_AMOUNT_RETRY)
        return AMOUNT

    context.user_data["iou_amount"] = amount

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t.BTN_SKIP, callback_data="iou_reason_skip")]
    ])
    await update.message.reply_text(t.CONV_REASON, reply_markup=keyboard)
    return REASON


# ── REASON step ──

async def conv_reason_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 4 (callback): User taps Skip."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    t = s(user.id)

    context.user_data["iou_reason"] = None

    # Show deadline buttons
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t.BTN_3_DAYS, callback_data="iou_dl_3d"),
            InlineKeyboardButton(t.BTN_1_WEEK, callback_data="iou_dl_1w"),
            InlineKeyboardButton(t.BTN_2_WEEKS, callback_data="iou_dl_2w"),
        ],
        [
            InlineKeyboardButton(t.BTN_1_MONTH, callback_data="iou_dl_1m"),
            InlineKeyboardButton(t.BTN_3_MONTHS, callback_data="iou_dl_3m"),
        ],
        [
            InlineKeyboardButton(t.BTN_OTHER_DEADLINE, callback_data="iou_dl_other"),
            InlineKeyboardButton(t.BTN_NO_DEADLINE, callback_data="iou_dl_none"),
        ],
    ])
    await query.edit_message_text(t.CONV_DEADLINE, reply_markup=keyboard)
    return DEADLINE


async def conv_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 4 (text): User types reason."""
    user = update.effective_user
    t = s(user.id)
    text = update.message.text.strip()

    if text == t.BTN_SKIP or text.lower() == "skip":
        context.user_data["iou_reason"] = None
    else:
        context.user_data["iou_reason"] = text[:200]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t.BTN_3_DAYS, callback_data="iou_dl_3d"),
            InlineKeyboardButton(t.BTN_1_WEEK, callback_data="iou_dl_1w"),
            InlineKeyboardButton(t.BTN_2_WEEKS, callback_data="iou_dl_2w"),
        ],
        [
            InlineKeyboardButton(t.BTN_1_MONTH, callback_data="iou_dl_1m"),
            InlineKeyboardButton(t.BTN_3_MONTHS, callback_data="iou_dl_3m"),
        ],
        [
            InlineKeyboardButton(t.BTN_OTHER_DEADLINE, callback_data="iou_dl_other"),
            InlineKeyboardButton(t.BTN_NO_DEADLINE, callback_data="iou_dl_none"),
        ],
    ])
    await update.message.reply_text(t.CONV_DEADLINE, reply_markup=keyboard)
    return DEADLINE


# ── DEADLINE step ──

async def conv_deadline_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 5 (callback): User taps deadline button."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    t = s(user.id)
    from datetime import timedelta, date as date_type

    data = query.data  # iou_dl_3d, iou_dl_1w, etc.

    if data == "iou_dl_other":
        await query.edit_message_text(t.CONV_DEADLINE_CUSTOM)
        return DEADLINE  # Wait for typed deadline

    due_date = None
    today = date_type.today()
    if data == "iou_dl_none":
        due_date = None
    elif data == "iou_dl_3d":
        due_date = today + timedelta(days=3)
    elif data == "iou_dl_1w":
        due_date = today + timedelta(weeks=1)
    elif data == "iou_dl_2w":
        due_date = today + timedelta(weeks=2)
    elif data == "iou_dl_1m":
        due_date = today + timedelta(days=30)
    elif data == "iou_dl_3m":
        due_date = today + timedelta(days=90)

    context.user_data["iou_due_date"] = due_date
    chat_id = query.message.chat_id
    await _finalize_iou(user, context, chat_id)
    return ConversationHandler.END


async def conv_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 5 (text fallback): User types date/period."""
    user = update.effective_user
    t = s(user.id)
    text = update.message.text.strip()
    from datetime import timedelta, date as date_type

    due_date = None

    # Check text buttons (backward compat with reply keyboards)
    if text == t.BTN_NO_DEADLINE or text.lower() in ("no deadline", "skip"):
        due_date = None
    elif text == t.BTN_3_DAYS or text.lower() == "3 days":
        due_date = date_type.today() + timedelta(days=3)
    elif text == t.BTN_1_WEEK or text.lower() == "1 week":
        due_date = date_type.today() + timedelta(weeks=1)
    elif text == t.BTN_2_WEEKS or text.lower() == "2 weeks":
        due_date = date_type.today() + timedelta(weeks=2)
    elif text == t.BTN_1_MONTH or text.lower() == "1 month":
        due_date = date_type.today() + timedelta(days=30)
    elif text == t.BTN_3_MONTHS or text.lower() == "3 months":
        due_date = date_type.today() + timedelta(days=90)
    elif text == t.BTN_OTHER_DEADLINE or text.lower() == "other":
        await update.message.reply_text(t.CONV_DEADLINE_CUSTOM)
        return DEADLINE
    else:
        # Try relative expressions: "10 days", "3 weeks", "2 months"
        due_date = parse_relative_deadline(text)
        if due_date is None:
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
                try:
                    due_date = datetime.strptime(text, fmt).date()
                    break
                except ValueError:
                    continue

        if due_date is None:
            await update.message.reply_text(t.CONV_DEADLINE_RETRY)
            return DEADLINE

    context.user_data["iou_due_date"] = due_date
    chat_id = update.effective_chat.id
    await _finalize_iou(user, context, chat_id)
    return ConversationHandler.END


# ── Cancel handlers ──

async def conv_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Explicit /cancel — show cancellation message."""
    t = s(update.effective_user.id)
    await update.message.reply_text(t.CONV_CANCELLED)
    _cleanup_conv(context)
    return ConversationHandler.END


async def conv_cancel_silent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Silent cancel — clean up without announcement (for fallback commands)."""
    _cleanup_conv(context)
    return ConversationHandler.END


# ── Non-conversational commands ───────────────────────────────

async def edawoch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /edawoch (list IOUs) command. Shows pay buttons for confirmed IOUs."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    ious = await run_sync(get_active_ious_for_user, user.id)

    if not ious["as_lender"] and not ious["as_borrower"]:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(t.BTN_I_LENT, callback_data="iou_dir_lent"),
            InlineKeyboardButton(t.BTN_GO_HOME, callback_data="go_home"),
        ]])
        await update.message.reply_text(t.IOU_LIST_EMPTY, reply_markup=keyboard)
        return

    lines = [t.IOU_LIST_HEADER.format(name=get_name(user))]

    # Collect confirmed IOUs for pay buttons
    confirmed_ious = []

    if ious["as_lender"]:
        lines.append(t.IOU_LIST_AS_LENDER)
        for i in ious["as_lender"]:
            other = get_user_by_id(i["borrower_id"])
            other_name = get_name_from_record(other) if other else str(i["borrower_id"])
            status = t.STATUS_MAP.get(i["status"], i["status"])
            lines.append(t.IOU_LIST_ITEM.format(
                id=i["id"], other=other_name, amount=birr(i["amount"]), status=status
            ))
            if i["status"] == "confirmed":
                confirmed_ious.append(i)

    if ious["as_borrower"]:
        lines.append("")
        lines.append(t.IOU_LIST_AS_BORROWER)
        for i in ious["as_borrower"]:
            other = get_user_by_id(i["lender_id"])
            other_name = get_name_from_record(other) if other else str(i["lender_id"])
            status = t.STATUS_MAP.get(i["status"], i["status"])
            lines.append(t.IOU_LIST_ITEM.format(
                id=i["id"], other=other_name, amount=birr(i["amount"]), status=status
            ))
            if i["status"] == "confirmed":
                confirmed_ious.append(i)

    # Build buttons: pay button per confirmed IOU + nav
    buttons = []
    for iou in confirmed_ious[:5]:
        other_id = iou["borrower_id"] if iou["lender_id"] == user.id else iou["lender_id"]
        other = get_user_by_id(other_id)
        other_name = get_name_from_record(other) if other else str(other_id)
        buttons.append([InlineKeyboardButton(
            f"💸 #{iou['id']} | {other_name} | {birr(iou['amount'])}",
            callback_data=f"kefel_pick_{iou['id']}"
        )])

    buttons.append([
        InlineKeyboardButton(t.BTN_I_LENT, callback_data="iou_dir_lent"),
        InlineKeyboardButton(t.BTN_GO_HOME, callback_data="go_home"),
    ])

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("\n".join(lines), reply_markup=keyboard)


async def edawoch_inline(query, user, context) -> None:
    """Show IOU list inline (called from go_edawoch callback)."""
    t = s(user.id)
    ious = await run_sync(get_active_ious_for_user, user.id)

    if not ious["as_lender"] and not ious["as_borrower"]:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(t.BTN_I_LENT, callback_data="iou_dir_lent"),
            InlineKeyboardButton(t.BTN_GO_HOME, callback_data="go_home"),
        ]])
        await query.edit_message_text(t.IOU_LIST_EMPTY, reply_markup=keyboard)
        return

    user_record = get_user_by_id(user.id)
    name = get_name_from_record(user_record) if user_record else str(user.id)
    lines = [t.IOU_LIST_HEADER.format(name=name)]
    confirmed_ious = []

    if ious["as_lender"]:
        lines.append(t.IOU_LIST_AS_LENDER)
        for i in ious["as_lender"]:
            other = get_user_by_id(i["borrower_id"])
            other_name = get_name_from_record(other) if other else str(i["borrower_id"])
            status = t.STATUS_MAP.get(i["status"], i["status"])
            lines.append(t.IOU_LIST_ITEM.format(
                id=i["id"], other=other_name, amount=birr(i["amount"]), status=status
            ))
            if i["status"] == "confirmed":
                confirmed_ious.append(i)

    if ious["as_borrower"]:
        lines.append("")
        lines.append(t.IOU_LIST_AS_BORROWER)
        for i in ious["as_borrower"]:
            other = get_user_by_id(i["lender_id"])
            other_name = get_name_from_record(other) if other else str(i["lender_id"])
            status = t.STATUS_MAP.get(i["status"], i["status"])
            lines.append(t.IOU_LIST_ITEM.format(
                id=i["id"], other=other_name, amount=birr(i["amount"]), status=status
            ))
            if i["status"] == "confirmed":
                confirmed_ious.append(i)

    buttons = []
    for iou in confirmed_ious[:5]:
        other_id = iou["borrower_id"] if iou["lender_id"] == user.id else iou["lender_id"]
        other = get_user_by_id(other_id)
        other_name = get_name_from_record(other) if other else str(other_id)
        buttons.append([InlineKeyboardButton(
            f"💸 #{iou['id']} | {other_name} | {birr(iou['amount'])}",
            callback_data=f"kefel_pick_{iou['id']}"
        )])

    buttons.append([
        InlineKeyboardButton(t.BTN_I_LENT, callback_data="iou_dir_lent"),
        InlineKeyboardButton(t.BTN_GO_HOME, callback_data="go_home"),
    ])

    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("\n".join(lines), reply_markup=keyboard)


async def kefel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /kefel [ID] (mark IOU as paid) command.
    If no ID given, show active IOUs as inline buttons."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    if not context.args:
        # Button flow: show pickable IOUs
        ious = await run_sync(get_active_ious_for_user, user.id)
        confirmed = [
            i for i in (ious["as_lender"] + ious["as_borrower"])
            if i["status"] == "confirmed"
        ]

        if not confirmed:
            keyboard = InlineKeyboardMarkup([_nav_buttons(t)])
            await update.message.reply_text(t.KEFEL_NO_IOUS, reply_markup=keyboard)
            return

        buttons = []
        for iou in confirmed[:10]:
            other_id = iou["borrower_id"] if iou["lender_id"] == user.id else iou["lender_id"]
            other = get_user_by_id(other_id)
            other_name = get_name_from_record(other) if other else str(other_id)
            buttons.append([InlineKeyboardButton(
                f"#{iou['id']} | {other_name} | {birr(iou['amount'])}",
                callback_data=f"kefel_pick_{iou['id']}"
            )])

        buttons.append(_nav_buttons(t))
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(t.KEFEL_PICK, reply_markup=keyboard)
        return

    try:
        iou_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(t.ERR_USAGE_PAYBACK)
        return

    await _kefel_send_request(update, context, user, iou_id)


async def kefel_inline(query, user, context) -> None:
    """Show kefel picker inline (called from go_kefel callback)."""
    t = s(user.id)
    ious = await run_sync(get_active_ious_for_user, user.id)
    confirmed = [
        i for i in (ious["as_lender"] + ious["as_borrower"])
        if i["status"] == "confirmed"
    ]

    if not confirmed:
        keyboard = InlineKeyboardMarkup([_nav_buttons(t)])
        await query.edit_message_text(t.KEFEL_NO_IOUS, reply_markup=keyboard)
        return

    buttons = []
    for iou in confirmed[:10]:
        other_id = iou["borrower_id"] if iou["lender_id"] == user.id else iou["lender_id"]
        other = get_user_by_id(other_id)
        other_name = get_name_from_record(other) if other else str(other_id)
        buttons.append([InlineKeyboardButton(
            f"#{iou['id']} | {other_name} | {birr(iou['amount'])}",
            callback_data=f"kefel_pick_{iou['id']}"
        )])

    buttons.append(_nav_buttons(t))
    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(t.KEFEL_PICK, reply_markup=keyboard)


async def _kefel_send_request(update, context, user, iou_id):
    """Shared logic for sending a payment request (used by command and button)."""
    t = s(user.id)

    iou = await run_sync(get_iou, iou_id)
    if not iou:
        await update.message.reply_text(t.ERR_NOT_FOUND)
        return

    if user.id not in (iou["lender_id"], iou["borrower_id"]):
        await update.message.reply_text(t.ERR_NOT_YOURS)
        return

    other_id = iou["lender_id"] if user.id == iou["borrower_id"] else iou["borrower_id"]
    other = await run_sync(get_user_by_id, other_id)
    other_name = get_name_from_record(other) if other else str(other_id)

    ot = s(other_id)
    text = ot.IOU_PAY_REQUEST.format(
        name=get_name(user), id=iou_id, amount=birr(iou["amount"]),
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(ot.BTN_CONFIRM_PAY, callback_data=f"iou_paid_{iou_id}"),
            InlineKeyboardButton(ot.BTN_NOT_PAID, callback_data=f"iou_notpaid_{iou_id}"),
        ]
    ])

    try:
        await context.bot.send_message(chat_id=other_id, text=text, reply_markup=keyboard)
        nav_kb = InlineKeyboardMarkup([_nav_buttons(t)])
        await update.message.reply_text(t.IOU_PAY_SENT.format(name=other_name), reply_markup=nav_kb)
    except Forbidden:
        await update.message.reply_text(
            t.ERR_DM_FAILED.format(username=other.get("username", "?") if other else "?")
        )
