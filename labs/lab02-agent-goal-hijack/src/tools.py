#!/usr/bin/env python3
"""
tools.py — 3 built-in sample tools for lab01-basic-agent.

These tools demonstrate the agent tool-calling interface and will be
mapped to OWASP Top 10 Agentic AI and MITRE ATLAS in later labs.
"""

import datetime as _dt
import json as _json


# ---------------------------------------------------------------------------
# Tool registry: name -> {description, inputSchema}
# ---------------------------------------------------------------------------
TOOLS: dict = {
    "echo": {
        "name": "echo",
        "description": "Echo the provided message at the screen. Useful to check that the agent is working.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to echo at the screen"
                }
            },
            "required": ["message"]
        }
    },
    "get_time": {
        "name": "get_time",
        "description": "Get the current UTC date and time.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    "calculator": {
        "name": "calculator",
        "description": "Perform a basic arithmetic operation: add, subtract, multiply, divide.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform"
                },
                "a": {
                    "type": "number",
                    "description": "First operand"
                },
                "b": {
                    "type": "number",
                    "description": "Second operand"
                }
            },
            "required": ["operation", "a", "b"]
        }
    },
    "run_command": {
        "name": "run_command",
        "description": "Execute a system command and return its output.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The system command to execute"
                }
            },
            "required": ["command"]
        }
    },
    "read_file": {
        "name": "read_file",
        "description": "Read a file from the filesystem and return its content.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to read"
                }
            },
            "required": ["path"]
        }
    },
    "send_data": {
        "name": "send_data",
        "description": "Send data to an external endpoint. (In this lab, simulates the send for safety; actual HTTP calls are not made.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The endpoint URL to send data to"
                },
                "data": {
                    "type": "string",
                    "description": "The data to send"
                }
            },
            "required": ["url", "data"]
        }
    },
}



# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------
def call_echo(arguments: dict) -> str:
    """Echo the user message at the screen."""
    message = arguments.get("message", "")
    return f"Echo: {message}"


def call_get_time(arguments: dict) -> str:
    """Return the current UTC date/time."""
    now = _dt.datetime.now(_dt.timezone.utc)
    return f"Current UTC time: {now.isoformat()}"


def call_calculator(arguments: dict) -> str:
    """Perform a basic arithmetic operation."""
    operation = arguments.get("operation", "add") or "add"
    a = arguments.get("a", 0)
    b = arguments.get("b", 0)

    if operation == "add":
        result = a + b
        symbol = "+"
    elif operation == "subtract":
        result = a - b
        symbol = "-"
    elif operation == "multiply":
        result = a * b
        symbol = "*"
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero"
        result = a / b
        symbol = "/"
    else:
        return f"Error: Unknown operation '{operation}'"

    # Format integer results without trailing .0
    if isinstance(result, float) and result == int(result):
        result = int(result)

    return f"Result: {a} {symbol} {b} = {result}"


def call_run_command(arguments: dict) -> str:
    """Execute a system command and return its output.

    WARNING: Intentionally vulnerable by design for educational purposes.
    Executes arbitrary commands without any restrictions or allowlists.
    """
    import subprocess
    command = arguments.get("command", "")
    if not command:
        return "Error: No command provided"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return output.strip() if output.strip() else f"Command executed (exit code: {result.returncode})"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {e}"


def call_read_file(arguments: dict) -> str:
    """Read a file from the filesystem and return its content.

    WARNING: Intentionally vulnerable by design for educational purposes.
    Reads arbitrary files without path restrictions.
    """
    path = arguments.get("path", "")
    if not path:
        return "Error: No file path provided"

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error: {e}"


def call_send_data(arguments: dict) -> str:
    """Send data to an external endpoint.

    WARNING: Intentionally vulnerable by design for educational purposes.
    In this lab, the send is SIMULATED for safety — no actual HTTP call is made.
    The data is logged locally so the audit lab can inspect it.
    """
    url = arguments.get("url", "")
    data = arguments.get("data", "")
    if not url:
        return "Error: No URL provided"
    if not data:
        return "Error: No data provided"

    # Simulated send — no actual HTTP request is made
    return (
        f"Simulated send: {len(data)} bytes of data would be sent to {url}. "
        f"(No actual HTTP call was made in this lab.)"
    )


# Map tool name → handler function
TOOL_HANDLERS: dict = {
    "echo": call_echo,
    "get_time": call_get_time,
    "calculator": call_calculator,
    "run_command": call_run_command,
    "read_file": call_read_file,
    "send_data": call_send_data,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def parse_arguments(raw: str | dict) -> dict:
    """Parse tool arguments from JSON string or dict."""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return _json.loads(raw)
        except _json.JSONDecodeError:
            return {}
    return {}
