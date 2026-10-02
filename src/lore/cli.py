"""Thin command-line adapter for Lore application services."""
import argparse
from pathlib import Path
import sys

from . import __version__
from .archaeologist import DEFAULT_QUESTION, import_response, prepare, run_model, show
from .storage import LoreError, encode, initialize, read_json, repository


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lore", description="Local repository evidence and candidate knowledge")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Initialize local knowledge storage")
    init.add_argument("path", nargs="?", default=".")
    arch = commands.add_parser("archaeologist", help="Prepare evidence and review inferred knowledge")
    actions = arch.add_subparsers(dest="action", required=True)
    prep = actions.add_parser("prepare", help="Prepare a request without calling any model")
    prep.add_argument("path", nargs="?", default=".")
    prep.add_argument("--question", default=DEFAULT_QUESTION)
    prep.add_argument("--include", action="append", default=[], help="Repeatable repository-relative glob")
    prep.add_argument("--include-untracked", action="store_true")
    prep.add_argument("--max-files", type=int, default=40)
    prep.add_argument("--max-file-bytes", type=int, default=24000)
    prep.add_argument("--max-bytes", type=int, default=120000)
    imp = actions.add_parser("import", help="Validate and save candidate findings")
    imp.add_argument("path", nargs="?", default=".")
    imp.add_argument("--run", required=True)
    imp.add_argument("--response", type=Path, required=True)
    report = actions.add_parser("show", help="Render imported candidates as Markdown")
    report.add_argument("path", nargs="?", default=".")
    report.add_argument("--run", required=True)
    run = actions.add_parser("run", help="Send a prepared bundle to a BYOK model (uses API budget)")
    run.add_argument("path", nargs="?", default=".")
    run.add_argument("--run", required=True)
    run.add_argument("--model", required=True)
    run.add_argument("--base-url", default="https://api.openai.com/v1")
    run.add_argument("--max-output-tokens", type=int, default=4000)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = {"path": str(initialize(repository(args.path)))}
        elif args.action == "prepare":
            result = prepare(args.path, args.question, includes=args.include,
                             include_untracked=args.include_untracked, max_files=args.max_files,
                             max_file_bytes=args.max_file_bytes, max_bytes=args.max_bytes)
        elif args.action == "import":
            result = import_response(args.path, args.run, read_json(args.response))
        elif args.action == "run":
            result = run_model(args.path, args.run, model=args.model, base_url=args.base_url,
                               max_output_tokens=args.max_output_tokens)
        else:
            print(show(args.path, args.run), end="")
            return 0
        print(encode(result), end="")
        return 0
    except (LoreError, OSError, UnicodeError) as error:
        print(f"lore: {error}", file=sys.stderr)
        return 1
