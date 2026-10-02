# Archaeologist implementation plan

Goal: a standalone, installable local Archaeologist for tomorrow's real-repository trial.
Execution: native, under the user's explicit instruction to continue independently overnight.
Spec: ../specs/2026-10-01-bootstrap-cli-design.md

User direction authorizes implementation choices and documentation without further review gates. Keep changes in this checkout so the Codex UI sees the result.

## Tasks

- [x] Write CLI integration tests using temporary Git repositories: init preservation, bounded evidence, ignored and unsafe paths, portable requests, valid/invalid/stale response import, idempotency, and readable output.
- [x] Implement Python package: storage helpers, deterministic ingestion, evidence/request schema, Archaeologist application service, thin argparse CLI.
- [x] Add optional explicit BYOK execution using the Responses API, with local HTTP integration tests and no live paid calls.
- [x] Exercise prepare → reason in this Codex session → import on Lore itself. Preserve candidate uncertainty.
- [x] Record implementation choices as scoped Lore knowledge, update quickstart/spec/AGENTS, and verify installation, complete tests, and clean diffs.

## Practical scope adjustments

Include bounded source excerpts for common code languages as well as Python AST import evidence. This allows a real TypeScript repository trial without claiming full AST analysis of all languages. Default to tracked source files, with explicit --include-untracked for new code. All reasoning results use the same validated import path. BYOK is optional and requires an explicit model; never fall back to paid inference.

## Review focus

Path traversal and symlinked state; stale citations after source edits; ignored or oversized source; empty evidence and exhausted budgets; provider refusal/incomplete/error responses. Tests must exercise these boundaries against filesystem or HTTP fixtures.


## Execution record

Initial CLI tests failed because the executable did not exist, then passed after implementation. Provider tests failed before the adapter existed, then passed against a loopback HTTP server. Independent review found two avoidable-spend issues: stale evidence checked only after inference, and retrying when a saved response already existed. A regression test reproduced the issue, and both paths now fail before provider execution. Post-inference validation remains in place.

Scope rulings: use one package; allow common-language source excerpts; add optional BYOK with explicit model selection; remain in the user's checkout; do not publish, push, or make paid model calls. These choices are captured in K-014 through K-022. The installed CLI completed self-analysis; see docs/experiments/001-self-archaeology.md.
