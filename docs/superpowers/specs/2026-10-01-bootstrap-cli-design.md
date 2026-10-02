# Bootstrap CLI design

Status: implemented with the scope adjustments below, under the user's explicit instruction to build independently overnight. This records delegated implementation choices, not a claim of individual human review.
Date: 2026-10-01.
Sources: [bootstrap source record](../../bootstrap-sources.md), [knowledge principles](../../../.lore/knowledge/principles.md).

## Intended outcome

Seed Lore's own knowledge and run one end-to-end Archaeologist experiment without requiring API usage. The maintainer starts in Codex UI, while Lore retains ownership of evidence and knowledge artifacts. A fresh session should be able to continue from files alone.

## Options

1. **External reasoning first (recommended).** Lore prepares a bounded evidence request; a human or coding agent supplies the response; Lore validates and stores candidates. No API credentials are needed. The tradeoff is a manual handoff.
2. **BYOK first.** Implement a direct OpenAI adapter immediately. This automates inference but spends API budget before the evidence and output contracts are proven.
3. **ChatGPT plan adapter first.** Evaluate the official sign-in integration for eligible plan usage. It addresses the budget constraint but adds authentication work and an untested external dependency to the first experiment.

Keep the first path usable independently. Later adapters can automate its reasoning boundary without changing the knowledge model. Do not build three execution backends now.

## Initial design and implemented scope

Use Python with a standard-library CLI and JSON interchange. This is a new implementation recommendation, not a language decision recovered from the handover. Python's AST makes one narrow dependency-analysis experiment inexpensive. Start with one installable package whose modules express the boundaries; split distributions only when needed.

Initial command design:

- `lore init [path]`: create local Lore directories without overwriting existing knowledge.
- `lore archaeologist prepare [path] --question "..." --include "src/**/*.py"`: collect a bounded source and Python import evidence bundle and a portable reasoning request.
- `lore archaeologist import [path] --run <id> --response result.json`: validate an externally produced response against that run and save candidate knowledge.

Prepare and import are implemented, together with show and optional BYOK run. See ../../quickstart.md for executable examples. Ask/context resolution and automated promotion remain deferred.

## Flow and contracts

1. Locate the repository and select tracked source files matching the include scope; include untracked files only with an explicit flag. Never execute analyzed code.
2. Read regular UTF-8 files only; skip symlinks, ignored files, unsupported encodings, and oversized files with reported reasons. Use sorted paths and explicit file/total-byte limits.
3. Extract import sites with Python AST. Include repository-relative paths, line ranges, and source-content hashes. Label syntax failures and partial coverage. Imports are static evidence, not proof of runtime behavior.
4. Write a versioned run bundle under `.lore/runs/<id>/`: evidence JSON and a Markdown request containing the question, evidence, output schema, and instructions to preserve uncertainty. Do not include all project knowledge or the whole repository.
5. The Codex session reads the request and writes a response JSON file. Lore does not launch Codex or read its credentials.
6. Validate schema version, run identity, nonempty statements, scope, evidence references, source hashes, and line ranges before writing candidates. Every candidate needs evidence and an uncertainty explanation; an empty candidate list is valid.
7. Save each validated result under a run-specific candidate path. Repeating an identical import is idempotent; conflicting content fails rather than overwriting. Nothing becomes accepted knowledge automatically.

Separate evidence collection, request rendering, response validation, and persistence from CLI argument parsing. External reasoning is a file exchange, not a fake synchronous model provider.

## Errors and persistence

Malformed responses, stale evidence, nonexistent citations, invalid repository paths, and conflicting imports exit nonzero with actionable diagnostics and no partial candidate writes. Stage writes and replace atomically where appropriate.

Run bundles can contain source-derived data and remain local/ignored by default. Seed knowledge is tracked. Users deliberately select any experiment artifacts to publish; init must not erase their existing ignore rules or files.

## Acceptance criteria

- Init is safe to repeat and preserves user-authored seed knowledge.
- Prepare produces reproducible evidence from the same inputs, with omitted files and coverage limitations visible.
- On a small fixture with inward imports and one counterexample, the request exposes both.
- The valid response imports with traceable evidence and candidate status.
- Invalid, stale, conflicting, and path-escaping input fails without corrupting state.
- The entire prepare → external response → import workflow works without an API key or network call.
- Run the CLI on Lore once implementation contains analyzable code; do not present the handwritten seed as independently inferred knowledge.

## Deferred

ChatGPT sign-in, additional language parsers, compiler/planner implementations, conflict resolution, HTTP/MCP, database indexing, automatic promotion, SaaS, and verification products.


## Scope adjustments during authorized implementation

The user requested an independently built Archaeologist usable on a real repository tomorrow. Include bounded source excerpts for common languages, retaining Python AST import extraction as the only language-specific analyzer. Add a small optional Responses API BYOK adapter now; it is never selected implicitly. Both paths import through the same validator. No live API calls were made during development.

The chosen module layout is one Python package under src/lore, with separate ingestion, storage, schema, application, CLI, and provider files. Avoid separate distributions before their boundaries are proven. Record implementation choices in .lore/knowledge/bootstrap-decisions.md.
