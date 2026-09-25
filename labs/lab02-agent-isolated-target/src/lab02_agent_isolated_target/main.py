from lab02_agent_isolated_target.agent import Agent


def main() -> None:
    agent = Agent()

    print("Lab 02 Agent")
    print("Type 'exit' or 'quit' to stop.")
    print()

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in {"exit", "quit"}:
            break

        if not user_input:
            continue

        try:
            response = agent.run(user_input)
            print(f"\n{response}\n")
        except Exception as exc:
            print(f"\n[ERROR] {exc}\n")


if __name__ == "__main__":
    main()