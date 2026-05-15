"""CLI for the AI Guess-The-Word game host."""

from game_engine import GameEngine


def main() -> None:
    engine = GameEngine()
    print("=== Guess The Word (AI Host) ===")
    print("Dynamic hints powered by Google Gemini.")
    print("Commands: 'new game', 'give up', 'exit'\n")

    try:
        print(f"Bot: {engine.new_game()}\n")
    except KeyboardInterrupt:
        print("\nBye!")
        return

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if user_input.strip().lower() == "exit":
            print("Bye!")
            break

        reply = engine.process_input(user_input)
        print(f"\nBot: {reply}\n")


if __name__ == "__main__":
    main()
