"""
Wase (ዋሴ) — Ethiopian Social Trust Platform
Telegram Bot Entry Point

Usage:
  python -m bot.main
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.handlers.start import start_handler, help_handler, language_handler
from bot.handlers.iou import (
    eda_handler, edawoch_handler, kefel_handler,
    conv_direction, conv_direction_cb, conv_who,
    conv_amount, conv_amount_cb,
    conv_reason, conv_reason_cb,
    conv_deadline, conv_deadline_cb,
    conv_cancel, conv_cancel_silent, _cleanup_conv,
    DIRECTION, WHO, AMOUNT, REASON, DEADLINE,
)
from bot.handlers.collection import (
    sebseb_handler, mewachoch_handler,
    col_conv_title, col_conv_amount, col_conv_cancel,
    COL_TITLE, COL_AMOUNT,
)
from bot.handlers.dashboard import dashboard_handler, netib_handler
from bot.handlers.admin import admin_handler
from bot.handlers.callbacks import callback_router
from bot.services.reminders import reminder_job

# ── Config ─────────────────────────────────────────────────────

# Load .env from project root
_env_paths = [
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]
for _p in _env_paths:
    if _p.exists():
        load_dotenv(_p)
        break

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN must be set in .env")

# Logging
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("wase")


# ── Passthrough fallback factory ──────────────────────────────
# When a user types another command mid-/eda flow, silently end
# the conversation AND execute the intended command.

def _make_passthrough(actual_handler):
    """Create a fallback handler that silently cancels /eda and runs the real handler."""
    async def _passthrough(update, context):
        _cleanup_conv(context)
        await actual_handler(update, context)
        return ConversationHandler.END
    return _passthrough


# ── Bot Commands Menu ──────────────────────────────────────────

COMMANDS = [
    BotCommand("start", "ዋሴ, እስቲ መላ በለኝ"),
    BotCommand("eda", "አዲስ እዳ መዝግብልኝ"),
    BotCommand("edawoch", "የእዳ ዝርዝር"),
    BotCommand("kefel", "እዳዬን ከፍያለሁ"),
    BotCommand("sebseb", "ማሰባሰብ ጀምር (ቡድን)"),
    BotCommand("mewachoch", "ንቁ ሜዋቾች (ቡድን)"),
    BotCommand("dashboard", "ዳሽቦርድ"),
    BotCommand("netib", "የአስተማማኝነት ነጥብ"),
    BotCommand("language", "Change language / ቋንቋ ቀይር"),
    BotCommand("erdata", "ትዕዛዞች ዝርዝር"),
]


async def post_init(application) -> None:
    """Set bot commands menu after startup."""
    await application.bot.set_my_commands(COMMANDS)
    logger.info("Bot commands menu set successfully.")


# ── Main ───────────────────────────────────────────────────────

def main():
    """Build and run the bot."""
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ── Command Handlers (Amharic primary + English alias) ──

    # /start
    app.add_handler(CommandHandler("start", start_handler))

    # /eda, /iou — Conversational flow (direction → who → amount → reason → deadline)
    # Entry points: /eda command OR home screen direction buttons (iou_dir_*)
    # Each state has both CallbackQueryHandler (inline buttons) and MessageHandler (text fallback)
    eda_conv = ConversationHandler(
        entry_points=[
            CommandHandler(["eda", "iou"], eda_handler),
            CallbackQueryHandler(conv_direction_cb, pattern="^iou_dir_"),
        ],
        states={
            DIRECTION: [
                CallbackQueryHandler(conv_direction_cb, pattern="^iou_dir_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, conv_direction),
            ],
            WHO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, conv_who),
            ],
            AMOUNT: [
                CallbackQueryHandler(conv_amount_cb, pattern="^iou_amt_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, conv_amount),
            ],
            REASON: [
                CallbackQueryHandler(conv_reason_cb, pattern="^iou_reason_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, conv_reason),
            ],
            DEADLINE: [
                CallbackQueryHandler(conv_deadline_cb, pattern="^iou_dl_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, conv_deadline),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", conv_cancel),                              # Explicit cancel — shows message
            CommandHandler(["eda", "iou"], eda_handler),                        # Restart mid-flow
            CommandHandler("start", _make_passthrough(start_handler)),
            CommandHandler("dashboard", _make_passthrough(dashboard_handler)),
            CommandHandler(["netib", "score"], _make_passthrough(netib_handler)),
            CommandHandler(["edawoch", "myious"], _make_passthrough(edawoch_handler)),
            CommandHandler(["kefel", "payback"], _make_passthrough(kefel_handler)),
            CommandHandler(["erdata", "help"], _make_passthrough(help_handler)),
            CommandHandler("language", _make_passthrough(language_handler)),
            CommandHandler(["sebseb", "collect"], conv_cancel_silent),
            CommandHandler(["mewachoch", "collections"], conv_cancel_silent),
        ],
        per_message=False,
        conversation_timeout=300,  # 5 min timeout — auto-cancel abandoned flows
    )
    app.add_handler(eda_conv)

    # /sebseb, /collect — Collection (with guided flow ConversationHandler)
    # Uses ForceReply so the bot receives replies even in groups with privacy mode.
    _col_text_filter = filters.TEXT & ~filters.COMMAND
    sebseb_conv = ConversationHandler(
        entry_points=[CommandHandler(["sebseb", "collect"], sebseb_handler)],
        states={
            COL_TITLE: [MessageHandler(_col_text_filter, col_conv_title)],
            COL_AMOUNT: [MessageHandler(_col_text_filter, col_conv_amount)],
        },
        fallbacks=[
            CommandHandler("cancel", col_conv_cancel),
            CommandHandler(["sebseb", "collect"], sebseb_handler),  # Restart
            CommandHandler("start", col_conv_cancel),
            CommandHandler("dashboard", col_conv_cancel),
            CommandHandler(["eda", "iou"], col_conv_cancel),
            CommandHandler(["edawoch", "myious"], col_conv_cancel),
            CommandHandler(["kefel", "payback"], col_conv_cancel),
        ],
        per_chat=True,
        per_user=True,
        conversation_timeout=120,  # 2 min timeout for group flow
    )
    app.add_handler(sebseb_conv)

    # /edawoch, /myious
    app.add_handler(CommandHandler(["edawoch", "myious"], edawoch_handler))

    # /kefel, /payback
    app.add_handler(CommandHandler(["kefel", "payback"], kefel_handler))

    # /mewachoch, /collections
    app.add_handler(CommandHandler(["mewachoch", "collections"], mewachoch_handler))

    # /dashboard
    app.add_handler(CommandHandler("dashboard", dashboard_handler))

    # /netib, /score
    app.add_handler(CommandHandler(["netib", "score"], netib_handler))

    # /language
    app.add_handler(CommandHandler("language", language_handler))

    # /erdata, /help
    app.add_handler(CommandHandler(["erdata", "help"], help_handler))

    # /admin (restricted)
    app.add_handler(CommandHandler("admin", admin_handler))

    # ── Callback Query Handler (all inline buttons NOT handled by ConversationHandler) ──
    app.add_handler(CallbackQueryHandler(callback_router))

    # ── Reminder Job (every 6 hours) ──
    job_queue = app.job_queue
    job_queue.run_repeating(
        reminder_job,
        interval=6 * 60 * 60,  # 6 hours in seconds
        first=60,              # First run 60 seconds after startup
        name="reminder_job",
    )

    # ── Start Polling ──
    logger.info("Wase bot starting... (polling mode)")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
