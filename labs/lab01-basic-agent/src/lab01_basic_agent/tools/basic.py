# imports
from datetime import datetime, timezone

# tools definitions
def get_current_time() -> str:
    """Return the current UTC time."""
    return datetime.now(timezone.utc).isoformat()


def get_current_date() -> str:
    """Return the current UTC date."""
    return datetime.now(timezone.utc).date().isoformat()