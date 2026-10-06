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


# Map tool name → handler function
TOOL_HANDLERS: dict = {
    "echo": call_echo,
    "get_time": call_get_time,
    "calculator": call_calculator,
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
