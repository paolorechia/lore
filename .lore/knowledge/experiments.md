# Experiments

Status: E-001 has an initial technical self-analysis; E-002 and E-003 are planned.
Scope: project.
Sources: [source record](../../docs/bootstrap-sources.md), README sections 23–25 and 30.

## E-001: Archaeologist

Choose one narrow question on a small repository: infer dependency boundaries or error-handling conventions. Collect deterministic evidence and return candidate knowledge with citations, uncertainty, and exceptions.

Review correctness, usefulness to a fresh agent, confusion between frequency and intent, missing evidence, and representation weaknesses. Include counterexamples and allow an empty result when evidence is insufficient.

Initial result: [self-analysis record](../../docs/experiments/001-self-archaeology.md). The workflow completed without API usage and produced three candidates. Semantic usefulness and comparative improvement remain unproven.

## E-002: Decision Compiler

Use real development corrections to propose durable knowledge changes. Human review evaluates local versus general scope, duplicates, conflicts, exceptions, supersession, and temporary instructions. Manual seed capture during bootstrap is not an implementation of this tool.

## E-003: Planner and dogfooding

Compare fresh agents on the same task and repository revision, with and without Lore-resolved knowledge. Keep model and task conditions comparable. Record supplied context, corrections, repeated mistakes, time to acceptable implementation, and context usage.

Use Lore's own development as a source of examples. Log what knowledge influenced a task and what new knowledge emerged. If resolved knowledge does not improve outcomes, revisit the hypothesis.

Do not treat the illustrative numerical confidence scores in the handover as calibrated measurements.
