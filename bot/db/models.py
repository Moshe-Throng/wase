"""
Database query helpers for Wase tables.
Each function maps to a specific operation on wase_* tables.
"""

import threading
import time
from datetime import datetime, date
from decimal import Decimal
from .supabase_client import get_client


# ══════════════════════════════════════════════════════════════
# USER CACHE — avoid Supabase round-trip on every message
# ══════════════════════════════════════════════════════════════

_user_cache: dict[int, dict] = {}            # user_id -> record
_username_cache: dict[str, int] = {}         # username -> user_id
_user_cache_time: dict[int, float] = {}      # user_id -> last_upserted_ts
_CACHE_TTL = 300  # Only re-upsert to Supabase every 5 minutes


# ══════════════════════════════════════════════════════════════
# USERS
# ══════════════════════════════════════════════════════════════

def upsert_user(user_id: int, username: str | None, first_name: str | None) -> dict:
    """Create or update a user. Uses cache to avoid blocking on every message."""
    now = time.time()

    # If user NOT in cache yet (first msg after bot restart), load from DB synchronously ONCE
    if user_id not in _user_cache:
        _load_user_from_db(user_id)

    # Build record preserving existing cached language
    existing = _user_cache.get(user_id, {})
    record = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "language": existing.get("language", "am"),
    }

    _user_cache[user_id] = record
    if username:
        _username_cache[username.lower()] = user_id

    # Persist to Supabase periodically (background, non-blocking)
    last = _user_cache_time.get(user_id, 0)
    if now - last > _CACHE_TTL:
        _user_cache_time[user_id] = now
        data = {"user_id": user_id, "first_name": first_name}
        if username:
            data["username"] = username
        threading.Thread(target=_bg_upsert, args=(data,), daemon=True).start()

    return record


