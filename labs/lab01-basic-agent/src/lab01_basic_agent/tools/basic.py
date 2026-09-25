from datetime import datetime, timezone

def get_current_time() -> str:
    """Return the current UTC time."""
    return datetime.now(timezone.utc).isoformat()