import math
from datetime import datetime, timezone


def _epoch_seconds(dt: datetime) -> float:
    """Convert a datetime to Unix timestamp seconds."""
    return dt.replace(tzinfo=timezone.utc).timestamp()


def hot_score(upvotes: int, downvotes: int, created_at: datetime) -> float:
    """
    Reddit-style hot ranking.

    Combines a Wilson-score-like popularity signal with time decay so that
    fresh content with fewer votes can still outrank old content with many
    votes once enough time has passed.
    """
    score = upvotes - downvotes
    order = math.log(max(abs(score), 1), 10)
    sign = 1 if score > 0 else (-1 if score < 0 else 0)
    # Epoch chosen so that posts created after 2024-01-01 have a positive base
    epoch = _epoch_seconds(datetime(2024, 1, 1, tzinfo=timezone.utc))
    seconds = _epoch_seconds(created_at) - epoch
    return round(sign * order + seconds / 45000, 7)


def rising_score(score: int, created_at: datetime) -> float:
    """
    Velocity-based score: net score divided by hours since posting.

    New posts with any positive engagement rise quickly; older posts with the
    same score fall back in the ranking.
    """
    now = datetime.now(tz=timezone.utc)
    hours = max((now - created_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600, 0.1)
    return score / hours


def top_score(upvotes: int, downvotes: int) -> int:
    """Net score for 'top' sort."""
    return upvotes - downvotes
