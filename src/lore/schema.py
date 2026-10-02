"""Portable candidate contract shared by external and BYOK reasoning."""
from .storage import LoreError

FIELDS = ("statement", "kind", "scope", "rationale", "uncertainty")
KINDS = ("observation", "convention", "constraint", "decision", "invariant", "preference", "learning")
CANDIDATE_PROPERTIES = {key: {"type": "string", "minLength": 1} for key in FIELDS}
CANDIDATE_PROPERTIES["kind"] = {"type": "string", "enum": list(KINDS)}
CANDIDATE_PROPERTIES.update({key: {"type": "array", "items": {"type": "string"}}
                             for key in ("evidence_ids", "exceptions")})
RESPONSE_SCHEMA = {"type": "object", "additionalProperties": False,
    "required": ["schema_version", "run_id", "candidates"], "properties": {
        "schema_version": {"type": "integer", "enum": [1]}, "run_id": {"type": "string"},
        "candidates": {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "required": list(CANDIDATE_PROPERTIES), "properties": CANDIDATE_PROPERTIES}}}}


def validate_response(response, run_id, evidence):
    if not isinstance(response, dict) or set(response) != {"schema_version", "run_id", "candidates"}:
        raise LoreError("Response must contain exactly schema_version, run_id, candidates")
    if type(response["schema_version"]) is not int or response["schema_version"] != 1:
        raise LoreError("Unsupported response schema_version")
    if response["run_id"] != run_id or not isinstance(response["candidates"], list):
        raise LoreError("Response run_id or candidates is invalid")
    if len(response["candidates"]) > 100:
        raise LoreError("At most 100 candidates per run")
    index = {item["id"]: item for item in evidence}
    for candidate in response["candidates"]:
        if not isinstance(candidate, dict) or set(candidate) != set(CANDIDATE_PROPERTIES):
            raise LoreError("Candidate fields must match response.schema.json")
        if any(not isinstance(candidate[k], str) or not candidate[k].strip() for k in FIELDS):
            raise LoreError("Candidate text fields must be nonempty strings")
        if candidate["kind"] not in KINDS:
            raise LoreError("Unsupported candidate kind")
        for key in ("evidence_ids", "exceptions"):
            if not isinstance(candidate[key], list) or any(not isinstance(v, str) or not v.strip() for v in candidate[key]):
                raise LoreError(f"Candidate {key} must be an array of nonempty strings")
        if not candidate["evidence_ids"] or any(v not in index for v in candidate["evidence_ids"]):
            raise LoreError("Each candidate must cite known evidence IDs")
    return response
