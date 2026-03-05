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


async def send_home(update_or_query, user_id: int, context=None) -> None:
    """Send the home screen with action-oriented buttons.

    Works with both Update objects (from commands) and CallbackQuery objects.
    """
    t = s(user_id)
    mini_app_url = os.getenv("MINI_APP_URL")

    buttons = [
        # Primary actions — direction IS the entry point (skips direction step)
        [
            InlineKeyboardButton(t.BTN_I_LENT, callback_data="iou_dir_lent"),
            InlineKeyboardButton(t.BTN_I_BORROWED, callback_data="iou_dir_borrowed"),
        ],
        # Quick access
        [
            InlineKeyboardButton(t.BTN_MY_IOUS, callback_data="go_edawoch"),
            InlineKeyboardButton(t.BTN_PAY_IOU, callback_data="go_kefel"),
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
    elif context:
        # Fallback: send as new message via bot
        await context.bot.send_message(
            chat_id=user_id, text=t.WELCOME_MESSAGE, reply_markup=keyboard,
        )


# Keep old name as alias for backward compatibility
_send_welcome = send_home


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
