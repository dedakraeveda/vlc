"""Real Windows playback and Qt startup, with an isolated task profile."""
import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload', type=Path, default=ROOT / 'dist/verified/portable/VLC-Juxtopposed')
    parser.add_argument('--gui', action='store_true', help='Initialize the real Windows Qt interface and play test media to completion')
    parser.add_argument('--visible', action='store_true', help='Launch a real window for native visual inspection; close through the app after checking')
    args = parser.parse_args()
    work = ROOT / 'smoke'
    work.mkdir(exist_ok=True)
    env = os.environ.copy()
    for key in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
        path = work / key.lower()
        path.mkdir(exist_ok=True)
        env[key] = str(path)
    exe = args.payload.resolve() / 'vlc.exe'
    (exe.parent / 'portable').mkdir(exist_ok=True)
    log = work / ('qt-startup.log' if args.gui else 'playback.log')
    if log.exists():
        log.unlink()
    (work / 'vlcrc').touch(exist_ok=True)
    command = [str(exe), '--no-one-instance', '--no-media-library', '--no-crashdump',
               '--config=' + str(work / 'vlcrc'), '--no-qt-privacy-ask',
               '--no-qt-updates-notif', '--no-qt-autoload-extensions',
               '--no-qt-video-autoresize', '--no-qt-remember-window-geometry',
               '--restore-playback-pos=0', '--no-osd',
               '--file-logging', '--logfile=' + str(log), '--verbose=2']
    if args.visible:
        command.remove('--no-media-library')
        command += ['--media-library', '--intf=qt', '--no-audio', '--no-hw-dec',
                    '--repeat', str(work / 'test-video.mp4')]
        with (work / 'visible-stderr.log').open('wb') as stderr:
            proc = subprocess.Popen(command, env=env, cwd=exe.parent,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                    stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        (work / 'visible-pid.json').write_text(json.dumps({'pid': proc.pid}), 'utf-8')
        print(json.dumps({'operation': 'visual-launch', 'pid': proc.pid, 'verified': False}))
        return
    if args.gui:
        command += ['--intf=qt', '--vout=dummy', '--no-audio', '--no-hw-dec',
                    '--play-and-exit', str(work / 'test-video.mp4')]
    else:
        command += ['--intf=dummy', '--vout=dummy', '--no-audio', '--no-hw-dec',
                    '--play-and-exit', str(work / 'test-video.mp4')]
    started = time.monotonic()
    stderr_path = work / ('qt-stderr.log' if args.gui else 'playback-stderr.log')
    alive = False
    timed_out = False
    with stderr_path.open('wb') as stderr:
        proc = subprocess.Popen(command, env=env, cwd=exe.parent, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=stderr,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            if args.gui:
                time.sleep(2)
                alive = proc.poll() is None
            proc.wait(timeout=40)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            proc.wait(timeout=10)
    err = stderr_path.read_bytes()
    text = log.read_text('utf-8', errors='replace') if log.exists() else ''
    combined = text + err.decode('utf-8', errors='replace')
    if args.gui:
        ok = alive and proc.returncode == 0 and 'using interface module "qt"' in combined and not any(
            s in combined for s in ['failed to load component', 'QQmlApplicationEngine failed', 'cannot load plug-in', 'qml loading', 'Type Redesign', 'is not a type', 'ReferenceError', 'TypeError', 'Failed to get image from provider'])
    else:
        ok = proc.returncode == 0 and 'using video decoder module' in combined and 'EOF reached' in combined and 'cannot load plug-in' not in combined
    ok = ok and not timed_out
    result = {'ok': ok, 'operation': 'qt-startup' if args.gui else 'playback',
              'exitCode': proc.returncode, 'timedOut': timed_out, 'durationSeconds': round(time.monotonic()-started, 2),
              'log': str(log), 'payload': str(exe.parent),
              'sourceRevisionFromLog': (re.search(r'revision (\S+)', combined).group(1) if re.search(r'revision (\S+)', combined) else None),
              'qtAliveDuringPlayback': alive if args.gui else None}
    (work / ('qt-result.json' if args.gui else 'playback-result.json')).write_text(json.dumps(result, indent=2), 'utf-8')
    print(json.dumps(result))
    raise SystemExit(0 if ok else 2)


if __name__ == '__main__':
    main()
