"""
Supabase client singleton for Wase bot.
All database interactions go through this module.

IMPORTANT: supabase-py is synchronous. Use run_sync() to call any DB
function from an async handler so it doesn't block the event loop.
"""

import asyncio
import functools
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env from project root
_env_paths = [
    Path(__file__).parent.parent.parent / ".env",
    Path(__file__).parent.parent.parent.parent / ".env",
]
for _p in _env_paths:
    if _p.exists():
        load_dotenv(_p)
        break

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

_client: Client | None = None


_executor = ThreadPoolExecutor(max_workers=4)


def get_client() -> Client:
    """Get or create Supabase client (singleton, service role)."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


async def run_sync(func, *args, **kwargs):
    """Run a sync function in a thread pool so it doesn't block the event loop.
    Usage: result = await run_sync(get_user_by_id, 123)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor, functools.partial(func, *args, **kwargs)
    )
