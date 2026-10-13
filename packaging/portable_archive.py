"""Archive real VLC runtime, without build scripts, SDK or user profiles."""
import argparse
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--payload', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = args.payload.resolve()
assert (root / 'vlc.exe').is_file() and (root / 'plugins/gui/libqt_plugin.dll').is_file()
if args.output.exists():
    parser.error('Output exists; refuse to overwrite')
with zipfile.ZipFile(args.output, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if {'sdk', 'NSIS', 'helpers', 'languages', 'msi'}.intersection(rel.parts):
            continue
        if path.suffix in {'.nsi', '.pdb', '.dbg'} or path.name.startswith('spad'):
            continue
        if rel.parts[0] == 'portable' and rel.as_posix() != 'portable/README.txt':
            continue
        if path.is_symlink():
            raise ValueError('Symlink in Windows runtime')
        archive.write(path, Path('VLC-Juxtopposed') / rel)
print(args.output)
