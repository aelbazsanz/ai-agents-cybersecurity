import os

from dotenv import load_dotenv
from ollama import Client

from lab01_basic_agent.tools.basic import get_current_time


load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")


client = Client(host=OLLAMA_HOST)

messages = [
    {
        "role": "user",
        "content": "What time is it right now?",
    }
]

response = client.chat(
    model=OLLAMA_MODEL,
    messages=messages,
    tools=[get_current_time],
)

print("First response:")
print(response)

if response.message.tool_calls:
    for tool_call in response.message.tool_calls:
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        print(f"\nRequested tool: {tool_name}")
        print(f"Arguments: {arguments}")

        if tool_name == "get_current_time":
            tool_result = get_current_time()

            print(f"Tool result: {tool_result}")

            messages.append(response.message)

            messages.append(
                {
                    "role": "tool",
                    "content": tool_result,
                }
            )

            final_response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=[get_current_time],
            )

            print("\nFinal response:")
            print(final_response.message.content)