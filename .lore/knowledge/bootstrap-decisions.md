# Bootstrap implementation decisions

Recorded: 2026-10-01.
Authority: delegated implementation choices under the user's instruction to build the minimum independently so it can bootstrap itself and be tried on a real repository the next day. Implemented, not individually human-reviewed.
Sources: current Codex bootstrap conversation; [design](../../docs/superpowers/specs/2026-10-01-bootstrap-cli-design.md); [plan](../../docs/superpowers/plans/2026-10-01-archaeologist.md); source and tests named below.

These records are Lore's initial natural-language knowledge format: stable ID, status, scope, statement, rationale, provenance, and limitations. The JSON candidate exchange format is separate and experimental.

## K-014 — Python package with no runtime dependencies

Status: implemented decision. Scope: repository/build.
Statement: Use Python 3.11+ and a single installable `lore-knowledge` package exposing `lore`; keep module responsibilities separate inside `src/lore`.
Rationale: Standard-library AST, Git subprocesses, JSON, argparse, and HTTP are sufficient for this experiment. Separate packages would add release/build work without demonstrated benefit.
Source: pyproject.toml; src/lore. The prior handover's Python examples did not mandate this language.
Revisit: when another runtime or independently distributed component has a concrete benefit. No package has been published; license selection remains a maintainer decision.

## K-015 — External reasoning is the default bootstrap path

Status: implemented decision. Scope: Archaeologist execution.
Statement: `prepare` and `import` work without network calls or API keys. An existing Codex session can supply reasoning as a portable JSON response.
Rationale: Make use of the maintainer's available subscription usage while preserving agent independence. Lore never launches Codex or reads its credentials.
Source: explicit user budget constraint; src/lore/archaeologist.py; docs/quickstart.md.
Limitation: manual handoff until an integration proves necessary.

## K-016 — Small, explicit BYOK option

Status: implemented decision. Scope: model inference.
Statement: `run` requires an explicit model and OPENAI_API_KEY, uses the Responses API structured-output contract, and validates results through the external import path.
Rationale: Keep a standalone automated experiment available without making paid inference mandatory. No implicit provider fallback or automatic retry. Preflight stale source and existing output before spending; check freshness again after inference.
Source: src/lore/provider.py; src/lore/archaeologist.py; tests/test_provider.py; code-review findings.
Limitations: local HTTP contract tests only; no live paid endpoint validation. Custom gateways must support Responses structured outputs. ChatGPT plan sign-in is deferred.

## K-017 — Bounded working-tree evidence

Status: implemented decision. Scope: ingestion.
Statement: Read sorted, nonignored tracked source files at the Git repository root, with opt-in untracked files and explicit include patterns. Default to 40 files, 24,000 bytes/file, and 120,000 source bytes total; report omissions.
Rationale: Make collection predictable and reviewable before spending context. Snapshot working-tree bytes, not only committed code.
Source: src/lore/ingestion.py; tests/test_cli.py.
Limitations: selection is lexical rather than question-ranked. Globs use documented fnmatch semantics. This is not a secret detector. Symlinks, dependency/build directories, binary data, and unsupported encodings are excluded.

## K-018 — Honest language coverage

Status: implemented decision. Scope: analyzers.
Statement: Extract Python imports with AST; include source excerpts for other supported languages without pretending to parse their architecture.
Rationale: Permit tomorrow's real-repository trial, including TypeScript, without building a parser platform. Never execute source code.
Source: src/lore/ingestion.py; CLI tests with Python and TypeScript.
Limitation: static evidence cannot establish runtime dependencies or intended policy. Python parse failures retain source evidence and report a warning.

## K-019 — Immutable run identity and provenance

Status: implemented decision. Scope: evidence and import.
Statement: Identify each run by a truncated SHA-256 of its question, evidence, coverage, and Git revision. Evidence records retain paths, line ranges, content hashes, and source text. Validate all selected source hashes on import.
Rationale: Keep reasoning tied to a concrete snapshot and detect stale or accidentally edited evidence bundles. Identical inputs are idempotent.
Source: src/lore/archaeologist.py; tests/test_cli.py.
Limitations: hashes provide integrity checks, not signatures or semantic truth. New files outside the prepared selection do not invalidate existing evidence; coverage is limited to the selected snapshot.

## K-020 — Candidate status cannot be supplied by the model

Status: implemented decision. Scope: knowledge lifecycle.
Statement: Responses supply statements, kind, scope, rationale, uncertainty, evidence IDs, and exceptions; Lore assigns candidate status. Even a proposed decision remains a candidate.
Rationale: Prevent inferred patterns from silently becoming accepted policy. An empty candidate array is valid. Human review and manual knowledge edits close the initial loop.
Source: src/lore/schema.py; src/lore/archaeologist.py; tests/test_cli.py.
Limitation: validation checks structure and citations, not correctness, entailment, duplication, or conflicts. Automated reconciliation and promotion are deferred.

## K-021 — Preserve artifacts and keep generated source data local

Status: implemented decision. Scope: persistence.
Statement: Atomically publish individual artifacts without overwriting conflicting content. Reject path escapes and symlinked state. Ignore generated runs/candidates while tracking deliberately authored knowledge. Preserve existing knowledge and ignore rules.
Rationale: Protect hand-authored records and avoid accidental publication of source-derived bundles.
Source: src/lore/storage.py; tests/test_cli.py.
Limitations: this is a local cooperative workflow, not hardened isolation from an attacker concurrently changing the filesystem. A multi-file prepare interrupted mid-write can be resumed by repeating it.

## K-022 — Validate the complete workflow without paid calls

Status: implemented decision. Scope: evaluation.
Statement: Use temporary Git repositories and a local HTTP fixture, then run prepare → external reasoning → import → show on Lore itself.
Rationale: Exercise the actual CLI and persistence contracts while avoiding API spend. A self-analysis should acknowledge limitations in Lore's own code.
Source: tests; docs/experiments/001-self-archaeology.md.
Limitation: a successful self-analysis does not prove better agent outcomes. E-003 comparative evaluation remains unperformed.
