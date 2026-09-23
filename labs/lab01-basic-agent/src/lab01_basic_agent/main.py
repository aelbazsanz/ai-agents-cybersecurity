import os

from dotenv import load_dotenv
from ollama import Client


load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")


def main() -> None:
    print(f"Connecting to Ollama at: {OLLAMA_HOST}")
    print(f"Using model: {OLLAMA_MODEL}")

    client = Client(host=OLLAMA_HOST)

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Explain what an AI agent is in one paragraph.",
            }
        ],
    )

    print("\nModel response:\n")
    print(response.message.content)


if __name__ == "__main__":
    main()