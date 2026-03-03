"""
Handlers for collection commands:
  /sebeseb title - amount each/total  — Start new collection (group only)
  /mesebeboch                         — List active collections in group
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.strings.lang import s
from bot.db.models import (
    upsert_user, create_collection, get_active_collections_in_chat,
)
from bot.utils.formatting import birr, get_name, parse_collection_command


async def sebeseb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /sebeseb (create collection) command. Group only."""
    user = update.effective_user
    chat = update.effective_chat
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    # Must be in a group
    if chat.type == "private":
        bot_me = await context.bot.get_me()
        await update.message.reply_text(t.ERR_GROUP_ONLY.format(bot_username=bot_me.username))
        return

    # Parse command arguments
    args_text = " ".join(context.args) if context.args else ""
    parsed = parse_collection_command(args_text)

    if not parsed:
        await update.message.reply_text(t.ERR_USAGE_COLLECT)
        return

    # Create collection
    collection = create_collection(
        creator_id=user.id,
        chat_id=chat.id,
        title=parsed["title"],
        amount_per_person=parsed["amount_per_person"],
        target_amount=parsed["target_amount"],
    )

    # Build collection card
    lines = [
        t.COL_NEW.format(id=collection["id"]),
        t.COL_TITLE.format(title=parsed["title"]),
    ]

    if parsed["amount_per_person"]:
        lines.append(t.COL_AMOUNT_EACH.format(amount=birr(parsed["amount_per_person"])))
    elif parsed["target_amount"]:
        lines.append(t.COL_TARGET.format(amount=birr(parsed["target_amount"])))

    lines.append(t.COL_STARTED_BY.format(name=get_name(user)))

    # Inline keyboard: I Paid + Status
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t.BTN_PAID, callback_data=f"col_paid_{collection['id']}"),
            InlineKeyboardButton(t.BTN_STATUS, callback_data=f"col_status_{collection['id']}"),
        ]
    ])

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=keyboard,
    )


async def mesebeboch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mesebeboch (list collections) command. Group only."""
    user = update.effective_user
    chat = update.effective_chat
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    if chat.type == "private":
        bot_me = await context.bot.get_me()
        await update.message.reply_text(t.ERR_GROUP_ONLY.format(bot_username=bot_me.username))
        return

    collections = get_active_collections_in_chat(chat.id)

    if not collections:
        await update.message.reply_text(t.COL_LIST_EMPTY)
        return

    lines = [t.COL_LIST_HEADER]
    for col in collections:
        # Count paid contributions
        from bot.db.models import get_contributions_for_collection
        contribs = get_contributions_for_collection(col["id"])
        paid_count = sum(1 for c in contribs if c["status"] == "paid")

        lines.append(t.COL_LIST_ITEM.format(
            id=col["id"],
            title=col["title"],
            count=paid_count,
        ))

        # Add I Paid button for convenience
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(t.BTN_PAID, callback_data=f"col_paid_{col['id']}"),
                InlineKeyboardButton(t.BTN_STATUS, callback_data=f"col_status_{col['id']}"),
            ]
        ])

    await update.message.reply_text("\n".join(lines), reply_markup=keyboard)
