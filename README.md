# Lore

## Status

Lore is an exploratory public open-source monorepo for researching and building infrastructure for **knowledge-driven, AI-native software development**.

The project should initially optimize for learning, experimentation, and clean composable primitives rather than production completeness.

The long-term commercial direction may be open-core:

- **Lore Core:** open-source, local-first software knowledge engine.
- **Lore Platform:** future multiplayer/team/organization knowledge infrastructure.

Do not prematurely build the SaaS platform.

---

# 1. Thesis

Software systems are ultimately **knowledge systems**.

A mature software system embodies accumulated knowledge about:

- what the product should do;
- domain rules and invariants;
- architecture;
- engineering conventions;
- UX conventions;
- libraries and technology choices;
- operational behavior;
- security;
- failed approaches;
- exceptions;
- historical reasoning;
- organizational preferences.

Today, most of this knowledge is stored indirectly.

It exists in:

```text id="f8fwdw"
source code
tests
Git history
PRs
tickets
documentation
incidents
conversations
developer memory
```

Source code currently acts as a **lossy storage format for engineering knowledge**.

AI coding changes the economics of this arrangement.

If AI increasingly performs implementation, source code does not necessarily need to remain the highest-level durable representation of a software system.

Lore explores:

> Humans and teams maintain accumulated software knowledge. AI increasingly maintains its realization as code.

Conceptually:

```text id="74z1i5"
Human/team reasoning
        ↓
Software Knowledge
        ↓
AI realization
        ↓
Source code
        ↓
Compiler/runtime
        ↓
Running system
```

This moves the human abstraction one level above source code.

Source code does **not** immediately become disposable.

The research question is whether increasingly large portions of implementation can become derived artifacts as the software knowledge layer becomes richer.

---

# 2. The compiler analogy

Traditional development:

```text id="gssu7j"
human reasoning
      ↓
 source code          ← durable human artifact
      ↓
  compiler
      ↓
machine code          ← derived artifact
```

Possible AI-native development:

```text id="x6cpcy"
human/team reasoning
        ↓
software knowledge    ← durable human/team artifact
        ↓
AI realization
        ↓
source code            ← increasingly derived artifact
        ↓
compiler
        ↓
machine code
```

AI effectively becomes part of the development runtime.

Unlike traditional model-driven development, the software knowledge representation does **not** need to deterministically describe every implementation detail.

It is intentionally incomplete.

AI supplies general software-engineering knowledge.

Lore supplies the accumulated knowledge specific to **this particular software system and organization**.

---

# 3. North-star principle

For information encountered during development, ask:

> If we deleted and regenerated the implementation, would we want this information to survive?

If yes, it is a candidate for the software knowledge layer.

Examples:

```text id="f9e3ne"
"Settled invoices cannot be edited."

"Domain code cannot import infrastructure."

"Recoverable errors use ErrorBanner."

"All externally triggered mutations must be idempotent."

"We use Postgres rather than Redis here because
conditional transactional behavior is required."

"Streaming clients are exempt from the standard
HTTP retry wrapper."

"We attempted approach X in 2026 and rejected it
because it caused Y."
```

These should not disappear merely because their current implementation disappears.

---

# 4. Knowledge accumulation

The system should optimize for **knowledge accumulation**, not code generation.

Every development cycle potentially teaches the organization something:

```text id="7xxoal"
build
  ↓
observe
  ↓
human/agent feedback
  ↓
what did we learn?
  ↓
software knowledge
  ↓
future development
  ↺
```

Current AI coding workflows frequently lose this information.

For example:

```text id="rzjzm8"
Agent implements feature
        ↓
Human:
"No, errors here should use ErrorBanner."
        ↓
Agent fixes implementation
        ↓
Feature completes
        ↓
knowledge disappears
```

The implementation improved.

The software organization's knowledge did not.

Lore should eventually recognize the candidate durable knowledge:

```text id="0a5lxj"
Recoverable application errors use ErrorBanner.
```

and reconcile it with what the organization already knows.

---

# 5. Existing practical evidence

An existing AI-heavy development workflow already demonstrated a primitive version of this idea.

Before implementing:

