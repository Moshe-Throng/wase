"""
Central callback query handler for all inline keyboard interactions.

Callback data patterns:
  iou_confirm_{id}   — Either party confirms IOU
  iou_dispute_{id}   — Either party disputes IOU
  iou_paid_{id}      — Other party confirms payment
  iou_notpaid_{id}   — Other party denies payment
  col_paid_{id}      — User marks contribution as paid
  col_status_{id}    — View collection status
  lang_am / lang_en  — Language selection
  menu_new_iou       — Start IOU flow from menu
  menu_dashboard     — Show dashboard inline
  menu_score         — Show trust score inline
  menu_new_collect   — Show group instructions
"""

from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from bot.strings.lang import s, set_lang
from bot.db.models import (
    upsert_user, get_iou, confirm_iou, dispute_iou, complete_iou,
    get_user_by_id, get_collection, record_contribution,
    get_contributions_for_collection, has_user_contributed,
    record_trust_event, has_overdue_event,
    get_user_financial_summary,
)
from bot.db.supabase_client import run_sync
from bot.services.trust_score import calculate_trust_score
from bot.utils.formatting import birr, get_name_from_record, progress_bar


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route all callback queries to the appropriate handler."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    # Language callbacks — handle BEFORE answering (need to update cache first)
    if data in ("lang_am", "lang_en"):
        lang = "am" if data == "lang_am" else "en"
        set_lang(user.id, lang)
        await query.answer()
        # Re-read strings AFTER language change
        t = s(user.id)
        from bot.handlers.start import _send_welcome
        await _send_welcome(query, user.id)
        return

    await query.answer()
    t = s(user.id)

    # IOU callbacks
    if data.startswith("iou_confirm_"):
        await _handle_iou_confirm(query, user, int(data.split("_")[-1]), context)
    elif data.startswith("iou_dispute_"):
        await _handle_iou_dispute(query, user, int(data.split("_")[-1]), context)
    elif data.startswith("iou_paid_"):
        await _handle_iou_paid(query, user, int(data.split("_")[-1]), context)
    elif data.startswith("iou_notpaid_"):
        await _handle_iou_notpaid(query, user, int(data.split("_")[-1]), context)
    # Collection callbacks
    elif data.startswith("col_paid_"):
        await _handle_col_paid(query, user, int(data.split("_")[-1]), context)
    elif data.startswith("col_status_"):
        await _handle_col_status(query, user, int(data.split("_")[-1]), context)
    # Menu callbacks — actually execute the features
    elif data == "menu_new_iou":
        await _menu_start_iou(query, user, context)
    elif data == "menu_dashboard":
        await _menu_show_dashboard(query, user, context)
    elif data == "menu_score":
        await _menu_show_score(query, user, context)
    elif data == "menu_new_collect":
        bot_me = await context.bot.get_me()
        await query.edit_message_text(
            t.ERR_GROUP_ONLY.format(bot_username=bot_me.username)
        )


# ── Menu Actions (actually do things) ────────────────────────

async def _menu_start_iou(query, user, context):
    """Start the IOU conversational flow from the menu button."""
    t = s(user.id)
    # Send the direction question as a NEW message (not edit)
    # The ConversationHandler will pick this up via its entry point
    keyboard = ReplyKeyboardMarkup(
        [[t.BTN_I_LENT, t.BTN_I_BORROWED]],
        one_time_keyboard=True, resize_keyboard=True,
    )
    await query.edit_message_text(t.CONV_DIRECTION)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=t.CONV_DIRECTION,
        reply_markup=keyboard,
    )
    # Put user into DIRECTION state manually
    from bot.handlers.iou import DIRECTION
    context.user_data["_conv_started_from_menu"] = True


async def _menu_show_dashboard(query, user, context):
    """Show dashboard data inline from the menu button."""
    t = s(user.id)
    summary = await run_sync(get_user_financial_summary, user.id)
    score_data = await run_sync(calculate_trust_score, user.id)

    user_record = get_user_by_id(user.id)
    name = get_name_from_record(user_record) if user_record else str(user.id)

    lines = [
        t.DASH_TITLE.format(name=name),
        "",
        t.DASH_OWED_TO.format(amount=birr(summary["owed_to_user"])),
        t.DASH_YOU_OWE.format(amount=birr(summary["user_owes"])),
    ]

    net = summary["net"]
    if net > 0:
        lines.append(t.DASH_NET_POS.format(amount=birr(net)))
    elif net < 0:
        lines.append(t.DASH_NET_NEG.format(amount=birr(abs(net))))
    else:
        lines.append(t.DASH_NET_ZERO)

    lines.append("")
    if summary["overdue_count"] > 0:
        lines.append(t.DASH_OVERDUE.format(count=summary["overdue_count"]))
    lines.append(t.DASH_COMPLETED.format(count=summary["completed_count"]))
    lines.append(t.DASH_CONTRIBUTIONS.format(count=summary["contribution_count"]))
    lines.append("")
    lines.append(f"🛡 {score_data['tier']}  {progress_bar(score_data['score'], 100)}")

    await query.edit_message_text("\n".join(lines))


