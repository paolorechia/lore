# System boundaries

Status: bootstrap architecture. Ingestion, candidate validation/storage, Archaeologist, CLI, and an optional BYOK adapter are implemented. Decision Compiler, Planner, HTTP, and MCP remain planned.
Scope: project.
Sources: [source record](../../docs/bootstrap-sources.md), README sections 8–20.

| Component | Responsibility | Boundary |
| --- | --- | --- |
| Ingestion | Collect evidence from sources; initially repository code. | Prefer deterministic analysis before inference. |
| Knowledge core | Represent knowledge, provenance, lifecycle, reconciliation, and retrieval. | Own knowledge independently of an agent harness. |
| Archaeologist | Infer candidate knowledge from repository evidence. | Preserve uncertainty; frequency does not prove intent. |
| Decision Compiler | Propose durable knowledge changes from development activity. | Distinguish local fixes, duplicates, conflicts, and exceptions. |
| Planner | Resolve knowledge relevant to a task. | Produce context for the coding agent; do not implement the task. |
| AI runtime | Supply model reasoning. | BYOK direction, OpenAI first, minimal replaceable interface. |
| CLI | Expose application operations locally. | Keep core logic in callable application APIs. |
| Future HTTP/MCP interfaces | Expose the same application operations. | Defer until the local workflow proves useful. |

The dependency direction is agents → Lore. Lore must not fundamentally depend on Codex, Claude Code, or another harness.

Git-friendly local artifacts are a starting point for persistence and review, not a permanent storage mandate. Natural language with lightweight metadata precedes a formal ontology.

The handover's package layout and Python examples are illustrative; no implementation language was selected there.

## Bootstrap implementation

Prepare evidence and reasoning requests locally, let an existing Codex session return a structured result, and validate the result in Lore. The optional BYOK adapter uses the same evidence and candidate validation. See the [CLI design](../../docs/superpowers/specs/2026-10-01-bootstrap-cli-design.md) and [implementation decisions](bootstrap-decisions.md).