- a new feature was logged;
- a defect was logged;
- relevant decisions were recorded in plain text.

Agents consulted this accumulated history during future work.

This produced useful behavior such as:

> This approach was already attempted in LOG-X and failed for reason Y. Are you sure you want to try it again?

Development became cumulative across agent sessions.

However, micro-decisions discovered during implementation were generally handled through manual correction and **not distilled back into the knowledge base**.

This distinction is important:

```text id="4ihvqy"
explicit feature/defect knowledge
        ↓
persisted
        ↓
compounded


implementation correction
        ↓
fixed code
        ↓
knowledge lost
```

Lore should eventually close this loop.

---

# 6. This is NOT agent memory

Do not optimize around:

> What should Claude/Codex remember?

Optimize around:

> What has this team learned about this software system?

The knowledge belongs to:

```text id="kql8bj"
project / team / organization
```

not:

```text id="slwnhv"
developer / session / agent
```

Agents are clients of the knowledge system.

Long term:

```text id="7nq0vl"
             SOFTWARE KNOWLEDGE
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
     Codex       Claude Code     Cursor
       │             │             │
       └─────────────┼─────────────┘
                     ▼
                   CODE
```

Lore should remain agent/vendor independent.

---

# 7. Multiplayer is a first principle

Software knowledge belongs to teams.

Multiple humans and agents may concurrently discover, propose, modify or invalidate knowledge.

The system must eventually support:

- shared state;
- provenance;
- authorship;
- history;
- branching;
- review;
- conflicts;
- scope;
- supersession;
- search;
- permissions;
- temporal queries;
- cross-repository knowledge.

Example:

```text id="65fp6x"
Developer A + Agent A ──┐
                        │
Developer B + Agent B ──┼──► SOFTWARE KNOWLEDGE
                        │
Developer C + Agent C ──┤
                        │
CI / incidents ─────────┘
```

Git is a reasonable initial persistence mechanism because it provides:

- history;
- branching;
- distribution;
- authorship;
- review;
- offline operation;
- temporal alignment between code and knowledge.

Do not assume Git must remain the final storage architecture.

---

# 8. Long-term architecture

Potential sources:

```text id="ofq3w1"
code
Git
PRs
reviews
Jira
Linear
Confluence
Notion
incidents
agent sessions
human conversations
tests
documentation
```

All feed an ingestion layer:

```text id="x4f2t5"
                 SOURCES

       code / Git / PRs / Jira / docs
       incidents / conversations / humans
                        │
                        ▼
                   INGESTION
                        │
                        ▼
                 KNOWLEDGE CORE
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
         extract     reconcile     resolve
            │           │           │
            └───────────┼───────────┘
                        ▼
                  AGENT INTERFACE
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
         Codex      Claude Code    Cursor
                        │
                        ▼
                      CODE
```

However:

> **v0 starts with code as the only ingestion source.**

Do not implement Jira, Confluence, GitHub, etc. yet.

The ingestion architecture should merely allow these sources later.

---

# 9. Initial tools

Build independent tools around shared primitives.

Initial focus:

1. Archaeologist
2. Decision Compiler
3. Knowledge-Aware Planner

These should eventually compose through the same knowledge core.

---

# 10. Tool 1 — Archaeologist

## Question

> What does this team appear to know?

Input:

```text id="cuy2g9"
existing repository
```

Output:

```text id="s4yr90"
inferred software knowledge
+
evidence
+
provenance
+
confidence
```

The Archaeologist should NOT merely summarize a repository.

It attempts to recover:

- decisions;
- conventions;
- constraints;
- patterns;
- architecture;
- product consistency;
- domain knowledge;

that are implicit in implementation.

Example:

```text id="cm8b1j"
ARCHITECTURE

A-17 [high confidence]

Domain modules do not depend on persistence.

Evidence:
- dependency graph consistently points inward
- 27 modules conform
- repository interfaces isolate persistence

Possible violation:
- legacy/importer.py
```

Another:

```text id="qqs7da"
EXPERIENCE

UX-12 [high confidence]

Recoverable form errors use ErrorBanner.

Evidence:
- 41 current usages
- shared ErrorBanner component exists

Possible exceptions:
- authentication expiration
```

