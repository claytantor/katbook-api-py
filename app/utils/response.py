from typing import Any


def success(data: dict[str, Any] | list[Any], message: str | None = None) -> dict[str, Any]:
    """Standard success envelope matching moltbook API response format."""
    result: dict[str, Any] = {"success": True, "data": data}
    if message:
        result["message"] = message
    return result


def paginated(
    items: list[Any],
    total: int,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    """Paginated success envelope."""
    return {
        "success": True,
        "data": items,
        "pagination": {"total": total, "limit": limit, "offset": offset},
    }
