ALLOWED_TOOLS = {
    "get_current_date",
    "get_current_time",
    "days_until_date",
}


def is_tool_allowed(tool_name: str) -> bool:
    """Return True if the tool is allowed by the current policy."""
    return tool_name in ALLOWED_TOOLS