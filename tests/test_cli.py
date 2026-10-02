import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC = str(Path(__file__).resolve().parents[1] / 'src')

class CLITest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        self.put('src/domain.py', 'import os\nfrom infrastructure import db\n')
        self.put('src/api.ts', 'import { save } from "./store";\nexport const run = () => save();\n')
        self.put('.gitignore', 'ignored.py\n')
        self.put('ignored.py', 'SECRET = "not evidence"\n')
        subprocess.run(['git', '-C', str(self.repo), 'add', '.'], check=True)

    def put(self, name, value):
        p = self.repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value)
        return p

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, '-m', 'lore', *map(str, args)],
            cwd=self.repo, env={**os.environ, 'PYTHONPATH': SRC}, text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('Traceback', result.stderr)
        return result

    def prepare(self, *args):
        result = self.cli('archaeologist', 'prepare', '.', '--question', 'What dependencies are visible?', *args)
        return json.loads(result.stdout)

    def response(self, run):
        bundle = json.loads((Path(run['path']) / 'evidence.json').read_text())
        e = next(e for e in bundle['evidence'] if e['path'] == 'src/domain.py')
        response = {'schema_version': 1, 'run_id': run['run_id'], 'candidates': [{
            'statement': 'The domain module imports infrastructure.', 'kind': 'observation',
            'scope': 'src', 'rationale': 'Direct import in the observed module.',
            'uncertainty': 'This does not establish intended policy.',
            'evidence_ids': [e['id']], 'exceptions': []}]}
        return self.put('response.json', json.dumps(response)), response

    def test_init_preserves_existing_knowledge_and_ignore(self):
        self.put('.lore/knowledge/custom.md', 'Keep me')
        self.cli('init', '.')
        self.cli('init', '.')
        self.assertEqual((self.repo / '.lore/knowledge/custom.md').read_text(), 'Keep me')
        self.assertEqual((self.repo / '.gitignore').read_text(), 'ignored.py\n')
        self.assertTrue((self.repo / '.lore/.gitignore').exists())

    def test_prepare_is_deterministic_and_includes_counterexample_and_typescript(self):
        a, b = self.prepare(), self.prepare()
        self.assertEqual(a['run_id'], b['run_id'])
        data = json.loads((Path(a['path']) / 'evidence.json').read_text())
        self.assertEqual({e['path'] for e in data['evidence']}, {'src/domain.py', 'src/api.ts'})
        self.assertIn('infrastructure', str(data))
        self.assertNotIn('not evidence', str(data))
        self.assertTrue((Path(a['path']) / 'request.md').exists())
        self.assertTrue((Path(a['path']) / 'response.schema.json').exists())

    def test_import_valid_idempotent_and_conflict_rejected(self):
        run = self.prepare()
        p, response = self.response(run)
        a = self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p)
        b = self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p)
        self.assertEqual(a.stdout, b.stdout)
        stored = json.loads(Path(json.loads(a.stdout)['path']).read_text())
        self.assertEqual(stored['candidates'][0]['status'], 'candidate')
        self.assertEqual(stored['candidates'][0]['evidence'][0]['path'], 'src/domain.py')
        response['candidates'][0]['statement'] = 'A different statement'
        p.write_text(json.dumps(response))
        self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p, ok=False)

    def test_stale_and_invented_evidence_rejected_without_writes(self):
        run = self.prepare()
        p, response = self.response(run)
        response['candidates'][0]['evidence_ids'] = ['invented']
        p.write_text(json.dumps(response))
        self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p, ok=False)
        p, _ = self.response(run)
        self.put('src/domain.py', 'import sys\n')
        self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p, ok=False)
        self.assertEqual(list((self.repo / '.lore/candidates').glob('*.json')), [])

    def test_budget_and_empty_selection_are_explicit(self):
        run = self.prepare('--max-files', '1')
        data = json.loads((Path(run['path']) / 'evidence.json').read_text())
        self.assertEqual(data['coverage']['included_files'], 1)
        self.assertTrue(data['coverage']['skipped'])
        self.cli('archaeologist', 'prepare', '.', '--include', '*.notreal', ok=False)
        self.cli('archaeologist', 'prepare', '.', '--max-files', '0', ok=False)

    def test_untracked_opt_in_and_symlinks_excluded(self):
        self.put('new.py', 'import json\n')
        (self.repo / 'link.py').symlink_to(self.repo / 'src/domain.py')
        run = self.prepare('--include-untracked')
        data = json.loads((Path(run['path']) / 'evidence.json').read_text())
        paths = {e['path'] for e in data['evidence']}
        self.assertIn('new.py', paths)
        self.assertNotIn('link.py', paths)
        self.assertNotIn('ignored.py', paths)

    def test_path_escape_and_symlinked_state_fail_cleanly(self):
        self.cli('archaeologist', 'import', '.', '--run', '../../outside', '--response', 'x', ok=False)
        outside = self.repo / 'outside'
        outside.mkdir()
        (self.repo / '.lore').symlink_to(outside, target_is_directory=True)
        self.cli('init', '.', ok=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_invalid_json_and_invalid_fields_fail_cleanly(self):
        run = self.prepare()
        p, response = self.response(run)
        for value in ['{', 'null', '[]', json.dumps({**response, 'candidates': [{'statement': ''}]}),
                      json.dumps({**response, 'schema_version': True})]:
            p.write_text(value)
            self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p, ok=False)

    def test_show_renders_reviewable_findings(self):
        run = self.prepare()
        p, _ = self.response(run)
        self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p)
        result = self.cli('archaeologist', 'show', '.', '--run', run['run_id'])
        self.assertIn('The domain module imports infrastructure.', result.stdout)
        self.assertIn('src/domain.py:1-2', result.stdout)
        self.assertIn('candidate', result.stdout)

    def test_no_findings_is_valid_and_deleted_sources_are_stale(self):
        run = self.prepare()
        p, response = self.response(run)
        response['candidates'] = []
        p.write_text(json.dumps(response))
        result = self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p)
        self.assertEqual(json.loads(result.stdout)['candidates'], 0)
        (self.repo / 'src/domain.py').unlink()
        self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p, ok=False)

    def test_binary_large_syntax_errors_and_tracked_ignored_are_visible(self):
        self.put('broken.py', 'def : broken')
        self.put('large.py', 'x' * 1000)
        (self.repo / 'binary.py').write_bytes(b'\xff\x00')
        subprocess.run(['git', '-C', str(self.repo), 'add', '-f', 'ignored.py'], check=True)
        run = self.prepare('--include-untracked', '--max-file-bytes', '100')
        data = json.loads((Path(run['path']) / 'evidence.json').read_text())
        self.assertIn('broken.py', [w['path'] for w in data['coverage']['warnings']])
        skipped = {e['path'] for e in data['coverage']['skipped']}
        self.assertTrue({'large.py', 'binary.py', 'ignored.py'} <= skipped)
        self.assertNotIn('SECRET', str(data['evidence']))

    def test_bundle_tampering_and_nested_state_symlinks_are_rejected(self):
        run = self.prepare()
        p, _ = self.response(run)
        evidence = Path(run['path']) / 'evidence.json'
        value = json.loads(evidence.read_text())
        value['question'] = 'tampered'
        evidence.write_text(json.dumps(value))
        self.cli('archaeologist', 'import', '.', '--run', run['run_id'], '--response', p, ok=False)
        candidates = self.repo / '.lore/candidates'
        candidates.rmdir()
        candidates.symlink_to(self.repo / 'src', target_is_directory=True)
        self.cli('init', '.', ok=False)

if __name__ == '__main__':
    unittest.main()
