import os

from dotenv import load_dotenv
from ollama import Client


load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")


def main() -> None:
    print(f"Connecting to Ollama at: {OLLAMA_HOST}")
    print(f"Using model: {OLLAMA_MODEL}")
    print("\nType 'exit' to quit.\n")

    client = Client(host=OLLAMA_HOST)

    messages = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=messages,
        )

        assistant_message = response.message.content

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message,
            }
        )

        print(f"\nAgent: {assistant_message}\n")


if __name__ == "__main__":
    main()