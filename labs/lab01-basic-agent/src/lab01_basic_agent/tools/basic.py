# imports
from datetime import datetime, timezone

# tools definitions
def get_current_time() -> str:
    """Return the current UTC time."""
    return datetime.now(timezone.utc).isoformat()


def get_current_date() -> str:
    """Return the current UTC date."""
    return datetime.now(timezone.utc).date().isoformat()

def days_until_date(current_date: str, target_date: str) -> int:
    """Return the number of days between the current date and a target date."""
    current = datetime.strptime(current_date, "%Y-%m-%d").date()
    target = datetime.strptime(target_date, "%Y-%m-%d").date()

    return (target - current).days