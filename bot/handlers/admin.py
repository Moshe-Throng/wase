"""
Admin command: /admin — Bot stats dashboard (restricted to ADMIN_IDS).
"""

from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from bot.db.models import upsert_user
from bot.db.supabase_client import get_client, run_sync

# Admin user IDs (Telegram user IDs who can run /admin)
ADMIN_IDS = {297659579}  # @Moshede


def _fetch_stats() -> dict:
    """Fetch all admin stats from Supabase (sync, run via run_sync)."""
    client = get_client()
    today = datetime.utcnow().date().isoformat()
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

    # Total users
    users = client.table("wase_users").select("user_id", count="exact").execute()
    total_users = users.count or 0

    # Users registered today
    new_today = client.table("wase_users").select("user_id", count="exact").gte("created_at", today).execute()
    new_today_count = new_today.count or 0

    # Total IOUs
    all_ious = client.table("wase_ious").select("id", count="exact").execute()
    total_ious = all_ious.count or 0

    # IOUs created today
    ious_today = client.table("wase_ious").select("id", count="exact").gte("created_at", today).execute()
    ious_today_count = ious_today.count or 0

    # IOUs this week
    ious_week = client.table("wase_ious").select("id", count="exact").gte("created_at", week_ago).execute()
    ious_week_count = ious_week.count or 0

    # By status
    pending = client.table("wase_ious").select("id", count="exact").eq("status", "pending").execute()
    confirmed = client.table("wase_ious").select("id", count="exact").eq("status", "confirmed").execute()
    completed = client.table("wase_ious").select("id", count="exact").eq("status", "completed").execute()
    disputed = client.table("wase_ious").select("id", count="exact").eq("status", "disputed").execute()

    # Total volume (sum of all IOU amounts)
    all_amounts = client.table("wase_ious").select("amount").execute()
    total_volume = sum(float(r["amount"]) for r in (all_amounts.data or []))

    # Collections
    total_collections = client.table("wase_collections").select("id", count="exact").execute()
    total_contributions = client.table("wase_contributions").select("id", count="exact").eq("status", "paid").execute()

    # Trust events
    total_events = client.table("wase_trust_events").select("id", count="exact").execute()

    # Language breakdown
    lang_en = client.table("wase_users").select("user_id", count="exact").eq("language", "en").execute()
    lang_am = client.table("wase_users").select("user_id", count="exact").eq("language", "am").execute()

    return {
        "total_users": total_users,
        "new_today": new_today_count,
        "total_ious": total_ious,
        "ious_today": ious_today_count,
        "ious_week": ious_week_count,
        "pending": pending.count or 0,
        "confirmed": confirmed.count or 0,
        "completed": completed.count or 0,
        "disputed": disputed.count or 0,
        "total_volume": total_volume,
        "total_collections": total_collections.count or 0,
        "total_contributions": total_contributions.count or 0,
        "total_events": total_events.count or 0,
        "lang_en": lang_en.count or 0,
        "lang_am": lang_am.count or 0,
    }


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /admin — show bot stats (admin only)."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only")
        return

    stats = await run_sync(_fetch_stats)

    lines = [
        "📊 WASE ADMIN DASHBOARD",
        f"{'━' * 28}",
        "",
        "👥 USERS",
        f"  Total: {stats['total_users']}",
        f"  New today: {stats['new_today']}",
        f"  🇬🇧 English: {stats['lang_en']}  |  🇪🇹 Amharic: {stats['lang_am']}",
        "",
        "🤝 IOUs",
        f"  Total: {stats['total_ious']}",
        f"  Today: {stats['ious_today']}  |  This week: {stats['ious_week']}",
        f"  💰 Volume: {stats['total_volume']:,.0f} Birr",
        "",
        f"  ⏳ Pending: {stats['pending']}",
        f"  ✅ Confirmed: {stats['confirmed']}",
        f"  🎉 Completed: {stats['completed']}",
        f"  ⚠️ Disputed: {stats['disputed']}",
        "",
        "💰 COLLECTIONS",
        f"  Total: {stats['total_collections']}",
        f"  Contributions: {stats['total_contributions']}",
        "",
        f"🛡 Trust events: {stats['total_events']}",
    ]

    await update.message.reply_text("\n".join(lines))
