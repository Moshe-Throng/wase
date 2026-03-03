"""
Reminder service for Wase.
Runs every 6 hours via python-telegram-bot's JobQueue.
"""

import logging
from datetime import date, timedelta

from telegram.ext import ContextTypes

from bot.strings import am
from bot.db.models import (
    get_ious_needing_reminder, get_user_by_id, increment_reminder,
    record_trust_event, has_overdue_event,
)
from bot.utils.formatting import birr, get_name_from_record

logger = logging.getLogger(__name__)


async def reminder_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Periodic job that sends reminders for IOUs approaching or past due date.

    Rules:
    - IOUs due within 3 days: remind borrower (max 3 reminders)
    - IOUs past due: remind borrower AND notify lender,
      record overdue trust event (once per IOU)
    """
    ious = get_ious_needing_reminder()
    today = date.today()

    for iou in ious:
        due_str = iou.get("due_date")
        if not due_str:
            continue

        # Parse due date
        if isinstance(due_str, str):
            from datetime import datetime
            try:
                due = datetime.strptime(due_str, "%Y-%m-%d").date()
            except ValueError:
                continue
        else:
            due = due_str

        days_until = (due - today).days

        lender = get_user_by_id(iou["lender_id"])
        lender_name = get_name_from_record(lender) if lender else str(iou["lender_id"])
        borrower = get_user_by_id(iou["borrower_id"])

        if days_until < 0:
            # OVERDUE
            days_late = abs(days_until)

            # Record overdue penalty (once only)
            if not has_overdue_event(iou["id"]):
                record_trust_event(iou["borrower_id"], "iou_overdue", -5, iou["id"])

            # Remind borrower
            try:
                await context.bot.send_message(
                    chat_id=iou["borrower_id"],
                    text=am.REMINDER_OVERDUE.format(
                        id=iou["id"],
                        lender=lender_name,
                        amount=birr(iou["amount"]),
                        days=days_late,
                    ),
                )
            except Exception as e:
                logger.warning(f"Failed to send overdue reminder to borrower {iou['borrower_id']}: {e}")

            # Notify lender
            borrower_username = borrower.get("username", "?") if borrower else "?"
            try:
                await context.bot.send_message(
                    chat_id=iou["lender_id"],
                    text=am.REMINDER_OVERDUE_LENDER.format(
                        borrower=borrower_username,
                        id=iou["id"],
                        amount=birr(iou["amount"]),
                        days=days_late,
                    ),
                )
            except Exception as e:
                logger.warning(f"Failed to send overdue notice to lender {iou['lender_id']}: {e}")

            increment_reminder(iou["id"])

        elif days_until <= 3 and iou["reminder_count"] < 3:
            # APPROACHING DUE DATE — remind borrower only
            try:
                await context.bot.send_message(
                    chat_id=iou["borrower_id"],
                    text=am.REMINDER.format(
                        id=iou["id"],
                        lender=lender_name,
                        amount=birr(iou["amount"]),
                        days=days_until,
                    ),
                )
            except Exception as e:
                logger.warning(f"Failed to send reminder to borrower {iou['borrower_id']}: {e}")

            increment_reminder(iou["id"])

    logger.info(f"Reminder job completed. Processed {len(ious)} IOUs.")
