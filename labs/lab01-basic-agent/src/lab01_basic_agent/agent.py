# imports
import os
import time

from dotenv import load_dotenv
from ollama import Client

from lab01_basic_agent.tools.registry import TOOLS, execute_tool

# read environment variables from .env file
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")

# Class definition for the Agent
class Agent:
    def __init__(self, max_iterations: int = 5) -> None:
        self.client = Client(host=OLLAMA_HOST)
        self.max_iterations = max_iterations

    def run(self, user_input: str) -> str:
        run_start = time.perf_counter()

        # time tracking variables
        total_llm_time = 0.0
        total_tool_time = 0.0
        tool_call_count = 0

        # event tracking
        events = []

        # messages list to maintain the conversation context
        messages = [
            {
                "role": "user",
                "content": user_input,
            }
        ]

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n[Agent] Iteration {iteration}")

            iteration_start = time.perf_counter()

            response = self.client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=list(TOOLS.values()),
            )

            iteration_duration = time.perf_counter() - iteration_start
            total_llm_time += iteration_duration

            events.append(
                {
                    "type": "llm_call",
                    "iteration": iteration,
                    "duration": iteration_duration,
                }
            )

            print(
                f"[Agent] LLM response received in "
                f"{iteration_duration:.3f}s"
            )

            if not response.message.tool_calls:
                total_duration = time.perf_counter() - run_start

                print("\n[Agent] Run summary")
                print(f"[Agent] Iterations: {iteration}")
                print(f"[Agent] Tool calls: {tool_call_count}")
                print(f"[Agent] LLM time: {total_llm_time:.3f}s")
                print(f"[Agent] Tool time: {total_tool_time:.6f}s")
                print(f"[Agent] Total time: {total_duration:.3f}s")

                return response.message.content

            messages.append(response.message)

            for tool_call in response.message.tool_calls:
                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

                print(f"[Agent] Tool requested: {tool_name}")
                print(f"[Agent] Arguments: {arguments}")

                tool_start = time.perf_counter()

                tool_result = execute_tool(tool_name, arguments)

                tool_duration = time.perf_counter() - tool_start

                total_tool_time += tool_duration
                tool_call_count += 1

                events.append(
                    {
                        "type": "tool_call",
                        "iteration": iteration,
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": tool_result,
                        "duration": tool_duration,
                    }
                )

                print(f"[Agent] Tool result: {tool_result}")
                print(f"[Agent] Tool duration: {tool_duration:.6f}s")

                messages.append(
                    {
                        "role": "tool",
                        "content": tool_result,
                    }
                )

        raise RuntimeError(
            f"Agent exceeded maximum iterations ({self.max_iterations})"
        )