async def _menu_show_score(query, user, context):
    """Show trust score inline from the menu button."""
    t = s(user.id)
    result = await run_sync(calculate_trust_score, user.id)
    c = result["components"]

    user_record = get_user_by_id(user.id)
    name = get_name_from_record(user_record) if user_record else str(user.id)

    lines = [
        t.SCORE_TITLE.format(name=name),
        "",
        f"{'━' * 20}",
        f"  {result['score']}/100  {result['tier']}",
        f"{'━' * 20}",
        "",
        f"💸 {t.SCORE_REPAID.format(done=c['repaid']['done'], total=c['repaid']['total'])}",
        f"   {progress_bar(c['repaid']['score'], c['repaid']['max'])}",
        "",
        f"💰 {t.SCORE_COLLECT.format(count=c['collections']['count'])}",
        f"   {progress_bar(c['collections']['score'], c['collections']['max'])}",
        "",
        f"👥 {t.SCORE_CONNECT.format(count=c['connections']['count'])}",
        f"   {progress_bar(c['connections']['score'], c['connections']['max'])}",
        "",
        f"📋 {t.SCORE_HISTORY.format(status='✅' if c['history']['has_history'] else '—')}",
        f"   {progress_bar(c['history']['score'], c['history']['max'])}",
    ]

    if c["overdue"]["count"] > 0:
        lines.append("")
        lines.append(t.SCORE_OVERDUE_PENALTY.format(points=c["overdue"]["penalty"]))

    lines.append("")
    lines.append(t.SCORE_IMPROVE)

    await query.edit_message_text("\n".join(lines))


# ── IOU Callbacks ──────────────────────────────────────────────

async def _handle_iou_confirm(query, user, iou_id, context):
    """Either party confirms the IOU."""
    iou = get_iou(iou_id)
    t = s(user.id)
    if not iou:
        await query.edit_message_text(t.ERR_NOT_FOUND)
        return

    if user.id not in (iou["lender_id"], iou["borrower_id"]):
        await query.answer(t.ERR_NOT_YOURS, show_alert=True)
        return

    confirm_iou(iou_id)
    record_trust_event(iou["lender_id"], "iou_created", 0, iou_id)
    record_trust_event(iou["borrower_id"], "iou_created", 0, iou_id)

    await query.edit_message_text(t.IOU_CONFIRMED.format(id=iou_id))

    other_id = iou["lender_id"] if user.id == iou["borrower_id"] else iou["borrower_id"]
    ot = s(other_id)
    confirmer = get_user_by_id(user.id)
    confirmer_name = get_name_from_record(confirmer) if confirmer else str(user.id)
    try:
        await context.bot.send_message(
            chat_id=other_id,
            text=ot.IOU_CONFIRMED_NOTIFY.format(
                borrower=confirmer_name, id=iou_id, amount=birr(iou["amount"])
            ),
        )
    except Exception:
        pass


async def _handle_iou_dispute(query, user, iou_id, context):
    """Either party disputes the IOU."""
    iou = get_iou(iou_id)
    t = s(user.id)
    if not iou:
        await query.edit_message_text(t.ERR_NOT_FOUND)
        return

    if user.id not in (iou["lender_id"], iou["borrower_id"]):
        await query.answer(t.ERR_NOT_YOURS, show_alert=True)
        return

    dispute_iou(iou_id)
    await query.edit_message_text(t.IOU_DISPUTED.format(id=iou_id))

    other_id = iou["lender_id"] if user.id == iou["borrower_id"] else iou["borrower_id"]
    ot = s(other_id)
    disputer = get_user_by_id(user.id)
    disputer_name = get_name_from_record(disputer) if disputer else str(user.id)
    try:
        await context.bot.send_message(
            chat_id=other_id,
            text=ot.IOU_DISPUTE_NOTIFY.format(borrower=disputer_name, id=iou_id),
        )
    except Exception:
        pass


