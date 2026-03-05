"""
Utility functions for formatting, parsing commands, and name resolution.
"""

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from telegram import User


def birr(amount) -> str:
    """Format amount as Ethiopian Birr string: '1,234 ብር'."""
    if isinstance(amount, Decimal):
        amount = float(amount)
    if amount == int(amount):
        return f"{int(amount):,} ብር"
    return f"{amount:,.2f} ብር"


def get_name(user: User) -> str:
    """Get display name from Telegram user object."""
    if user.first_name:
        return user.first_name
    if user.username:
        return f"@{user.username}"
    return str(user.id)


def get_name_from_record(record: dict) -> str:
    """Get display name from a wase_users database record."""
    if record.get("first_name"):
        return record["first_name"]
    if record.get("username"):
        return f"@{record['username']}"
    return str(record["user_id"])


def parse_amount(text: str) -> Decimal | None:
    """Parse an amount string, stripping commas. Returns None if invalid."""
    text = text.strip().replace(",", "")
    try:
        amount = Decimal(text)
        if amount <= 0:
            return None
        return amount
    except (InvalidOperation, ValueError):
        return None


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate text to max length."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"


def parse_iou_command(text: str) -> dict | None:
    """
    Parse /eda command arguments.
    Format: @username amount [reason] [ቀን YYYY-MM-DD]

    Returns dict with keys: username, amount, description, due_date
    or None if parsing fails.
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # Extract @username
    match = re.match(r"@(\w+)\s+(.+)", text)
    if not match:
        return None

    username = match.group(1)
    rest = match.group(2).strip()

    # Extract due date if present (ቀን YYYY-MM-DD or due YYYY-MM-DD)
    due_date = None
    date_pattern = r"(?:ቀን|due)\s+(\d{4}-\d{2}-\d{2})"
    date_match = re.search(date_pattern, rest)
    if date_match:
        try:
            due_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
        except ValueError:
            pass  # Invalid date, ignore
        rest = rest[:date_match.start()].strip()

    # Extract amount (first number in remaining text)
    amount_match = re.match(r"([\d,]+(?:\.\d+)?)\s*(.*)", rest)
    if not amount_match:
        return None

    amount = parse_amount(amount_match.group(1))
    if amount is None:
        return None

    description = truncate(amount_match.group(2).strip()) or None

    return {
        "username": username,
        "amount": amount,
        "description": description,
        "due_date": due_date,
    }


def parse_collection_command(text: str) -> dict | None:
    """
    Parse /sebseb command arguments.
    Format: title - amount ሰው/each  OR  title - amount ጠቅላላ/total

    Returns dict with keys: title, amount_per_person, target_amount
    or None if parsing fails.
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # Split on dash separator
    parts = text.split("-", 1)
    if len(parts) != 2:
        return None

    title = truncate(parts[0].strip())
    if not title:
        return None

    amount_part = parts[1].strip()

    # Extract amount
    amount_match = re.match(r"([\d,]+(?:\.\d+)?)\s*(.*)", amount_part)
    if not amount_match:
        return None

    amount = parse_amount(amount_match.group(1))
    if amount is None:
        return None

    type_hint = amount_match.group(2).strip().lower()

    # Determine if per-person or total target
    is_total = any(kw in type_hint for kw in ["ጠቅላላ", "total"])

    if is_total:
        return {
            "title": title,
            "amount_per_person": None,
            "target_amount": amount,
        }
    else:
        # Default: per-person (keywords: ሰው, each, or nothing)
        return {
            "title": title,
            "amount_per_person": amount,
            "target_amount": None,
        }


def parse_relative_deadline(text: str):
    """
    Parse relative deadline like '10 days', '3 weeks', '2 months'.
    Also supports Amharic: '10 ቀን', '3 ሳምንት', '2 ወር'.
    Returns a date or None.
    """
    from datetime import timedelta

    text = text.lower().strip()
    match = re.match(r"(\d+)\s*(day|days|ቀን|ቀናት|week|weeks|ሳምንት|month|months|ወር|ወራት)", text)
    if not match:
        return None

    num = int(match.group(1))
    unit = match.group(2)
    today = date.today()

    if unit in ("day", "days", "ቀን", "ቀናት"):
        return today + timedelta(days=num)
    elif unit in ("week", "weeks", "ሳምንት"):
        return today + timedelta(weeks=num)
    elif unit in ("month", "months", "ወር", "ወራት"):
        return today + timedelta(days=num * 30)
    return None


def progress_bar(current: int, total: int, width: int = 10) -> str:
    """Create a text progress bar. Example: '████████░░ 80%'"""
    if total <= 0:
        return "░" * width + " 0%"
    ratio = min(current / total, 1.0)
    filled = int(ratio * width)
    empty = width - filled
    pct = int(ratio * 100)
    return "█" * filled + "░" * empty + f" {pct}%"


def format_date(d: date | str | None) -> str:
    """Format a date for display. Returns empty string if None."""
    if d is None:
        return ""
    if isinstance(d, str):
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return d
    return d.strftime("%d/%m/%Y")
