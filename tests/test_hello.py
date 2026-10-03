"""Offline tests: exercise the real CLI and SDK, replace only HTTP transport."""
import contextlib
import io
import json
import os
import unittest
from unittest.mock import patch

import httpx
from google import genai
from lore.cli import main


class HelloTests(unittest.TestCase):
    def run_cli(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_prompt_and_model_reach_gemini_and_response_is_printed(self):
        requests = []

        def respond(request):
            requests.append(request)
            return httpx.Response(200, json={
                "candidates": [{"content": {"role": "model", "parts": [{"text": "Hello, engineer!"}]}, "finishReason": "STOP"}]
            })

        client = genai.Client(api_key="test-key", http_options={
            "client_args": {"transport": httpx.MockTransport(respond)}
        })
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "LORE_PROVIDER": "gemini", "LORE_MODEL": "test-model"}, clear=True), patch(
            "lore.providers.gemini.genai.Client", return_value=client
        ):
            result = self.run_cli(["hello", "Say hello", "--model", "test-model"])
        self.assertEqual(result, (0, "Hello, engineer!\n", ""))
        self.assertEqual(len(requests), 1)
        self.assertIn("test-model:generateContent", requests[0].url.path)
        body = json.loads(requests[0].content)
        self.assertEqual(body["contents"][0]["parts"][0]["text"], "Say hello")

    def test_missing_key_is_actionable(self):
        with patch.dict(os.environ, {"LORE_PROVIDER": "gemini", "LORE_MODEL": "test-model"}, clear=True):
            code, output, error = self.run_cli(["hello"])
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("GEMINI_API_KEY", error)

    def test_unknown_provider_never_falls_back(self):
        with patch.dict(os.environ, {"LORE_PROVIDER": "unknown"}, clear=True):
            code, output, error = self.run_cli(["hello"])
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("Unsupported provider", error)

    def test_rate_limit_is_not_retried_or_exposed_raw(self):
        requests = []

        def respond(request):
            requests.append(request)
            return httpx.Response(429, json={"error": {"code": 429, "message": "private diagnostic", "status": "RESOURCE_EXHAUSTED"}})

        client = genai.Client(api_key="test-key", http_options={
            "client_args": {"transport": httpx.MockTransport(respond)},
            "retry_options": {"attempts": 1}
        })
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "LORE_PROVIDER": "gemini", "LORE_MODEL": "test-model"}, clear=True), patch(
            "lore.providers.gemini.genai.Client", return_value=client
        ):
            code, output, error = self.run_cli(["hello"])
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("429", error)
        self.assertNotIn("private diagnostic", error)
        self.assertEqual(len(requests), 1)

    def test_empty_response_is_an_error(self):
        client = genai.Client(api_key="test-key", http_options={
            "client_args": {"transport": httpx.MockTransport(lambda request: httpx.Response(200, json={"candidates": []}))}
        })
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "LORE_PROVIDER": "gemini", "LORE_MODEL": "test-model"}, clear=True), patch(
            "lore.providers.gemini.genai.Client", return_value=client
        ):
            code, output, error = self.run_cli(["hello"])
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("no text", error)


if __name__ == "__main__":
    unittest.main()
