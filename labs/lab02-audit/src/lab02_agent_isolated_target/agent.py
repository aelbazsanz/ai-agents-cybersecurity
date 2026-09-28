import json
import os

from ollama import Client

from lab02_agent_isolated_target.tools.network import (
    check_tcp_port,
    http_get,
    resolve_host,
)

SYSTEM_PROMPT = """\
You are a cybersecurity reconnaissance agent.

You investigate the configured target using the tools available to you.

The target hostname is provided by the environment and should be used when
the user asks you to investigate the target.

Do not assume information that has not been observed.
Use tools when they are useful to answer the user's request.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "resolve_host",
            "description": "Resolve a hostname to an IP address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "Hostname to resolve.",
                    }
                },
                "required": ["host"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_tcp_port",
            "description": "Check whether a TCP port is reachable on a host.",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "Hostname or IP address to check.",
                    },
                    "port": {
                        "type": "integer",
                        "description": "TCP port number to check.",
                    },
                },
                "required": ["host", "port"],
            },
        },
    },
            {
            "type": "function",
            "function": {
                "name": "http_get",
                "description": "Perform an HTTP GET request against a host and port.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "host": {
                            "type": "string",
                            "description": "Hostname or IP address of the HTTP server.",
                        },
                        "port": {
                            "type": "integer",
                            "description": "TCP port of the HTTP server.",
                        },
                        "path": {
                            "type": "string",
                            "description": "HTTP path, for example / or /health.",
                        },
                    },
                    "required": ["host", "port", "path"],
                },
            },
        },
]

def execute_tool(name: str, arguments: dict) -> dict:
    if name == "resolve_host":
        return resolve_host(**arguments)

    if name == "check_tcp_port":
        return check_tcp_port(**arguments)

    if name == "http_get":
        return http_get(**arguments)

    raise ValueError(f"Unknown tool: {name}")

class Agent:
    def __init__(self) -> None:
        self.client = Client(host=os.environ["OLLAMA_HOST"])
        self.model = os.environ["OLLAMA_MODEL"]
        self.target_host = os.environ["TARGET_HOST"]

        self.messages = [
            {
                "role": "system",
                "content": (
                    f"{SYSTEM_PROMPT}\n"
                    f"Configured target: {self.target_host}"
                ),
            }
        ]

    def run(self, user_input: str) -> str:
        self.messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        while True:
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=TOOLS,
            )

            message = response.message
            self.messages.append(message)

            if not message.tool_calls:
                return message.content

            for tool_call in message.tool_calls:
                name = tool_call.function.name
                arguments = tool_call.function.arguments

                print(
                    f"[TOOL] {name} "
                    f"args={json.dumps(arguments, ensure_ascii=False)}"
                )

                result = execute_tool(name, arguments)

                print(
                    f"[RESULT] "
                    f"{json.dumps(result, ensure_ascii=False)}"
                )

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_name": name,
                        "content": json.dumps(result),
                    }
                )