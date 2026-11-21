"""Small CLI demo for the AI Agent Kit for Shops.

Run it and type customer messages, the agent replies:

    python3 chat.py

Replay the fixed test conversation from demo_conversation.txt:

    python3 chat.py --script

Try the optional NVIDIA NIM backend (needs NVIDIA_API_KEY set):

    NVIDIA_API_KEY=nvapi-... python3 chat.py --ai

Without a key, or when the AI call fails, the agent answers with the
offline rules engine and says so. No key is ever read from a file.
"""

import argparse
import os
import sys

from agent import ShopAgent


def run_script(agent):
    """Replay demo_conversation.txt and print the whole exchange."""
    with open("demo_conversation.txt", "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    for line in lines:
        if line.startswith("Customer:"):
            message = line[len("Customer:"):].strip()
            print("Customer: " + message)
            print("Agent: " + agent.respond(message))
            print()


def run_interactive(agent):
    """Live chat loop. Type 'quit' or 'exit' to stop."""
    print("Shop Agent demo. Type your message, or 'quit' to stop.\n")
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if message.lower() in ("quit", "exit"):
            print("Agent: Thank you for visiting. Allah Hafiz!")
            break
        print("Agent: " + agent.respond(message) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Shop Agent demo chat")
    parser.add_argument("--script", action="store_true",
                        help="Replay demo_conversation.txt")
    parser.add_argument("--ai", action="store_true",
                        help="Try the NVIDIA NIM backend first (needs NVIDIA_API_KEY)")
    parser.add_argument("--shop", default="shop.json",
                        help="Path to the shop data file")
    args = parser.parse_args()

    if args.ai and not os.environ.get("NVIDIA_API_KEY"):
        print("Note: --ai was given but NVIDIA_API_KEY is not set, "
              "so the agent will answer with the offline rules engine.")
    elif args.ai:
        print("Note: NVIDIA NIM backend is on. If an AI call fails, "
              "the agent falls back to the offline rules engine.")

    agent = ShopAgent(shop_path=args.shop, use_ai=args.ai)
    if args.script:
        run_script(agent)
    else:
        run_interactive(agent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
