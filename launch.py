"""Open only the verified Juxtopposed payload, never the failed first build."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
exe = root / 'dist/verified/portable/VLC-Juxtopposed/vlc.exe'
if not exe.is_file():
    raise SystemExit('Verified Windows build is not available yet. See TASK-STATE.md.')
(exe.parent / 'portable').mkdir(exist_ok=True)
subprocess.Popen([str(exe), '--no-crashdump', *sys.argv[1:]], cwd=exe.parent,
                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                 stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