def _load_user_from_db(user_id: int) -> None:
    """Load a user from Supabase into cache. Called once per user per bot restart."""
    try:
        result = (
            get_client()
            .table("wase_users")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if result.data:
            rec = result.data[0]
            _user_cache[user_id] = rec
            # Seed the language cache from DB
            from bot.strings.lang import seed_lang
            seed_lang(user_id, rec.get("language", "am"))
            if rec.get("username"):
                _username_cache[rec["username"].lower()] = user_id
    except Exception:
        pass  # Will default to "am" if DB is unreachable


def _bg_upsert(data: dict) -> None:
    """Background thread: upsert user to Supabase."""
    try:
        get_client().table("wase_users").upsert(data, on_conflict="user_id").execute()
    except Exception:
        pass


def get_user_by_username(username: str) -> dict | None:
    """Find a user by their Telegram @username. Checks cache first."""
    uid = _username_cache.get(username.lower())
    if uid and uid in _user_cache:
        return _user_cache[uid]

    result = (
        get_client()
        .table("wase_users")
        .select("*")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    if result.data:
        rec = result.data[0]
        _user_cache[rec["user_id"]] = rec
        if rec.get("username"):
            _username_cache[rec["username"].lower()] = rec["user_id"]
        return rec
    return None


def get_user_by_id(user_id: int) -> dict | None:
    """Find a user by their Telegram user ID. Checks cache first."""
    if user_id in _user_cache:
        return _user_cache[user_id]

    result = (
        get_client()
        .table("wase_users")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if result.data:
        rec = result.data[0]
        _user_cache[rec["user_id"]] = rec
        if rec.get("username"):
            _username_cache[rec["username"].lower()] = rec["user_id"]
        return rec
    return None


# ══════════════════════════════════════════════════════════════
# IOUs
# ══════════════════════════════════════════════════════════════

def create_iou(
    lender_id: int,
    borrower_id: int,
    amount: Decimal,
    description: str | None = None,
    due_date: date | None = None,
) -> dict:
    """Create a new IOU record."""
    data = {
        "lender_id": lender_id,
        "borrower_id": borrower_id,
        "amount": float(amount),
    }
    if description:
        data["description"] = description
    if due_date:
        data["due_date"] = due_date.isoformat()

    result = get_client().table("wase_ious").insert(data).execute()
    return result.data[0]


def get_iou(iou_id: int) -> dict | None:
    """Get an IOU by ID."""
    result = (
        get_client()
        .table("wase_ious")
        .select("*")
        .eq("id", iou_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def get_active_ious_for_user(user_id: int) -> list[dict]:
    """Get all non-completed IOUs where user is lender or borrower."""
    as_lender = (
        get_client()
        .table("wase_ious")
        .select("*")
        .eq("lender_id", user_id)
        .neq("status", "completed")
        .order("created_at", desc=True)
        .execute()
        .data
    )
    as_borrower = (
        get_client()
        .table("wase_ious")
        .select("*")
        .eq("borrower_id", user_id)
        .neq("status", "completed")
        .order("created_at", desc=True)
        .execute()
        .data
    )
    return {"as_lender": as_lender, "as_borrower": as_borrower}


def confirm_iou(iou_id: int) -> dict:
    """Borrower confirms the IOU."""
    result = (
        get_client()
        .table("wase_ious")
        .update({"confirmed_by_borrower": True, "status": "confirmed"})
        .eq("id", iou_id)
        .execute()
    )
    return result.data[0] if result.data else {}


def dispute_iou(iou_id: int) -> dict:
    """Borrower disputes the IOU."""
    result = (
        get_client()
        .table("wase_ious")
        .update({"status": "disputed"})
        .eq("id", iou_id)
        .execute()
    )
    return result.data[0] if result.data else {}


def complete_iou(iou_id: int) -> dict:
    """Mark IOU as completed (paid)."""
    result = (
        get_client()
        .table("wase_ious")
        .update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
        })
        .eq("id", iou_id)
        .execute()
    )
    return result.data[0] if result.data else {}


def increment_reminder(iou_id: int) -> None:
    """Increment the reminder count for an IOU."""
    iou = get_iou(iou_id)
    if iou:
        get_client().table("wase_ious").update(
            {"reminder_count": iou["reminder_count"] + 1}
        ).eq("id", iou_id).execute()


def get_ious_needing_reminder() -> list[dict]:
    """Get confirmed IOUs with due dates within 3 days or overdue."""
    # Get all confirmed IOUs with a due date
    result = (
        get_client()
        .table("wase_ious")
        .select("*")
        .eq("status", "confirmed")
        .not_.is_("due_date", "null")
        .execute()
    )
    return result.data


# ══════════════════════════════════════════════════════════════
# COLLECTIONS
# ══════════════════════════════════════════════════════════════

def create_collection(
    creator_id: int,
    chat_id: int,
    title: str,
    amount_per_person: Decimal | None = None,
    target_amount: Decimal | None = None,
) -> dict:
    """Create a new collection."""
    data = {
        "creator_id": creator_id,
        "chat_id": chat_id,
        "title": title,
    }
    if amount_per_person is not None:
        data["amount_per_person"] = float(amount_per_person)
    if target_amount is not None:
        data["target_amount"] = float(target_amount)

    result = get_client().table("wase_collections").insert(data).execute()
    return result.data[0]


def get_collection(collection_id: int) -> dict | None:
    """Get a collection by ID."""
    result = (
        get_client()
        .table("wase_collections")
        .select("*")
        .eq("id", collection_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def get_active_collections_in_chat(chat_id: int) -> list[dict]:
    """Get all active collections for a group chat."""
    return (
        get_client()
        .table("wase_collections")
        .select("*")
        .eq("chat_id", chat_id)
        .eq("status", "active")
        .order("created_at", desc=True)
        .execute()
        .data
    )


def complete_collection(collection_id: int) -> dict:
    """Mark a collection as completed."""
    result = (
        get_client()
        .table("wase_collections")
        .update({"status": "completed"})
        .eq("id", collection_id)
        .execute()
    )
    return result.data[0] if result.data else {}


# ══════════════════════════════════════════════════════════════
# CONTRIBUTIONS
# ══════════════════════════════════════════════════════════════

def record_contribution(collection_id: int, user_id: int, amount: Decimal | None) -> dict | None:
    """Record a contribution. Returns None if already paid (duplicate)."""
    data = {
        "collection_id": collection_id,
        "user_id": user_id,
        "status": "paid",
        "confirmed_at": datetime.utcnow().isoformat(),
    }
    if amount is not None:
        data["amount"] = float(amount)

    try:
        result = get_client().table("wase_contributions").insert(data).execute()
        return result.data[0] if result.data else data
    except Exception as e:
        if "duplicate" in str(e).lower() or "23505" in str(e):
            return None  # Already paid
        raise


def get_contributions_for_collection(collection_id: int) -> list[dict]:
    """Get all contributions for a collection."""
    return (
        get_client()
        .table("wase_contributions")
        .select("*")
        .eq("collection_id", collection_id)
        .order("confirmed_at")
        .execute()
        .data
    )


def has_user_contributed(collection_id: int, user_id: int) -> bool:
    """Check if a user has already contributed to a collection."""
    result = (
        get_client()
        .table("wase_contributions")
        .select("id")
        .eq("collection_id", collection_id)
        .eq("user_id", user_id)
        .eq("status", "paid")
        .limit(1)
        .execute()
    )
    return len(result.data) > 0


# ══════════════════════════════════════════════════════════════
# TRUST EVENTS
# ══════════════════════════════════════════════════════════════

def record_trust_event(
    user_id: int,
    event_type: str,
    score_delta: float,
    reference_id: int | None = None,
) -> dict:
    """Record a trust event."""
    data = {
        "user_id": user_id,
        "event_type": event_type,
        "score_delta": score_delta,
    }
    if reference_id is not None:
        data["reference_id"] = reference_id

    result = get_client().table("wase_trust_events").insert(data).execute()
    return result.data[0] if result.data else data


def get_trust_events_for_user(user_id: int) -> list[dict]:
    """Get all trust events for a user."""
    return (
        get_client()
        .table("wase_trust_events")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
        .data
    )


def has_overdue_event(iou_id: int) -> bool:
    """Check if an overdue trust event already exists for an IOU."""
    result = (
        get_client()
        .table("wase_trust_events")
        .select("id")
        .eq("event_type", "iou_overdue")
        .eq("reference_id", iou_id)
        .limit(1)
        .execute()
    )
    return len(result.data) > 0


# ══════════════════════════════════════════════════════════════
# AGGREGATE QUERIES (for dashboard + trust score)
# ══════════════════════════════════════════════════════════════

def get_user_financial_summary(user_id: int) -> dict:
    """Get dashboard summary: owed to user, user owes, overdue, completed."""
    ious = get_active_ious_for_user(user_id)

    owed_to_user = sum(
        float(i["amount"]) for i in ious["as_lender"]
        if i["status"] in ("pending", "confirmed")
    )
    user_owes = sum(
        float(i["amount"]) for i in ious["as_borrower"]
        if i["status"] in ("pending", "confirmed")
    )
    overdue = sum(
        1 for i in (ious["as_lender"] + ious["as_borrower"])
        if i.get("due_date") and i["due_date"] < date.today().isoformat()
        and i["status"] in ("pending", "confirmed")
    )

    # Lifetime completed IOUs
    completed = (
        get_client()
        .table("wase_ious")
        .select("id", count="exact")
        .eq("status", "completed")
        .or_(f"lender_id.eq.{user_id},borrower_id.eq.{user_id}")
        .execute()
    )

    # Lifetime contributions
    contributions = (
        get_client()
        .table("wase_contributions")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("status", "paid")
        .execute()
    )

    return {
        "owed_to_user": owed_to_user,
        "user_owes": user_owes,
        "net": owed_to_user - user_owes,
        "overdue_count": overdue,
        "completed_count": completed.count or 0,
        "contribution_count": contributions.count or 0,
    }


def get_trust_score_data(user_id: int) -> dict:
    """Get raw data needed to calculate trust score."""
    # IOUs as borrower (total and repaid)
    total_as_borrower = (
        get_client()
        .table("wase_ious")
        .select("id", count="exact")
        .eq("borrower_id", user_id)
        .in_("status", ["confirmed", "completed"])
        .execute()
    )
    repaid = (
        get_client()
        .table("wase_ious")
        .select("id", count="exact")
        .eq("borrower_id", user_id)
        .eq("status", "completed")
        .execute()
    )

    # Collection contributions
    contributions = (
        get_client()
        .table("wase_contributions")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("status", "paid")
        .execute()
    )

    # Unique connections (people interacted with via IOUs)
    as_lender = (
        get_client()
        .table("wase_ious")
        .select("borrower_id")
        .eq("lender_id", user_id)
        .execute()
        .data
    )
    as_borrower = (
        get_client()
        .table("wase_ious")
        .select("lender_id")
        .eq("borrower_id", user_id)
        .execute()
        .data
    )
    unique_people = set()
    for i in as_lender:
        unique_people.add(i["borrower_id"])
    for i in as_borrower:
        unique_people.add(i["lender_id"])

    # Any history at all
    any_history = (total_as_borrower.count or 0) > 0 or len(as_lender) > 0

    # Overdue IOUs (current, as borrower)
    overdue_ious = (
        get_client()
        .table("wase_ious")
        .select("id")
        .eq("borrower_id", user_id)
        .eq("status", "confirmed")
        .lt("due_date", date.today().isoformat())
        .execute()
        .data
    )

    return {
        "total_as_borrower": total_as_borrower.count or 0,
        "repaid": repaid.count or 0,
        "contributions": contributions.count or 0,
        "unique_connections": len(unique_people),
        "has_history": any_history,
        "overdue_count": len(overdue_ious),
    }