## Critical distinction

Frequency does not automatically imply intent.

This:

```text id="n7mhy7"
OBSERVATION

47/51 forms use ErrorBanner.
```

does not automatically imply:

```text id="7vb5x8"
DECISION

All forms must use ErrorBanner.
```

The system must preserve uncertainty.

---

# 11. Repository Evidence

Do not make the LLM blindly explore repositories if deterministic tooling can collect useful evidence first.

Prefer:

```text id="krbhcm"
                 Repository
                     │
          ┌──────────┼───────────┐
          ▼          ▼           ▼
         AST       Git         search
          │          │           │
          └──────────┼───────────┘
                     ▼
             Repository Evidence
                     │
                     ▼
                    LLM
                     │
                     ▼
             Candidate Knowledge
```

Possible deterministic evidence:

- file structure;
- imports;
- dependency graph;
- symbols;
- call relationships;
- inheritance;
- repeated component usage;
- configuration;
- tests;
- Git history;
- textual search;
- framework metadata.

This has two advantages:

1. reduces unnecessary LLM exploration;
2. creates explicit provenance for inferred knowledge.

The model should reason over evidence rather than merely claim:

> I looked around and noticed X.

---

# 12. Tool 2 — Decision Compiler

## Question

> What did we learn during this development activity?

Eventually inputs may include:

- agent sessions;
- human corrections;
- PR discussions;
- diffs;
- reviews;
- incidents;
- explicit decisions.

Initial implementations may accept plain text/session/change input.

Example:

```text id="j2nkv4"
Human:

No, don't show a modal here.
Use ErrorBanner like the other settings forms.
```

Candidate output:

```text id="ifppgv"
CANDIDATE KNOWLEDGE

Statement:
Recoverable errors in settings forms use ErrorBanner.

Kind:
Convention

Scope:
web/settings/forms

Source:
Human correction

Status:
Candidate
```

The Decision Compiler eventually performs:

```text id="z5lt88"
extract
   ↓
compare with existing knowledge
   ↓
duplicate?
conflict?
exception?
supersedes?
narrower scope?
generalization?
   ↓
candidate knowledge change
```

This is:

> development activity → software knowledge changes

not:

> conversation → summary

---

# 13. Tool 3 — Knowledge-Aware Planner

## Question

> What accumulated knowledge matters before implementing this change?

Input:

```text id="bop9r7"
task
+
software knowledge
+
repository evidence
```

Example:

```text id="0b12yd"
Add bulk account deletion.
```

Potential output:

```text id="5eyz2r"
RELEVANT KNOWLEDGE

K-18
Destructive actions require confirmation.

K-31
Mutations produce audit events.

K-82
Bulk operations permit partial success.

K-91
Recoverable failures use ErrorBanner.


HISTORICAL CONTEXT

LOG-281
Batch transaction implementation was previously attempted.
Rejected because ...


LIKELY IMPACT

- Accounts domain
- Admin API
- Audit system
- Admin frontend


UNRESOLVED KNOWLEDGE

Retention behavior following account deletion is unspecified.

HUMAN DECISION MAY BE REQUIRED.
```

The Planner should produce a **high-signal context package** suitable for any coding agent.

It should not implement the feature itself.

---

# 14. Context resolution

Never solve the knowledge problem by dumping the entire knowledge base into an LLM context window.

Resolve applicable knowledge.

```text id="3ak35n"
Task
 ↓
Knowledge Resolver
 ↓
relevant domain knowledge
relevant architecture
relevant conventions
relevant history
relevant exceptions
 ↓
Agent context
```

Potential future scope hierarchy:

```text id="3wm77r"
organization
    ↓
project
    ↓
subsystem
    ↓
directory/component
    ↓
task
```

Narrower knowledge may specialize or override broader knowledge.

This resembles a cascade of engineering knowledge.

---

# 15. Knowledge lifecycle

Tentative:

```text id="x57s05"
OBSERVE
   ↓
EXTRACT
   ↓
CANDIDATE
   ↓
RECONCILE
   ↓
PROMOTE
   ↓
ACTIVE KNOWLEDGE
   ↓
APPLY
   ↓
OBSERVE
   ↺
```

