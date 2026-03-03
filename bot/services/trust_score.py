"""
Trust score calculation for Wase.

Score components (max 100):
  - IOUs Repaid:             40 pts  (repaid / total_as_borrower * 40)
  - Collection Contributions: 30 pts  (min(count * 3, 30))
  - Connections:              20 pts  (min(unique_people * 3, 20))
  - History Exists:           10 pts  (10 if any transactions, else 0)
  - Overdue Penalty:          -5 each (-5 per IOU past due)

Tiers:
  0-29  = አዲስ (New)
  30-59 = እየተሻሻለ (Rising)
  60-84 = አስተማማኝ (Trusted)
  85-100 = በጣም ጥሩ (Excellent)
"""

from bot.db.models import get_trust_score_data
from bot.strings.lang import s


def calculate_trust_score(user_id: int) -> dict:
    """
    Calculate trust score for a user.

    Returns dict with:
      score: int (0-100)
      tier: str (Amharic tier label)
      components: dict with individual component scores
    """
    data = get_trust_score_data(user_id)

    # Component 1: IOUs repaid (max 40)
    if data["total_as_borrower"] > 0:
        repaid_score = int((data["repaid"] / data["total_as_borrower"]) * 40)
    else:
        repaid_score = 0

    # Component 2: Collection contributions (max 30)
    collect_score = min(data["contributions"] * 3, 30)

    # Component 3: Connections (max 20)
    connect_score = min(data["unique_connections"] * 3, 20)

    # Component 4: History exists (10 or 0)
    history_score = 10 if data["has_history"] else 0

    # Component 5: Overdue penalty (-5 each)
    overdue_penalty = data["overdue_count"] * 5

    # Total score (clamped to 0-100)
    raw_score = repaid_score + collect_score + connect_score + history_score - overdue_penalty
    score = max(0, min(100, raw_score))

    # Determine tier (in user's language)
    t = s(user_id)
    if score >= 85:
        tier = t.TIER_EXCELLENT
    elif score >= 60:
        tier = t.TIER_TRUSTED
    elif score >= 30:
        tier = t.TIER_RISING
    else:
        tier = t.TIER_NEW

    return {
        "score": score,
        "tier": tier,
        "components": {
            "repaid": {
                "score": repaid_score,
                "max": 40,
                "done": data["repaid"],
                "total": data["total_as_borrower"],
            },
            "collections": {
                "score": collect_score,
                "max": 30,
                "count": data["contributions"],
            },
            "connections": {
                "score": connect_score,
                "max": 20,
                "count": data["unique_connections"],
            },
            "history": {
                "score": history_score,
                "max": 10,
                "has_history": data["has_history"],
            },
            "overdue": {
                "penalty": overdue_penalty,
                "count": data["overdue_count"],
            },
        },
    }
