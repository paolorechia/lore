"""Exercise the CLI and adapter without making network requests."""
import contextlib
import io
import json
import os
import unittest
from unittest.mock import patch

import httpx

from lore.cli import main


class OpenRouterTests(unittest.TestCase):
    def run_cli(self, args, env):
        out, err = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, env, clear=True), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(args)
        return code, out.getvalue(), err.getvalue()

    def request(self, response, args=None, env=None):
        requests = []

        def respond(request):
            requests.append(request)
            return response

        with patch("lore.providers.openrouter.httpx.Client", return_value=httpx.Client(
            transport=httpx.MockTransport(respond)
        )):
            result = self.run_cli(
                args or ["hello", "Hi", "--model", "example/model:free"],
                env if env is not None else {"OPENROUTER_API_KEY": "test-key"},
            )
        return result, requests

    def test_default_provider_sends_selected_model_prompt_and_auth(self):
        result, requests = self.request(httpx.Response(200, json={
            "choices": [{"message": {"role": "assistant", "content": "Hello!"}}]
        }))
        self.assertEqual(result, (0, "Hello!\n", ""))
        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual(str(request.url), "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(request.headers["Authorization"], "Bearer test-key")
        payload = json.loads(request.content)
        self.assertEqual(payload["model"], "example/model:free")
        self.assertEqual(payload["messages"], [{"role": "user", "content": "Hi"}])
        self.assertFalse(payload["stream"])

    def test_environment_model_and_flag_override(self):
        for extra, expected in [([], "env/model:free"), (["--model", "flag/model:free"], "flag/model:free")]:
            with self.subTest(extra=extra):
                result, requests = self.request(
                    httpx.Response(200, json={"choices": [{"message": {"content": "Hi"}}]}),
                    args=["hello", *extra],
                    env={"OPENROUTER_API_KEY": "test-key", "LORE_MODEL": "env/model:free"},
                )
                self.assertEqual(result[0], 0)
                self.assertEqual(json.loads(requests[0].content)["model"], expected)

    def test_requires_explicit_model(self):
        code, output, error = self.run_cli(["hello"], {})
        self.assertEqual((code, output), (1, ""))
        self.assertIn("--model", error)

    def test_missing_key_is_actionable(self):
        code, output, error = self.run_cli(["hello", "--model", "openrouter/free"], {})
        self.assertEqual((code, output), (1, ""))
        self.assertIn("OPENROUTER_API_KEY", error)

    def test_http_error_is_not_retried_and_raw_body_is_not_shown(self):
        result, requests = self.request(httpx.Response(429, json={"error": {"message": "private diagnostic"}}))
        self.assertEqual(result[:2], (1, ""))
        self.assertIn("429", result[2])
        self.assertNotIn("private diagnostic", result[2])
        self.assertEqual(len(requests), 1)

    def test_empty_malformed_and_error_responses_fail_cleanly(self):
        for payload in ({}, {"choices": []}, {"choices": [{"message": {"content": None}}]},
                        {"choices": [{"message": {"content": " "}}]},
                        {"error": {"code": 502, "message": "private diagnostic"}}, []):
            with self.subTest(payload=payload):
                result, _ = self.request(httpx.Response(200, json=payload))
                self.assertEqual(result[:2], (1, ""))
                self.assertNotIn("private diagnostic", result[2])

    def test_non_json_response_fails_cleanly(self):
        result, _ = self.request(httpx.Response(200, text="not json"))
        self.assertEqual(result[:2], (1, ""))


if __name__ == "__main__":
    unittest.main()
