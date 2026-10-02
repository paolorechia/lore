import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest

class ProviderTest(unittest.TestCase):
    def setUp(self):
        owner = self
        self.status = 200
        self.payload = {'status': 'completed', 'output': [{'type': 'message', 'content': [
            {'type': 'output_text', 'text': '{"schema_version":1,"run_id":"abc","candidates":[]}'}]}]}
        self.request = None
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                owner.request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                self.send_response(owner.status)
                self.end_headers()
                self.wfile.write(json.dumps(owner.payload).encode())
            def log_message(self, *args):
                pass
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = f'http://127.0.0.1:{self.server.server_port}/v1'

    def call(self):
        from lore.provider import generate
        return generate('evidence request', model='fixture-model', api_key='fixture-key', base_url=self.url)

    def test_structured_response_and_explicit_model(self):
        self.assertEqual(self.call()['candidates'], [])
        self.assertEqual(self.request['model'], 'fixture-model')
        self.assertFalse(self.request['store'])
        self.assertEqual(self.request['text']['format']['type'], 'json_schema')

    def test_http_failure_never_leaks_provider_body(self):
        from lore.storage import LoreError
        self.status = 401
        self.payload = {'error': 'fixture-key secret'}
        with self.assertRaises(LoreError) as raised:
            self.call()
        self.assertNotIn('fixture-key', str(raised.exception))
        self.assertIn('401', str(raised.exception))

    def test_incomplete_refusal_and_malformed_outputs_fail(self):
        from lore.storage import LoreError
        for payload in [None, {}, {'status': 'incomplete', 'output': []},
                        {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'refusal', 'refusal': 'No'}]}]},
                        {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': 'bad JSON'}]}]}]:
            with self.subTest(payload=payload):
                self.payload = payload
                with self.assertRaises(LoreError):
                    self.call()

    def test_requires_explicit_credentials_and_safe_endpoint(self):
        from lore.provider import generate
        from lore.storage import LoreError
        for kwargs in [{'api_key': ''}, {'base_url': 'http://example.com/v1'},
                       {'base_url': 'https://user:password@example.com/v1'}, {'model': ''},
                       {'max_output_tokens': 0}]:
            options = {'model': 'fixture-model', 'api_key': 'fixture-key', **kwargs}
            with self.assertRaises(LoreError):
                generate('request', **options)

    def test_paid_run_preflights_stale_sources_and_saved_responses(self):
        import os
        from pathlib import Path
        import subprocess
        import tempfile
        from unittest.mock import patch
        from lore.archaeologist import prepare, run_model
        from lore.storage import LoreError

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', tmp], check=True)
            source = root / 'code.py'
            source.write_text('import os\n')
            subprocess.run(['git', '-C', tmp, 'add', '.'], check=True)
            run = prepare(root)
            source.write_text('import sys\n')
            # Any provider execution here is a bug, regardless of network behavior.
            with patch('lore.provider.generate', side_effect=AssertionError('Unnecessary paid call')):
                with self.assertRaisesRegex(LoreError, 'Stale'):
                    run_model(root, run['run_id'], model='fixture')
            source.write_text('import os\n')
            (Path(run['path']) / 'model-response.json').write_text('{}')
            with patch('lore.provider.generate', side_effect=AssertionError('Unnecessary paid retry')):
                with self.assertRaisesRegex(LoreError, 'saved response'):
                    run_model(root, run['run_id'], model='fixture')

    def test_full_byok_run_stores_candidates_and_refuses_repeat(self):
        import os
        from pathlib import Path
        import subprocess
        import tempfile
        from unittest.mock import patch
        from lore.archaeologist import prepare, run_model
        from lore.storage import LoreError

        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'OPENAI_API_KEY': 'fixture-key'}):
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', tmp], check=True)
            (root / 'code.py').write_text('import os\n')
            subprocess.run(['git', '-C', tmp, 'add', '.'], check=True)
            run = prepare(root)
            answer = {'schema_version': 1, 'run_id': run['run_id'], 'candidates': []}
            self.payload['output'][0]['content'][0]['text'] = json.dumps(answer)
            result = run_model(root, run['run_id'], model='fixture', base_url=self.url)
            self.assertEqual(json.loads(Path(result['path']).read_text())['candidates'], [])
            with self.assertRaisesRegex(LoreError, 'already has candidates'):
                run_model(root, run['run_id'], model='fixture', base_url=self.url)
