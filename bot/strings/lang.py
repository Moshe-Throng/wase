"""
Language helper for Wase bot.
Returns the correct strings module based on user's language preference.
"""

import threading
from bot.strings import am, en

_LANG_MAP = {
    "am": am,
    "en": en,
}

# Single source of truth for language preference
_lang_cache: dict[int, str] = {}


def seed_lang(user_id: int, lang: str) -> None:
    """Seed the language cache from a DB record. Only sets if not already cached."""
    if user_id not in _lang_cache:
        _lang_cache[user_id] = lang


def get_strings(user_id: int):
    """Get the strings module for a user. Defaults to Amharic."""
    lang = _lang_cache.get(user_id, "am")
    return _LANG_MAP.get(lang, am)


def get_lang(user_id: int) -> str:
    return _lang_cache.get(user_id, "am")


def set_lang(user_id: int, lang: str) -> None:
    """Set language (cache immediately, persist to DB in background)."""
    _lang_cache[user_id] = lang
    # Also update model cache
    from bot.db.models import _user_cache
    if user_id in _user_cache:
        _user_cache[user_id]["language"] = lang
    # Persist
    threading.Thread(target=_bg_set_lang, args=(user_id, lang), daemon=True).start()


def _bg_set_lang(user_id: int, lang: str) -> None:
    try:
        from bot.db.supabase_client import get_client
        get_client().table("wase_users").update(
            {"language": lang}
        ).eq("user_id", user_id).execute()
    except Exception:
        pass


def s(user_id: int):
    """Shorthand alias for get_strings."""
    return get_strings(user_id)
