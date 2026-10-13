#!/usr/bin/env python3
"""Package the actual compiled VLC payload; no replacement binary or UI."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def escape(value):
    return str(value).replace('$', '$$').replace('"', '$\\"')


def manifests(payload):
    files = sorted(p for p in payload.rglob('*') if p.is_file())
    excluded = {'sdk', 'NSIS', 'helpers', 'languages', 'msi'}
    files = [p for p in files if not excluded.intersection(p.relative_to(payload).parts)
             and p.suffix not in {'.nsi', '.pdb', '.dbg'} and not p.name.startswith('spad')
             and (p.relative_to(payload).parts[0] != 'portable'
                  or p.relative_to(payload).as_posix() == 'portable/README.txt')]
    install, uninstall, dirs = [], [], set()
    for p in files:
        if p.is_symlink():
            raise ValueError('Symbolic links are not valid Windows payload files')
        rel = p.relative_to(payload)
        parent = str(rel.parent).replace('/', '\\')
        install += [f'SetOutPath "$INSTDIR\\{escape(parent)}"', f'File "{escape(p)}"']
        uninstall += [f'Delete "$INSTDIR\\{escape(str(rel).replace(chr(47), chr(92)))}"']
        dirs.update(rel.parents)
    uninstall += [f'RMDir "$INSTDIR\\{escape(str(d).replace(chr(47), chr(92)))}"'
                  for d in sorted(dirs, key=lambda d: (-len(d.parts), str(d))) if str(d) != '.']
    return '\n'.join(install), '\n'.join(uninstall), len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path, help='Explicit temporary storage, on D-backed volume locally')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    payload, output = args.payload.resolve(), args.output.resolve()
    required = ['vlc.exe', 'libvlc.dll', 'libvlccore.dll', 'COPYING.txt', 'README.txt', 'plugins/gui/libqt_plugin.dll']
    missing = [f for f in required if not (payload / f).is_file()]
    if missing:
        parser.error('Incomplete native payload: ' + ', '.join(missing))
    install, uninstall, count = manifests(payload)
    if args.dry_run:
        print(json.dumps({'ok': True, 'operation': 'plan', 'payload': str(payload), 'output': str(output), 'files': count}))
        return
    compiler = shutil.which('makensis')
    if not compiler:
        parser.error('makensis is required')
    if output.exists():
        parser.error('Output already exists; refuse to overwrite installer')
    output.parent.mkdir(parents=True, exist_ok=True)
    args.work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='nsis-', dir=args.work) as tmp:
        tmp = Path(tmp)
        (tmp / 'install.nsh').write_text(install + '\n', encoding='utf-8')
        (tmp / 'uninstall.nsh').write_text(uninstall + '\n', encoding='utf-8')
        subprocess.run([compiler, '-V2', f'-DPAYLOAD={payload}', f'-DOUTPUT={output}',
                        f'-DINSTALL_MANIFEST={tmp / "install.nsh"}',
                        f'-DUNINSTALL_MANIFEST={tmp / "uninstall.nsh"}',
                        str(Path(__file__).with_name('juxtopposed.nsi'))], check=True)
    if not output.is_file() or output.stat().st_size < 100_000:
        raise RuntimeError('Installer verification failed')
    print(json.dumps({'ok': True, 'operation': 'package', 'output': str(output),
                      'files': count, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
