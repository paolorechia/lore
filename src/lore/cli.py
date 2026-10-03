"""A one-prompt smoke test, before adding an agent loop or repository tools."""
import argparse
import os
import sys

from lore.providers import ProviderError, create_provider


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lore", description="Lore learning sandbox")
    commands = parser.add_subparsers(dest="command", required=True)
    hello = commands.add_parser("hello", help="Send one prompt to a model and print its response")
    hello.add_argument("prompt", nargs="?", default="Say hello in one short sentence.")
    hello.add_argument("--provider", default=os.environ.get("LORE_PROVIDER", "openrouter"))
    hello.add_argument("--model", default=os.environ.get("LORE_MODEL", ""))
    args = parser.parse_args(argv)
    if not args.prompt.strip():
        parser.error("prompt must not be empty")
    try:
        provider = create_provider(args.provider, args.model)
        print(provider.generate(args.prompt))
    except ProviderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    return 0
