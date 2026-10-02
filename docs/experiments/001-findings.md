# Archaeologist findings: 6a41910ce035a392e724395b

Status: candidates; human review required.

Question: What architectural boundaries does Lore currently implement, and where are those boundaries incomplete?

## 6a41910ce035a392e724395b-K001

CLI argument handling delegates evidence preparation and candidate import to the Archaeologist application module.

Scope: src/lore
Kind: observation
Rationale: cli.main calls prepare, import_response, run_model, and show; the corresponding implementations live in archaeologist.py.
Uncertainty: This describes the current snapshot, not a proven project-wide policy. Initialization is also invoked directly from the CLI.

Evidence:
- src/lore/cli.py:1-60 (E-0011, sha256 50987ee669b19f8f82a1a8be35f91618e0eb06ea539299eaa11e80379489229e)
- src/lore/archaeologist.py:1-120 (E-0004, sha256 cfd421fa69974bcc78bec77f431a124b299f4919731cdf9af7317033c614eaaa)

Exceptions: The CLI calls initialize and repository from storage for the init command.

## 6a41910ce035a392e724395b-K002

Evidence collection is deterministic and separate from model reasoning, but ingestion currently depends on the storage module for Git, path, and hashing helpers.

Scope: src/lore
Kind: observation
Rationale: collect reads selected source and returns evidence without writing knowledge or invoking a model. run_model invokes the provider separately.
Uncertainty: The module boundary is not a strict dependency inversion: storage contains shared infrastructure helpers. Non-Python evidence is source text, not parsed dependencies.

Evidence:
- src/lore/ingestion.py:1-90 (E-0018, sha256 c474bceada107a59faef9a08340a6814b8d813b3313498cc766777a28f18782c)
- src/lore/archaeologist.py:1-120 (E-0004, sha256 cfd421fa69974bcc78bec77f431a124b299f4919731cdf9af7317033c614eaaa)
- src/lore/storage.py:1-97 (E-0033, sha256 4c244be5f72947ff68e0e73669666c2f02431ba115bc73e0c9eb903d4d0f2e7f)

Exceptions: Ingestion imports repository utility functions from storage.

## 6a41910ce035a392e724395b-K003

Externally supplied and BYOK-generated findings share the same validation and candidate-only persistence path.

Scope: src/lore/archaeologist.py
Kind: observation
Rationale: run_model passes its response to import_response, which validates schema and source hashes before adding candidate status and publishing the result.
Uncertainty: Validation establishes structure and citation freshness, not the truth of the inferred statement or intended policy. Human review remains necessary.

Evidence:
- src/lore/archaeologist.py:1-120 (E-0004, sha256 cfd421fa69974bcc78bec77f431a124b299f4919731cdf9af7317033c614eaaa)
- src/lore/schema.py:1-39 (E-0031, sha256 d205de046db81896ef65a4e103436921e5b13070a492967f69908bd2e116cd88)

Exceptions: None reported; absence is not proof.
