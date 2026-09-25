# Tool registry for the lab01-basic-agent project.
# imports
from lab01_basic_agent.tools.basic import days_until_date
from lab01_basic_agent.tools.basic import get_current_date
from lab01_basic_agent.tools.basic import get_current_time

# tools registry
TOOLS = {
    "days_until_date": days_until_date,
    "get_current_date": get_current_date,
    "get_current_time": get_current_time,
}


def execute_tool(name: str, arguments: dict) -> str:
    tool = TOOLS.get(name)

    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    result = tool(**arguments)

    return str(result)