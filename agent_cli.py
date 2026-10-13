"""Secret-safe, exact-project build/artifact control. JSON output only."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist/verified'
REPO = 'dedakraeveda/vlc'
EXPECTED = ['VLC-Juxtopposed-4.0-dev-win64-Setup.exe',
            'VLC-Juxtopposed-4.0-dev-win64-portable.zip', 'SHA256SUMS']


def invoke(args):
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
    if proc.returncode:
        raise ValueError('backend-operation-failed')
    return proc.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['capabilities', 'status', 'preflight', 'plan', 'apply', 'verify'])
    parser.add_argument('--json', action='store_true', help='JSON is the default and only output format')
    parser.add_argument('--authorized', action='store_true', help='Explicit owner authorization to submit one cloud build')
    args = parser.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    envelope = {'ok': True, 'operation': args.operation, 'contractVersion': 1,
                'evidence': {'verifiedAt': now, 'scope': str(ROOT), 'status': 'read-only'}}
    try:
        missing = [name for name in EXPECTED if not (DIST / name).is_file()]
        if args.operation == 'capabilities':
            result = {'commands': ['capabilities', 'status', 'preflight', 'plan', 'apply', 'verify'],
                      'target': REPO, 'branch': 'juxtopposed-redesign',
                      'safety': ['No credential output', 'No stock VLC changes', 'No file associations',
                                 'Apply submits exactly one build; never auto-retry'],
                      'uiRequired': [{'stage': 'visual-verification', 'reason': 'Native Qt rendering needs an actual Windows window',
                                      'verification': 'Orca target-window screenshot and interaction; not inferred from build'}]}
        elif args.operation == 'status':
            result = {'repo': REPO, 'sourceRevision': invoke(['git', 'rev-parse', 'HEAD']),
                      'missingArtifacts': missing,
                      'runtimeEvidence': {p.name: json.loads(p.read_text('utf-8')) for p in (ROOT / 'smoke').glob('*-result.json')},
                      'diskFreeGiB': {drive: round(shutil.disk_usage(drive).free / 2**30, 2)
                                      for drive in (['C:/', 'D:/'] if sys.platform == 'win32' else ['/'])}}
        elif args.operation in ['preflight', 'plan', 'apply']:
            remote = invoke(['git', 'remote', 'get-url', 'origin'])
            if remote != 'https://github.com/' + REPO + '.git':
                raise ValueError('identity-mismatch')
            if not shutil.which('gh'):
                raise ValueError('github-cli-missing')
            login = invoke(['gh', 'api', 'user', '--jq', '.login'])
            if login != REPO.split('/')[0]:
                raise ValueError('identity-mismatch')
            result = {'repo': REPO, 'branch': 'juxtopposed-redesign', 'workflow': 'windows-redesign.yml',
                      'action': 'Submit one native Windows x64 build; installer remains unsigned',
                      'idempotent': False}
            if args.operation == 'apply':
                if not args.authorized:
                    raise ValueError('owner-authorization-required')
                result['submitted'] = invoke(['gh', 'workflow', 'run', 'windows-redesign.yml',
                                              '--repo', REPO, '--ref', 'juxtopposed-redesign'])
                result['completionVerified'] = False
        else:
            if missing:
                raise ValueError('artifacts-missing')
            hashes = {}
            for line in (DIST / 'SHA256SUMS').read_text('utf-8').splitlines():
                expected, name = line.split(maxsplit=1)
                target = (DIST / name.lstrip('*')).resolve()
                if not target.is_relative_to(DIST.resolve()) or not target.is_file():
                    raise ValueError('invalid-artifact-path')
                actual = hashlib.sha256(target.read_bytes()).hexdigest()
                if expected != actual:
                    raise ValueError('verification-failed')
                hashes[target.name] = actual
            if set(EXPECTED[:-1]) != set(hashes):
                raise ValueError('invalid-artifact-manifest')
            result = {'sha256': hashes, 'scope': 'Artifact integrity only; runtime evidence is separate'}
            envelope['evidence']['status'] = 'artifact-integrity-verified'
        envelope['result'] = result
    except ValueError as error:
        envelope.update(ok=False, error={'code': str(error), 'message': 'Exact-project precondition/verification failed',
                                        'stage': args.operation, 'retryable': False,
                                        'nextAction': 'Inspect TASK-STATE.md and status; never blindly replay a submitted build'})
    print(json.dumps(envelope, ensure_ascii=False))
    return 0 if envelope['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
