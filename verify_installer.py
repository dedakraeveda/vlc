"""Real per-user NSIS install/uninstall smoke, without touching stock VLC."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import winreg
import zipfile
import win32com.client

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist/verified'
TARGET = Path('D:/projects/temp/vlc-juxtopposed-installer-smoke')
OWN_KEYS = [r'Software\Quite\VLCJuxtopposed',
            r'Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed']


def key_exists(path):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path):
            return True
    except FileNotFoundError:
        return False


def hash_stream(stream):
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def stock_snapshot():
    rows = []
    for hive in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for view in [winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY]:
            try:
                with winreg.OpenKey(hive, r'Software\VideoLAN\VLC', 0, winreg.KEY_READ | view) as key:
                    for name in ['', 'InstallDir', 'Version', 'Lang']:
                        try:
                            value, kind = winreg.QueryValueEx(key, name)
                            rows.append((int(hive), view, name, str(value), kind))
                        except FileNotFoundError:
                            pass
            except FileNotFoundError:
                pass
    profile = Path(os.environ['APPDATA']) / 'vlc'
    metadata = []
    if profile.exists():
        for path in sorted(profile.rglob('*')):
            if path.is_file():
                stat = path.stat()
                metadata.append((str(path.relative_to(profile)), stat.st_size, stat.st_mtime_ns))
    return {'registryDigest': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
            'profileMetadataDigest': hashlib.sha256(json.dumps(metadata).encode()).hexdigest(),
            'profileFileCount': len(metadata)}


def shortcut_path():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                       r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
        programs, _ = winreg.QueryValueEx(key, 'Programs')
    return Path(programs) / 'VLC Juxtopposed.lnk'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorized', action='store_true', help='Run the exact temporary install/uninstall scenario')
    args = parser.parse_args()
    if not args.authorized:
        parser.error('Explicit --authorized is required')
    assert not TARGET.exists(), 'Scratch install target already exists; refuse to overwrite'
    assert not any(key_exists(k) for k in OWN_KEYS), 'Existing redesign registration; refuse to overwrite'
    shortcut = shortcut_path()
    assert not shortcut.exists(), 'Existing user shortcut; refuse to overwrite'
    before = stock_snapshot()
    env = os.environ.copy()
    temporary = ROOT / 'smoke/installer-temp'
    temporary.mkdir(parents=True, exist_ok=True)
    env.update(TEMP=str(temporary), TMP=str(temporary))
    setup = DIST / 'VLC-Juxtopposed-4.0-dev-win64-Setup.exe'
    archive = DIST / 'VLC-Juxtopposed-4.0-dev-win64-portable.zip'
    assert setup.is_file() and archive.is_file()
    expected = {}
    with zipfile.ZipFile(archive) as zipped:
        for item in zipped.infolist():
            if item.is_dir():
                continue
            rel = Path(item.filename).relative_to('VLC-Juxtopposed')
            assert not rel.is_absolute() and '..' not in rel.parts
            with zipped.open(item) as stream:
                expected[str(rel)] = hash_stream(stream)
    result = {'ok': False, 'operation': 'installer-roundtrip', 'target': str(TARGET),
              'stockBefore': before, 'filesExpected': len(expected)}
    evidence = ROOT / 'smoke/installer-result.json'
    evidence.write_text(json.dumps(result, indent=2), 'utf-8')
    installed = False
    try:
        subprocess.run([str(setup), '/S', '/D=' + str(TARGET).replace('/', '\\')],
                       env=env, check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        installed = True
        assert (TARGET / 'vlc.exe').is_file()
        for rel, expected_hash in expected.items():
            with (TARGET / rel).open('rb') as stream:
                assert hash_stream(stream) == expected_hash, 'Installed payload mismatch: ' + rel
        assert (TARGET / 'portable/README.txt').is_file()
        assert shortcut.exists()
        link = win32com.client.Dispatch('WScript.Shell').CreateShortcut(str(shortcut))
        assert Path(link.TargetPath).resolve() == (TARGET / 'vlc.exe').resolve()
        assert link.Arguments == '--no-crashdump --config="' + str(TARGET / 'portable/vlcrc') + '"'
        assert Path(link.WorkingDirectory).resolve() == TARGET.resolve()
        result['shortcutVerified'] = True
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, OWN_KEYS[0]) as key:
            location, _ = winreg.QueryValueEx(key, 'InstallDir')
            assert Path(location).resolve() == TARGET.resolve()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, OWN_KEYS[1]) as key:
            command, _ = winreg.QueryValueEx(key, 'UninstallString')
            assert command.startswith('"') and command.endswith('"')
            assert Path(command[1:-1]).resolve() == (TARGET / 'Uninstall-Juxtopposed.exe').resolve()
        assert stock_snapshot() == before, 'Stock VLC state changed during install'
        result['installationVerified'] = True
        # Run the actual installed executable on actual H.264 media.
        run = subprocess.run(['python.exe', str(ROOT / 'verify_runtime.py'), '--payload', str(TARGET)],
                             env=env, capture_output=True, text=True, timeout=90,
                             creationflags=subprocess.CREATE_NO_WINDOW)
        result['installedPlayback'] = json.loads(run.stdout)
        assert run.returncode == 0 and result['installedPlayback']['ok']
        (ROOT / 'smoke/installed-playback-result.json').write_text(json.dumps(result['installedPlayback'], indent=2), 'utf-8')
        for rel in ['portable/keep-user-preferences.txt', 'keep-user-file.txt']:
            (TARGET / rel).write_text('Task-created sentinel: uninstall must preserve non-package files.', 'utf-8')
        result['userSentinelsCreated'] = True
    finally:
        if installed and (TARGET / 'Uninstall-Juxtopposed.exe').is_file():
            subprocess.run([str(TARGET / 'Uninstall-Juxtopposed.exe'), '/S'],
                           env=env, check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline and (any(key_exists(k) for k in OWN_KEYS) or (TARGET / 'vlc.exe').exists()):
                time.sleep(0.5)
            assert not any(key_exists(k) for k in OWN_KEYS)
            assert not shortcut.exists()
            assert not (TARGET / 'Uninstall-Juxtopposed.exe').exists()
            assert not any((TARGET / rel).exists() for rel in expected)
            if result.get('userSentinelsCreated'):
                assert (TARGET / 'portable/keep-user-preferences.txt').is_file()
                assert (TARGET / 'keep-user-file.txt').is_file()
            assert stock_snapshot() == before, 'Stock VLC state changed during uninstall'
            result['uninstallationVerified'] = True
            result['stockAfter'] = stock_snapshot()
        result['ok'] = (result.get('installationVerified', False)
                        and result.get('uninstallationVerified', False)
                        and result.get('installedPlayback', {}).get('ok', False))
        evidence.write_text(json.dumps(result, indent=2), 'utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
