# Tool registry for the lab01-basic-agent project.
from lab01_basic_agent.tools.basic import get_current_time

TOOLS = {
    "get_current_time": get_current_time,
}

# Tool dispatcher function to execute a tool by name with provided arguments.
def execute_tool(name: str, arguments: dict) -> str:
    tool = TOOLS.get(name)

    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    return tool(**arguments)