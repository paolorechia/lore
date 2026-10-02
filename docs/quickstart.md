# Try the Archaeologist

Requires Python 3.11+ and Git. No API key is needed for the default workflow.

## Install locally

From the Lore checkout:

```sh
uv venv .venv
uv pip install --python .venv/bin/python -e .
.venv/bin/lore --help
```

Without uv: `python3 -m venv .venv`, then `.venv/bin/python -m pip install -e .`.
For a command available from other directories, optionally install with `uv tool install --editable /absolute/path/to/lore`; this installs the `lore` executable. The package is named `lore-knowledge`, but is not published to a package index.

## 1. Prepare a small real-repository question

Run from Lore's checkout, substituting a Git repository root and its source layout:

```sh
.venv/bin/lore archaeologist prepare /path/to/repo \
  --include 'src/**/*.ts' --include 'src/**/*.tsx' \
  --question 'How are recoverable errors handled in these files? Cite patterns and counterexamples.'
```

Use `--include 'src/**/*.py'` for Python, or omit includes to select supported source files across the repository. Quote globs so Lore receives them. Patterns are matched against repository-relative paths; `**/` also matches zero directories, and `*` can span slashes. Repeated includes are ORed.

Default limits: 40 files, 24,000 bytes per file, 120,000 source bytes total. Increase with `--max-files`, `--max-file-bytes`, and `--max-bytes`, or narrow the question/scope. Selection is sorted, not ranked by question relevance. Files exceeding a budget are omitted, never silently truncated. The request can be larger than source bytes due to JSON and import evidence.

Only tracked, nonignored source is included by default. `--include-untracked` also includes new nonignored source. `.lore`, dependency/build directories, symlinks, empty files, and binary/non-UTF-8 files are excluded. Ignored files are excluded even if tracked. This is not a secret scanner: inspect the prepared request before sharing it with any model.

Python imports are parsed with AST. TypeScript/JavaScript, Go, Rust, Java, Kotlin, Swift, Ruby, PHP, C/C++/C#, shell, SQL, Vue, and Svelte contribute bounded source excerpts. Lore does not yet parse their dependency graphs or resolve runtime imports.

The command initializes `.lore` if needed and prints JSON containing:

- `run_id`: use this exact value in later commands.
- `path`: local run directory containing `request.md`, `evidence.json`, and `response.schema.json`.
- `included_files`, `skipped_files`, and `request_bytes`: inspect scope and size before reasoning.

Inspect `coverage` in `evidence.json` for omissions and parser warnings. No selected evidence is an error; narrow globs or budgets may need adjustment.

## 2. Reason in your existing Codex session

Open the target repository in Codex and ask:

> Read `.lore/runs/RUN_ID/request.md`. Answer its question using only its evidence and schema. Save the JSON response as `.lore/runs/RUN_ID/response.json`. Preserve exceptions and uncertainty; do not modify source files or promote findings to accepted knowledge.

Replace `RUN_ID` with the actual ID. The request is also portable text that can be supplied to another model. Lore does not launch an agent or require subscription credentials. This path uses whichever inference environment you choose, with no API request from Lore.

## 3. Import and review

```sh
.venv/bin/lore archaeologist import /path/to/repo \
  --run RUN_ID --response /path/to/repo/.lore/runs/RUN_ID/response.json
.venv/bin/lore archaeologist show /path/to/repo --run RUN_ID
```

Findings are stored as JSON in `.lore/candidates/RUN_ID.json`. `show` prints readable Markdown with evidence locations, hashes, rationale, uncertainty, and exceptions. Citation validation does not prove a finding is true. Review it and manually record accepted knowledge under `.lore/knowledge/`, including its source and rationale.

Repeated identical imports are safe. Conflicting results do not overwrite previous candidates. Source edits invalidate the prepared snapshot, even if the edited file is not cited by a candidate. Prepare a new run after changing source. The run ID depends on question, evidence, coverage, and Git revision. Change the question for a deliberate alternative reasoning experiment.

`.lore/runs` and `.lore/candidates` are ignored by generated `.lore/.gitignore` rules. Existing `.gitignore` and knowledge files are preserved. Deliberately curate findings before committing them. There is no automatic acceptance, reconciliation, or Planner yet.

## Optional: standalone BYOK inference

After inspecting a prepared run:

```sh
export OPENAI_API_KEY='your-key'
.venv/bin/lore archaeologist run /path/to/repo \
  --run RUN_ID --model YOUR_MODEL --max-output-tokens 4000
```

This explicitly sends the selected evidence to the model and uses API budget. There is no fallback from the no-API path. Supply a model available to your account that supports Responses API structured outputs. `--base-url https://your-gateway/v1` supports gateways implementing that API; generic Chat Completions-only compatibility is insufficient. HTTPS is required except for loopback testing. Redirects are refused.

The adapter uses `store: false`, a 120-second timeout, and no automatic retries. Refusals, incomplete outputs, HTTP errors, and malformed responses fail visibly. A received JSON result is saved locally as `model-response.json` before import validation. If it needs correction, use `import --response` rather than making another paid call. A run with existing candidates or a saved model response refuses another model call. Stale sources are checked before and after inference.

The provider adapter was tested against a local HTTP fixture, not a live paid endpoint. BYOK authentication does not use ChatGPT subscription allowance. ChatGPT sign-in integration is deferred.

## Development checks

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Tests use temporary Git repositories and a loopback HTTP fixture; no paid API calls are made.
