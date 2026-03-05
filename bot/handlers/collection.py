"""
Handlers for collection commands:
  /sebseb title - amount each/total  — Start new collection (group only)
  /sebseb                            — Guided flow: title → amount (group only)
  /mewachoch                         — List active collections in group
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ContextTypes, ConversationHandler

from bot.strings.lang import s
from bot.db.models import (
    upsert_user, create_collection, get_active_collections_in_chat,
)
from bot.utils.formatting import birr, get_name, parse_collection_command, parse_amount

# Conversation states for guided flow
COL_TITLE, COL_AMOUNT = range(100, 102)  # Offset to avoid collision with IOU states

# Context keys used by the collection conversation
_COL_CONTEXT_KEYS = ("col_title",)


def _cleanup_col_conv(context):
    """Remove all /sebseb conversation keys from user_data."""
    for key in _COL_CONTEXT_KEYS:
        context.user_data.pop(key, None)


def _build_collection_card(t, collection, parsed_title, amount_per_person, target_amount, creator_name):
    """Build the collection announcement message and keyboard."""
    lines = [
        t.COL_NEW.format(id=collection["id"]),
        t.COL_TITLE.format(title=parsed_title),
    ]

    if amount_per_person:
        lines.append(t.COL_AMOUNT_EACH.format(amount=birr(amount_per_person)))
    elif target_amount:
        lines.append(t.COL_TARGET.format(amount=birr(target_amount)))

    lines.append(t.COL_STARTED_BY.format(name=creator_name))

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t.BTN_PAID, callback_data=f"col_paid_{collection['id']}"),
            InlineKeyboardButton(t.BTN_STATUS, callback_data=f"col_status_{collection['id']}"),
        ]
    ])

    return "\n".join(lines), keyboard


async def sebseb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /sebseb (create collection) command. Group only.
    With args: create directly. Without args: start guided flow."""
    user = update.effective_user
    chat = update.effective_chat
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    # Must be in a group
    if chat.type == "private":
        bot_me = await context.bot.get_me()
        await update.message.reply_text(t.ERR_GROUP_ONLY.format(bot_username=bot_me.username))
        return ConversationHandler.END

    # Parse command arguments
    args_text = " ".join(context.args) if context.args else ""

    if args_text:
        # Direct creation with args
        parsed = parse_collection_command(args_text)

        if not parsed:
            await update.message.reply_text(t.ERR_USAGE_COLLECT)
            return ConversationHandler.END

        collection = create_collection(
            creator_id=user.id,
            chat_id=chat.id,
            title=parsed["title"],
            amount_per_person=parsed["amount_per_person"],
            target_amount=parsed["target_amount"],
        )

        text, keyboard = _build_collection_card(
            t, collection, parsed["title"],
            parsed["amount_per_person"], parsed["target_amount"],
            get_name(user),
        )
        await update.message.reply_text(text, reply_markup=keyboard)
        return ConversationHandler.END

    # No args — start guided flow
    # ForceReply ensures the user REPLIES to this message, which the bot
    # can always see in groups (even with privacy mode on).
    await update.message.reply_text(
        t.COL_ASK_TITLE,
        reply_markup=ForceReply(selective=True, input_field_placeholder=t.COL_TITLE_PLACEHOLDER),
    )
    return COL_TITLE


async def col_conv_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guided step 1: User replies with collection title."""
    user = update.effective_user
    t = s(user.id)
    title = update.message.text.strip()[:200]

    if not title:
        await update.message.reply_text(
            t.COL_ASK_TITLE,
            reply_markup=ForceReply(selective=True, input_field_placeholder=t.COL_TITLE_PLACEHOLDER),
        )
        return COL_TITLE

    context.user_data["col_title"] = title
    await update.message.reply_text(
        t.COL_ASK_AMOUNT,
        reply_markup=ForceReply(selective=True, input_field_placeholder=t.COL_AMOUNT_PLACEHOLDER),
    )
    return COL_AMOUNT


async def col_conv_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guided step 2: User replies with amount per person. Creates the collection."""
    user = update.effective_user
    chat = update.effective_chat
    t = s(user.id)

    amount = parse_amount(update.message.text.strip())
    if amount is None:
        await update.message.reply_text(
            t.ERR_INVALID_AMOUNT + "\n" + t.COL_ASK_AMOUNT,
            reply_markup=ForceReply(selective=True, input_field_placeholder=t.COL_AMOUNT_PLACEHOLDER),
        )
        return COL_AMOUNT

    title = context.user_data.pop("col_title", "Collection")

    collection = create_collection(
        creator_id=user.id,
        chat_id=chat.id,
        title=title,
        amount_per_person=amount,
    )

    text, keyboard = _build_collection_card(
        t, collection, title, amount, None, get_name(user),
    )
    await update.message.reply_text(text, reply_markup=keyboard)
    _cleanup_col_conv(context)
    return ConversationHandler.END


async def col_conv_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Silent cancel for the collection guided flow."""
    _cleanup_col_conv(context)
    return ConversationHandler.END


async def mewachoch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mewachoch (list collections) command. Group only."""
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
    keyboard = None
    for col in collections:
        from bot.db.models import get_contributions_for_collection
        contribs = get_contributions_for_collection(col["id"])
        paid_count = sum(1 for c in contribs if c["status"] == "paid")

        lines.append(t.COL_LIST_ITEM.format(
            id=col["id"],
            title=col["title"],
            count=paid_count,
        ))

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(t.BTN_PAID, callback_data=f"col_paid_{col['id']}"),
                InlineKeyboardButton(t.BTN_STATUS, callback_data=f"col_status_{col['id']}"),
            ]
        ])

    await update.message.reply_text("\n".join(lines), reply_markup=keyboard)
