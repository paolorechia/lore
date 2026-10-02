"""Optional BYOK Responses API adapter; no subscription credential discovery."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .schema import RESPONSE_SCHEMA
from .storage import LoreError


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LoreError("Provider redirect refused; configure the final base URL explicitly")


def generate(request, *, model, api_key, base_url="https://api.openai.com/v1", max_output_tokens=4000):
    if not api_key or not api_key.strip():
        raise LoreError("Set OPENAI_API_KEY to use BYOK; prepare/import needs no key")
    if not model or not model.strip():
        raise LoreError("Choose a model explicitly with --model")
    if type(max_output_tokens) is not int or max_output_tokens <= 0:
        raise LoreError("max_output_tokens must be positive")
    url = urlsplit(base_url)
    if url.username or url.password or url.query or url.fragment or not url.hostname:
        raise LoreError("Invalid provider base URL")
    if url.scheme != "https" and not (url.scheme == "http" and url.hostname in ("localhost", "127.0.0.1", "::1")):
        raise LoreError("Use HTTPS for remote providers; HTTP is allowed only on loopback")
    body = {"model": model, "input": request, "store": False, "max_output_tokens": max_output_tokens,
            "text": {"format": {"type": "json_schema", "name": "lore_candidates", "strict": True,
                                "schema": RESPONSE_SCHEMA}}}
    req = Request(base_url.rstrip("/") + "/responses", data=json.dumps(body).encode(),
                  headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"})
    try:
        with build_opener(NoRedirect()).open(req, timeout=120) as response:
            raw = response.read(16_000_001)
        if len(raw) > 16_000_000:
            raise LoreError("Provider response exceeds 16 MB")
        payload = json.loads(raw)
    except HTTPError as error:
        raise LoreError(f"Provider HTTP {error.code}; check key, model, endpoint, and quota. No retry was made.") from error
    except (URLError, TimeoutError) as error:
        raise LoreError("Provider connection failed or timed out. No retry was made.") from error
    except (ValueError, UnicodeError) as error:
        raise LoreError("Provider returned invalid JSON") from error
    if not isinstance(payload, dict) or payload.get("status") != "completed":
        raise LoreError("Provider response did not complete; inspect model/output budget before retrying")
    texts = []
    try:
        for item in payload["output"]:
            if item.get("type") != "message":
                continue
            for part in item["content"]:
                if part.get("type") == "refusal":
                    raise LoreError("Provider refused the request")
                if part.get("type") == "output_text":
                    texts.append(part["text"])
        return json.loads("".join(texts))
    except (KeyError, TypeError, AttributeError, ValueError) as error:
        if isinstance(error, LoreError):
            raise
        raise LoreError("Provider output was not valid candidate JSON") from error
