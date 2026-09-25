# imports
import os
from lab02_agent_isolated_target.agent import main

if __name__ == "__main__":
    main()

# LLM parameters
def main() -> None:
    ollama_host = os.environ["OLLAMA_HOST"]
    ollama_model = os.environ["OLLAMA_MODEL"]
    target_host = os.environ["TARGET_HOST"]

    print(f"OLLAMA_HOST={ollama_host}")
    print(f"OLLAMA_MODEL={ollama_model}")
    print(f"TARGET_HOST={target_host}")


if __name__ == "__main__":
    main()