# Durable principles

Status: seed records distilled from the adopted handover unless explicitly marked otherwise.
Scope: project.
Sources: [source record](../../docs/bootstrap-sources.md). IDs below are local bootstrap identifiers, not a finalized schema.

| ID | Statement | Rationale / source |
| --- | --- | --- |
| K-001 | Keep knowledge independent of an agent or vendor. | Knowledge belongs to the project/team. README §6. |
| K-002 | Agents call Lore; Lore must not fundamentally depend on agent harnesses. | Preserve ownership of evidence, prompts, provenance, and reconciliation. README §§18–19. |
| K-003 | Start with a local CLI over application APIs. | Exercise local workflows while retaining future HTTP/MCP options. README §20. |
| K-004 | Retain BYOK as the standalone model-access direction. | Users can select their approved provider; avoid a required Lore service. README §§18, 21. |
| K-005 | Start automated ingestion with repository code. | Validate a narrow useful loop before adding external systems. README §8. |
| K-006 | Defer verification platforms, SaaS, IDEs, and automatic regeneration. | These are downstream possibilities. README §26. |
| K-007 | Prefer natural language plus lightweight metadata. | Let experiments drive the schema. README §§15–16. |
| K-008 | Collect evidence deterministically where practical before model reasoning. | Reduce exploration cost and provide traceable sources. README §11. |
| K-009 | Do not promote observed frequency into intended policy. | Existing code can contain accidents, legacy behavior, and exceptions. README §10. |
| K-010 | Resolve relevant context rather than dumping the knowledge base. | Keep agent context useful and bounded. README §14. |
| K-011 | Use a public exploratory repository and keep the local core portable. | Explicit user choice supersedes the earlier private-first suggestion. Source exchange d6428b1b. |
| K-012 | Preserve durable knowledge discovered while building Lore. | Lore should become its own first test repository. Source exchange dd82229b. |
| K-013 | Account for greater available ChatGPT Pro usage than API usage during bootstrap. | Explicit constraint in the current Codex request; external reasoning is a proposed way to satisfy it. |

When new development teaches us something, record its statement, scope, rationale, source, and whether it is observed, proposed, or accepted. Do not silently generalize a local correction or erase a superseded decision's rationale.
