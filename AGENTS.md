# Working on Lore

Read [the vision](.lore/knowledge/vision.md) and [principles](.lore/knowledge/principles.md), then consult [architecture](.lore/knowledge/architecture.md) and [experiments](.lore/knowledge/experiments.md) as relevant to the task.

The README includes the recovered project brief, whose examples include future capabilities. Use docs/quickstart.md and `lore --help` for implemented commands. Check actual code before claiming a feature exists.

Keep new proposed decisions distinct from established knowledge. Capture durable human corrections with source, rationale, and scope. Use [the source record](docs/bootstrap-sources.md) to resolve provenance and superseded suggestions.

Start with a narrow Archaeologist experiment. Keep deterministic ingestion, reasoning, knowledge handling, and CLI presentation separate. Do not implement the future platform prematurely.

Respect the maintainer's bootstrap inference constraint: make local preparation and validation useful without requiring paid API calls. BYOK remains the standalone direction; external reasoning is implemented, with an optional explicitly selected BYOK command. Never silently fall back to paid inference.

Implementation: Python 3.11+, standard library runtime, one installable package under src/lore.

- Install: `uv venv .venv` then `uv pip install --python .venv/bin/python -e .`.
- Test: `.venv/bin/python -m unittest discover -s tests -v`.
- CLI: `.venv/bin/lore --help`.
- Self-analysis: `.venv/bin/lore archaeologist prepare . --include 'src/lore/*.py' --include-untracked`.

Read .lore/knowledge/bootstrap-decisions.md for implementation rationale. Tests use Git fixtures and local HTTP only. Generated runs and candidates are ignored; curate knowledge deliberately. No Planner or Decision Compiler is implemented.
