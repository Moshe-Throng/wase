"""
Handlers for dashboard and trust score commands:
  /dashboard  — Financial overview
  /netib      — Trust score with breakdown
"""

from telegram import Update
from telegram.ext import ContextTypes

from bot.strings.lang import s
from bot.db.models import upsert_user, get_user_financial_summary
from bot.db.supabase_client import run_sync
from bot.services.trust_score import calculate_trust_score
from bot.utils.formatting import birr, get_name, progress_bar


async def dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dashboard — full financial overview."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    # Run heavy DB queries in thread pool (non-blocking)
    summary = await run_sync(get_user_financial_summary, user.id)
    score_data = await run_sync(calculate_trust_score, user.id)

    lines = [
        t.DASH_TITLE.format(name=get_name(user)),
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

    await update.message.reply_text("\n".join(lines))


async def netib_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /netib — detailed trust score with breakdown."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    t = s(user.id)

    result = await run_sync(calculate_trust_score, user.id)
    c = result["components"]

    lines = [
        t.SCORE_TITLE.format(name=get_name(user)),
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

    await update.message.reply_text("\n".join(lines))
