"""Entrypoint CLI."""
import argparse
import os
import sys

from lore.providers import ProviderError, create_provider
from lore.file_system import FileSearcher
from lore.analyzer import FileAnalyzer

PROVIDER = "openrouter"
DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning:free"

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lore", description="Lore learning sandbox")
    commands = parser.add_subparsers(dest="command", required=True)


    analyze = commands.add_parser("analyze", help="Analyze a directory of source code.")
    analyze.add_argument("path")
    analyze.add_argument("--suffix", default=None, nargs="*")
    analyze.add_argument("--model", default=DEFAULT_MODEL)

    config = {}

    args = parser.parse_args(argv)
    if args.suffix:
        config["suffixes"] = args.suffix

    provider = create_provider(PROVIDER, args.model)
    file_searcher = FileSearcher(args.path, **config)
    analyzer = FileAnalyzer(provider=provider, file_searcher=file_searcher)
    analyzer.analyze()
