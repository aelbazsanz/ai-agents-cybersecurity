import os

from ollama import Client


def main() -> None:
    ollama_host = os.environ["OLLAMA_HOST"]
    ollama_model = os.environ["OLLAMA_MODEL"]

    client = Client(host=ollama_host)

    response = client.chat(
        model=ollama_model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Ollama connection successful.",
            }
        ],
    )

    print(response.message.content)


if __name__ == "__main__":
    main()