async def _handle_iou_paid(query, user, iou_id, context):
    """Other party confirms payment."""
    iou = get_iou(iou_id)
    t = s(user.id)
    if not iou:
        await query.edit_message_text(t.ERR_NOT_FOUND)
        return

    if user.id not in (iou["lender_id"], iou["borrower_id"]):
        await query.answer(t.ERR_NOT_YOURS, show_alert=True)
        return

    complete_iou(iou_id)
    record_trust_event(iou["borrower_id"], "iou_repaid", 5, iou_id)

    if iou.get("due_date"):
        due = iou["due_date"]
        if isinstance(due, str):
            from datetime import datetime
            due = datetime.strptime(due, "%Y-%m-%d").date()
        if date.today() <= due:
            record_trust_event(iou["borrower_id"], "iou_early", 2, iou_id)

    await query.edit_message_text(
        t.IOU_PAID.format(id=iou_id) + "\n" +
        t.IOU_PAID_DETAIL.format(amount=birr(iou["amount"])) + "\n" +
        t.IOU_TRUST_NOTE
    )

    other_id = iou["lender_id"] if user.id == iou["borrower_id"] else iou["borrower_id"]
    ot = s(other_id)
    try:
        await context.bot.send_message(
            chat_id=other_id,
            text=(
                ot.IOU_PAID.format(id=iou_id) + "\n" +
                ot.IOU_PAID_DETAIL.format(amount=birr(iou["amount"])) + "\n" +
                ot.IOU_TRUST_NOTE
            ),
        )
    except Exception:
        pass


async def _handle_iou_notpaid(query, user, iou_id, context):
    """Other party says payment was NOT received."""
    iou = get_iou(iou_id)
    t = s(user.id)
    if not iou:
        await query.edit_message_text(t.ERR_NOT_FOUND)
        return

    if user.id not in (iou["lender_id"], iou["borrower_id"]):
        await query.answer(t.ERR_NOT_YOURS, show_alert=True)
        return

    await query.edit_message_text(t.IOU_NOT_PAID.format(id=iou_id))


# ── Collection Callbacks ──────────────────────────────────────

async def _handle_col_paid(query, user, collection_id, context):
    """User marks their contribution as paid."""
    collection = get_collection(collection_id)
    t = s(user.id)
    if not collection:
        await query.answer(t.ERR_NOT_FOUND, show_alert=True)
        return

    if has_user_contributed(collection_id, user.id):
        await query.answer(t.ERR_ALREADY_PAID, show_alert=True)
        return

    amount = collection.get("amount_per_person")
    result = record_contribution(collection_id, user.id, amount)
    if result is None:
        await query.answer(t.ERR_ALREADY_PAID, show_alert=True)
        return

    record_trust_event(user.id, "collection_paid", 3, collection_id)

    contribs = get_contributions_for_collection(collection_id)
    paid_count = sum(1 for c in contribs if c["status"] == "paid")

    user_record = get_user_by_id(user.id)
    user_name = get_name_from_record(user_record) if user_record else str(user.id)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            t.COL_USER_PAID.format(name=user_name, title=collection["title"]) + "\n" +
            t.COL_COUNT.format(count=paid_count)
        ),
    )


async def _handle_col_status(query, user, collection_id, context):
    """Show collection payment status board."""
    collection = get_collection(collection_id)
    t = s(user.id)
    if not collection:
        await query.answer(t.ERR_NOT_FOUND, show_alert=True)
        return

    contribs = get_contributions_for_collection(collection_id)

    lines = [t.COL_STATUS_HEADER.format(id=collection_id, title=collection["title"])]

    total_amount = 0
    for c in contribs:
        user_record = get_user_by_id(c["user_id"])
        name = get_name_from_record(user_record) if user_record else str(c["user_id"])
        if c["status"] == "paid":
            lines.append(t.COL_STATUS_PAID.format(name=name))
            total_amount += float(c.get("amount", 0) or 0)
        else:
            lines.append(t.COL_STATUS_UNPAID.format(name=name))

    paid_count = sum(1 for c in contribs if c["status"] == "paid")
    lines.append("")
    lines.append(t.COL_PROGRESS.format(
        paid=paid_count,
        total=len(contribs) if contribs else "?",
        amount=birr(total_amount),
    ))

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t.BTN_PAID, callback_data=f"col_paid_{collection_id}")]
    ])

    await query.edit_message_text("\n".join(lines), reply_markup=keyboard)
