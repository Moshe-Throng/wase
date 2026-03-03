"""
Handlers for IOU commands:
  /eda                — Start IOU flow: direction → who → amount → reason → deadline
  /edawoch            — List active IOUs
  /kefel [ID]         — Mark IOU as paid
"""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from telegram.error import Forbidden

from bot.strings.lang import s
from bot.db.models import (
    upsert_user, get_user_by_username, create_iou, get_iou,
    get_active_ious_for_user, get_user_by_id,
)
from bot.db.supabase_client import run_sync
from bot.utils.formatting import (
    birr, get_name, get_name_from_record, parse_iou_command, format_date,
    parse_amount,
)

# Conversation states
DIRECTION, WHO, AMOUNT, REASON, DEADLINE = range(5)


async def _create_and_notify(update, context, lender_id, lender_name, borrower, amount, description, due_date):
    """Shared: create IOU record, notify both parties."""
    t = s(lender_id)

    iou = await run_sync(
        create_iou,
        lender_id=lender_id,
        borrower_id=borrower["user_id"],
        amount=amount,
        description=description,
        due_date=due_date,
    )

    borrower_name = get_name_from_record(borrower)
    lines = [
        t.IOU_NEW.format(id=iou["id"]),
        t.IOU_LENT.format(lender=lender_name, borrower=borrower_name),
        t.IOU_AMOUNT.format(amount=birr(amount)),
    ]
    if description:
        lines.append(t.IOU_REASON.format(desc=description))
    if due_date:
        lines.append(t.IOU_DUE.format(date=format_date(due_date)))
    lines.append("")
    lines.append(t.IOU_WAITING.format(name=borrower_name))

    await update.message.reply_text("\n".join(lines), reply_markup=ReplyKeyboardRemove())

    # DM the OTHER party (whoever didn't initiate) for confirmation
    initiator_id = update.effective_user.id
    other_id = borrower["user_id"] if initiator_id == lender_id else lender_id
    ot = s(other_id)

    if initiator_id == lender_id:
        # Lender initiated → borrower confirms
        confirm_text = ot.IOU_CONFIRM_REQUEST.format(
            lender=lender_name, amount=birr(amount), desc=description or "-",
        )
    else:
        # Borrower initiated → lender confirms
        confirm_text = ot.IOU_CONFIRM_LENDER_REQUEST.format(
            borrower=borrower_name, amount=birr(amount), desc=description or "-",
        )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(ot.BTN_CONFIRM, callback_data=f"iou_confirm_{iou['id']}"),
            InlineKeyboardButton(ot.BTN_DISPUTE, callback_data=f"iou_dispute_{iou['id']}"),
        ]
    ])

    try:
        await context.bot.send_message(
            chat_id=other_id, text=confirm_text, reply_markup=keyboard,
        )
    except Forbidden:
        bot_me = await context.bot.get_me()
        other_username = borrower.get("username", "?") if other_id == borrower["user_id"] else "?"
        await update.message.reply_text(
            t.ERR_DM_FAILED.format(username=other_username)
            + "\n\n" + t.INVITE_MESSAGE.format(bot_username=bot_me.username)
        )


# ── Conversational flow ──────────────────────────────────────

async def eda_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /eda — ask direction first: I lent or I borrowed."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    keyboard = ReplyKeyboardMarkup(
        [[t.BTN_I_LENT, t.BTN_I_BORROWED]],
        one_time_keyboard=True, resize_keyboard=True,
    )
    await update.message.reply_text(t.CONV_DIRECTION, reply_markup=keyboard)
    return DIRECTION


