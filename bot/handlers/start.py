"""
Handlers for /start, /erdata (help), and /language.
"""

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

from bot.db.models import upsert_user
from bot.strings.lang import s, get_lang, set_lang


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — show language picker, then welcome after selection."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    # Always show language picker + welcome
    # Language picker on top, then welcome in current language below
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ])

    t = s(user.id)
    text = "🌍 ቋንቋ ይምረጡ / Choose your language:\n\n" + t.WELCOME_MESSAGE

    await update.message.reply_text(text, reply_markup=keyboard)


async def _send_welcome(update_or_query, user_id: int) -> None:
    """Send the welcome message in the user's language."""
    t = s(user_id)
    mini_app_url = os.getenv("MINI_APP_URL")

    buttons = [
        [
            InlineKeyboardButton(t.BTN_NEW_IOU, callback_data="menu_new_iou"),
            InlineKeyboardButton(t.BTN_NEW_COLLECT, callback_data="menu_new_collect"),
        ],
        [
            InlineKeyboardButton(t.BTN_DASHBOARD, callback_data="menu_dashboard"),
            InlineKeyboardButton(t.BTN_SCORE, callback_data="menu_score"),
        ],
    ]

    if mini_app_url:
        buttons.append([
            InlineKeyboardButton(
                t.BTN_OPEN_APP,
                web_app=WebAppInfo(url=mini_app_url),
            )
        ])

    keyboard = InlineKeyboardMarkup(buttons)

    # Handle both Update and CallbackQuery
    if hasattr(update_or_query, 'message') and update_or_query.message:
        await update_or_query.message.reply_text(t.WELCOME_MESSAGE, reply_markup=keyboard)
    elif hasattr(update_or_query, 'edit_message_text'):
        await update_or_query.edit_message_text(t.WELCOME_MESSAGE, reply_markup=keyboard)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /erdata and /help — list all commands."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    await update.message.reply_text(t.HELP_TITLE + t.HELP_COMMANDS)


async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /language — show language selection buttons."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ])

    await update.message.reply_text(
        "🌍 ቋንቋ ይምረጡ / Choose your language:",
        reply_markup=keyboard,
    )
