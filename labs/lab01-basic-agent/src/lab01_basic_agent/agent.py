# imports
import os

from dotenv import load_dotenv
from ollama import Client

from lab01_basic_agent.tools.registry import TOOLS, execute_tool

# Read environment variables from .env file
load_dotenv()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")

# class definition for the Agent
class Agent:
    def __init__(self, max_iterations: int = 5) -> None:
        self.client = Client(host=OLLAMA_HOST)
        self.max_iterations = max_iterations

    def run(self, user_input: str) -> str:
        messages = [
            {
                "role": "user",
                "content": user_input,
            }
        ]

        for _ in range(self.max_iterations):
            response = self.client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=list(TOOLS.values()),
            )

            if not response.message.tool_calls:
                return response.message.content

            messages.append(response.message)

            for tool_call in response.message.tool_calls:
                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

                print(f"[Agent] Tool requested: {tool_name}")
                print(f"[Agent] Arguments: {arguments}")

                tool_result = execute_tool(tool_name, arguments)

                print(f"[Agent] Tool result: {tool_result}")

                messages.append(
                    {
                        "role": "tool",
                        "content": tool_result,
                    }
                )

        raise RuntimeError(
            f"Agent exceeded maximum iterations ({self.max_iterations})"
        )