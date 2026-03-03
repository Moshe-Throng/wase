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
    conv_direction, conv_who, conv_amount, conv_reason, conv_deadline, conv_cancel,
    DIRECTION, WHO, AMOUNT, REASON, DEADLINE,
)
from bot.handlers.collection import sebeseb_handler, mesebeboch_handler
from bot.handlers.dashboard import dashboard_handler, netib_handler
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


# ── Bot Commands Menu ──────────────────────────────────────────

COMMANDS = [
    BotCommand("start", "ዋሴ, እስቲ መላ በለኝ"),
    BotCommand("eda", "አዲስ እዳ መዝግብልኝ"),
    BotCommand("edawoch", "የእዳ ዝርዝር"),
    BotCommand("kefel", "እዳዬን ከፍያለሁ"),
    BotCommand("sebeseb", "ማሰባሰብ ጀምር (ቡድን)"),
    BotCommand("mesebeboch", "ንቁ ማሰባሰቦች (ቡድን)"),
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
    eda_conv = ConversationHandler(
        entry_points=[CommandHandler(["eda", "iou"], eda_handler)],
        states={
            DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_direction)],
            WHO: [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_who)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_amount)],
            REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_reason)],
            DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_deadline)],
        },
        fallbacks=[
            CommandHandler("cancel", conv_cancel),
            CommandHandler(["eda", "iou"], eda_handler),       # restart mid-flow
            CommandHandler("start", conv_cancel),               # /start breaks out
            CommandHandler("dashboard", conv_cancel),
            CommandHandler(["netib", "score"], conv_cancel),
            CommandHandler(["edawoch", "myious"], conv_cancel),
            CommandHandler(["kefel", "payback"], conv_cancel),
            CommandHandler(["erdata", "help"], conv_cancel),
            CommandHandler("language", conv_cancel),
        ],
        conversation_timeout=300,  # 5 min timeout — auto-cancel abandoned flows
    )
    app.add_handler(eda_conv)

    # /edawoch, /myious
    app.add_handler(CommandHandler(["edawoch", "myious"], edawoch_handler))

    # /kefel, /payback
    app.add_handler(CommandHandler(["kefel", "payback"], kefel_handler))

    # /sebeseb, /collect
    app.add_handler(CommandHandler(["sebeseb", "collect"], sebeseb_handler))

    # /mesebeboch, /collections
    app.add_handler(CommandHandler(["mesebeboch", "collections"], mesebeboch_handler))

    # /dashboard
    app.add_handler(CommandHandler("dashboard", dashboard_handler))

    # /netib, /score
    app.add_handler(CommandHandler(["netib", "score"], netib_handler))

    # /language
    app.add_handler(CommandHandler("language", language_handler))

    # /erdata, /help
    app.add_handler(CommandHandler(["erdata", "help"], help_handler))

    # ── Callback Query Handler (all inline buttons) ──
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