Potential states:

```text id="d29qsi"
observation
candidate
accepted
deprecated
superseded
rejected
```

Do not lock this schema prematurely.

---

# 16. Knowledge is broader than decisions

"Decision" is useful but probably too narrow.

Potential knowledge primitives include:

```text id="2e6o5r"
DECISION
"We use Postgres."

CONSTRAINT
"Domain cannot depend on infrastructure."

CONVENTION
"Recoverable errors use ErrorBanner."

INVARIANT
"Settled invoices are immutable."

PREFERENCE
"Prefer existing design-system components."

RATIONALE
"Polling is used because provider X has no webhooks."

EXCEPTION
"Authentication failures may interrupt the workflow."

LEARNING
"Retrying this operation caused duplicate bookings."

OBSERVATION
"47/51 forms currently use ErrorBanner."
```

Treat this as a hypothesis.

Do NOT design an elaborate ontology before experiments demonstrate the need.

Natural language plus lightweight metadata is preferred initially.

---

# 17. Provenance

Lore must eventually answer:

> Why do we believe this?

Knowledge should be traceable to evidence.

Example:

```text id="f6fdp3"
K-291

Statement:
Use DynamoDB for payment idempotency.

Reason:
Conditional writes are required for concurrent workers.

Sources:
INC-183
PR #281
load test May 2026

Supersedes:
K-172 Redis SETNX
```

Potential provenance:

- source code;
- commits;
- PRs;
- human statements;
- incidents;
- tests;
- documents;
- agent interactions.

---

# 18. AI runtime

Lore must NOT fundamentally depend on Codex, Claude Code, Cursor, or another coding-agent harness.

The core owns:

- ingestion;
- evidence collection;
- prompts/reasoning stages;
- structured outputs;
- provenance;
- reconciliation;
- knowledge retrieval.

AI models provide reasoning.

Initial model architecture:

```text id="cs5gh1"
                   Lore
                    │
              AI Runtime
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      OpenAI     Anthropic    custom
```

Implement only what is necessary initially.

Recommended v0:

- BYOK;
- OpenAI provider first;
- configurable model;
- configurable OpenAI-compatible base URL if straightforward.

Example:

```bash id="05cbr1"
export OPENAI_API_KEY=...

lore archaeologist .
```

Potential later interface:

```bash id="5mqvdh"
lore archaeologist . \
  --provider openai \
  --model <model>
```

Do not over-engineer provider abstraction prematurely.

A minimal internal interface is enough:

```python id="yn2h18"
class Model:
    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        ...
```

Additional providers can be implemented when needed.

---

# 19. Agent direction

Protect this architectural principle:

> **Agents call Lore. Lore should not fundamentally depend on agents.**

Long-term:

```text id="54h91j"
Claude Code ─┐
Codex ───────┼──► Lore
Cursor ──────┘
```

Potential integration:

```text id="amvk4j"
MCP / API
```

Example agent query:

> I am modifying `payments/refunds.py`. Give me the relevant knowledge, historical decisions, conventions and constraints.

Lore responds with resolved context.

Coding agents remain responsible for implementation.

---

# 20. CLI vs HTTP

Start with a **local CLI**.

Example:

```bash id="wbxvkg"
lore init
lore archaeologist .
lore ask "Why do we use Redis here?"
lore context "Add bulk account deletion"
```

However, CLI commands must be thin wrappers around application APIs.

Do NOT embed core logic in CLI handlers.

Architecture:

```text id="l3p7eq"
                lore-core
                    │
             application API
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
       CLI         HTTP        MCP
      first        later       later
```

This allows a future hosted service without rewriting core functionality.

---

# 21. Local-first

Local-first is important.

Repository analysis should happen locally wherever practical.

Advantages:

- proprietary source does not need to be uploaded to Lore;
- deterministic repository analysis remains local;
- teams can use approved AI endpoints;
- easier adoption inside real work environments;
- open-source users retain control over software knowledge.

Possible enterprise topology:

```text id="8t07m8"
company repository
        ↓
local Lore
        ↓
company-approved LLM endpoint
``