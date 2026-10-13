import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('vlc_agent_cli', Path(__file__).resolve().parents[1] / 'agent_cli.py')
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


class AgentCliTests(unittest.TestCase):
    def call(self, *args):
        out = io.StringIO()
        with patch('sys.argv', ['agent_cli.py', *args]), contextlib.redirect_stdout(out):
            code = cli.main()
        return code, json.loads(out.getvalue())

    @staticmethod
    def backend(args):
        if args[:4] == ['git', 'remote', 'get-url', 'origin']:
            return 'https://github.com/dedakraeveda/vlc.git'
        if args[:3] == ['gh', 'api', 'user']:
            return 'dedakraeveda'
        if args[:3] == ['gh', 'run', 'list']:
            return '[]'
        if args[:3] == ['git', 'status', '--porcelain']:
            return ''
        raise AssertionError('Unexpected backend call: ' + str(args))

    def test_capabilities_envelope(self):
        code, obj = self.call('capabilities', '--json')
        self.assertEqual(code, 0)
        self.assertTrue(obj['ok'])
        self.assertEqual(obj['contractVersion'], 1)
        self.assertIn('apply', obj['result']['commands'])

    def test_missing_artifacts_classified(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp, patch.object(cli, 'DIST', Path(tmp)):
            code, obj = self.call('verify')
        self.assertEqual(code, 2)
        self.assertEqual(obj['error']['code'], 'artifacts-missing')

    def test_identity_mismatch_blocks_backend(self):
        with patch.object(cli, 'invoke', return_value='https://github.com/another/repo.git'):
            code, obj = self.call('preflight')
        self.assertEqual(code, 2)
        self.assertEqual(obj['error']['code'], 'identity-mismatch')

    def test_backend_diagnostics_never_leak(self):
        result = cli.subprocess.CompletedProcess([], 1, stdout='', stderr='TEST_SECRET_DO_NOT_PRINT')
        with patch.object(cli.subprocess, 'run', return_value=result):
            code, obj = self.call('preflight')
        self.assertEqual(code, 2)
        self.assertNotIn('TEST_SECRET', json.dumps(obj))
        self.assertEqual(obj['error']['code'], 'backend-operation-failed')

    def test_github_cli_missing(self):
        with patch.object(cli, 'invoke', side_effect=self.backend), patch.object(cli.shutil, 'which', return_value=None):
            code, obj = self.call('preflight')
        self.assertEqual(code, 2)
        self.assertEqual(obj['error']['code'], 'github-cli-missing')

    def test_plan_read_only(self):
        with patch.object(cli, 'invoke', side_effect=self.backend) as backend, patch.object(cli.shutil, 'which', return_value='gh'):
            code, obj = self.call('plan')
        self.assertEqual(code, 0)
        self.assertFalse(obj['result']['idempotent'])
        self.assertFalse(any(call.args[0][:3] == ['gh', 'workflow', 'run'] for call in backend.call_args_list))

    def test_apply_requires_authorization(self):
        with patch.object(cli, 'invoke', side_effect=self.backend), patch.object(cli.shutil, 'which', return_value='gh'):
            code, obj = self.call('apply')
        self.assertEqual(code, 2)
        self.assertEqual(obj['error']['code'], 'owner-authorization-required')

    def test_concurrent_build_rejected(self):
        def backend(args):
            if args[:3] == ['gh', 'run', 'list']:
                return '[{"databaseId":1,"status":"in_progress"}]'
            return self.backend(args)
        with patch.object(cli, 'invoke', side_effect=backend), patch.object(cli.shutil, 'which', return_value='gh'):
            code, obj = self.call('apply', '--authorized')
        self.assertEqual(code, 2)
        self.assertEqual(obj['error']['code'], 'concurrent-operation')

    def test_dirty_source_rejected(self):
        def backend(args):
            if args[:3] == ['git', 'status', '--porcelain']:
                return ' M source.cpp'
            return self.backend(args)
        with patch.object(cli, 'invoke', side_effect=backend), patch.object(cli.shutil, 'which', return_value='gh'):
            code, obj = self.call('apply', '--authorized')
        self.assertEqual(code, 2)
        self.assertEqual(obj['error']['code'], 'revision-changed')

    def test_hash_postcondition_and_corruption(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp, patch.object(cli, 'DIST', Path(tmp)):
            folder = Path(tmp)
            rows = []
            for name in cli.EXPECTED[:-1]:
                content = ('test-' + name).encode()
                (folder / name).write_bytes(content)
                rows.append(hashlib.sha256(content).hexdigest() + '  ' + name)
            (folder / 'SHA256SUMS').write_text('\n'.join(rows), 'utf-8')
            code, obj = self.call('verify')
            self.assertEqual(code, 0)
            self.assertEqual(obj['evidence']['status'], 'artifact-integrity-verified')
            (folder / cli.EXPECTED[0]).write_bytes(b'corrupted')
            code, obj = self.call('verify')
            self.assertEqual(code, 2)
            self.assertEqual(obj['error']['code'], 'verification-failed')


if __name__ == '__main__':
    unittest.main()