async def conv_direction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 1: User chooses 'I lent' or 'I borrowed'."""
    user = update.effective_user
    t = s(user.id)
    text = update.message.text.strip()

    if text == t.BTN_I_LENT or text.lower() in ("i lent", "lent"):
        context.user_data["iou_direction"] = "lent"
        await update.message.reply_text(t.CONV_WHO_BORROWED, reply_markup=ReplyKeyboardRemove())
    elif text == t.BTN_I_BORROWED or text.lower() in ("i borrowed", "borrowed"):
        context.user_data["iou_direction"] = "borrowed"
        await update.message.reply_text(t.CONV_WHO_LENT, reply_markup=ReplyKeyboardRemove())
    else:
        keyboard = ReplyKeyboardMarkup(
            [[t.BTN_I_LENT, t.BTN_I_BORROWED]],
            one_time_keyboard=True, resize_keyboard=True,
        )
        await update.message.reply_text(t.CONV_DIRECTION, reply_markup=keyboard)
        return DIRECTION

    return WHO


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
        bot_me = await context.bot.get_me()
        await update.message.reply_text(
            t.ERR_USER_NOT_STARTED.format(username=username)
            + "\n\n" + t.INVITE_MESSAGE.format(bot_username=bot_me.username)
        )
        return ConversationHandler.END

    context.user_data["iou_other"] = other_user
    context.user_data["iou_other_name"] = get_name_from_record(other_user)

    await update.message.reply_text(
        t.CONV_AMOUNT.format(name=context.user_data["iou_other_name"])
    )
    return AMOUNT


async def conv_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 3: User sends amount in Birr."""
    user = update.effective_user
    t = s(user.id)

    amount = parse_amount(update.message.text.strip())
    if amount is None:
        await update.message.reply_text(t.ERR_INVALID_AMOUNT + "\n" + t.CONV_AMOUNT_RETRY)
        return AMOUNT

    context.user_data["iou_amount"] = amount

    keyboard = ReplyKeyboardMarkup(
        [[t.BTN_SKIP]], one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(t.CONV_REASON, reply_markup=keyboard)
    return REASON


async def conv_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 4: User sends reason or skips."""
    user = update.effective_user
    t = s(user.id)
    text = update.message.text.strip()

    if text == t.BTN_SKIP or text.lower() == "skip":
        context.user_data["iou_reason"] = None
    else:
        context.user_data["iou_reason"] = text[:200]

    # Deadline quick-pick buttons
    keyboard = ReplyKeyboardMarkup(
        [[t.BTN_1_WEEK, t.BTN_2_WEEKS, t.BTN_1_MONTH], [t.BTN_NO_DEADLINE]],
        one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(t.CONV_DEADLINE, reply_markup=keyboard)
    return DEADLINE


async def conv_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 5: User picks deadline button or types date. Then create the IOU."""
    user = update.effective_user
    t = s(user.id)
    text = update.message.text.strip()
    from datetime import timedelta, date as date_type

    due_date = None

    # Quick-pick buttons
    if text == t.BTN_NO_DEADLINE or text.lower() in ("no deadline", "skip"):
        due_date = None
    elif text == t.BTN_1_WEEK or text.lower() == "1 week":
        due_date = date_type.today() + timedelta(weeks=1)
    elif text == t.BTN_2_WEEKS or text.lower() == "2 weeks":
        due_date = date_type.today() + timedelta(weeks=2)
    elif text == t.BTN_1_MONTH or text.lower() == "1 month":
        due_date = date_type.today() + timedelta(days=30)
    else:
        # Try parsing typed date
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
            try:
                due_date = datetime.strptime(text, fmt).date()
                break
            except ValueError:
                continue

        if due_date is None:
            await update.message.reply_text(t.CONV_DEADLINE_RETRY)
            return DEADLINE

    # Determine lender/borrower based on direction
    other = context.user_data["iou_other"]
    amount = context.user_data["iou_amount"]
    reason = context.user_data.get("iou_reason")
    direction = context.user_data.get("iou_direction", "lent")

    if direction == "lent":
        lender_id = user.id
        lender_name = get_name(user)
        borrower = other
    else:
        lender_id = other["user_id"]
        lender_name = get_name_from_record(other)
        borrower = {"user_id": user.id, "username": user.username, "first_name": user.first_name}

    await _create_and_notify(update, context, lender_id, lender_name, borrower, amount, reason, due_date)

    # Clean up
    for key in ("iou_direction", "iou_other", "iou_other_name", "iou_amount", "iou_reason"):
        context.user_data.pop(key, None)

    return ConversationHandler.END


async def conv_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversational IOU flow."""
    t = s(update.effective_user.id)
    await update.message.reply_text(t.CONV_CANCELLED, reply_markup=ReplyKeyboardRemove())
    for key in ("iou_direction", "iou_other", "iou_other_name", "iou_amount", "iou_reason"):
        context.user_data.pop(key, None)
    return ConversationHandler.END


# ── Non-conversational commands ───────────────────────────────

async def edawoch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /edawoch (list IOUs) command."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    ious = await run_sync(get_active_ious_for_user, user.id)

    if not ious["as_lender"] and not ious["as_borrower"]:
        await update.message.reply_text(t.IOU_LIST_EMPTY)
        return

    lines = [t.IOU_LIST_HEADER.format(name=get_name(user))]

    if ious["as_lender"]:
        lines.append(t.IOU_LIST_AS_LENDER)
        for i in ious["as_lender"]:
            other = get_user_by_id(i["borrower_id"])
            other_name = get_name_from_record(other) if other else str(i["borrower_id"])
            status = t.STATUS_MAP.get(i["status"], i["status"])
            lines.append(t.IOU_LIST_ITEM.format(
                id=i["id"], other=other_name, amount=birr(i["amount"]), status=status
            ))

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

    await update.message.reply_text("\n".join(lines))


async def kefel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /kefel [ID] (mark IOU as paid) command."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    if not context.args:
        await update.message.reply_text(t.ERR_USAGE_PAYBACK)
        return

    try:
        iou_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(t.ERR_USAGE_PAYBACK)
        return

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
        await update.message.reply_text(t.IOU_PAY_SENT.format(name=other_name))
    except Forbidden:
        await update.message.reply_text(
            t.ERR_DM_FAILED.format(username=other.get("username", "?") if other else "?")
        )
