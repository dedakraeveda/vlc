"""Real Windows playback and Qt startup, with an isolated task profile."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload', type=Path, default=ROOT / 'dist/portable/vlc-4.0.0-dev')
    parser.add_argument('--gui', action='store_true', help='Initialize Qt offscreen (not a visual proof)')
    args = parser.parse_args()
    work = ROOT / 'smoke'
    work.mkdir(exist_ok=True)
    env = os.environ.copy()
    for key in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
        path = work / key.lower()
        path.mkdir(exist_ok=True)
        env[key] = str(path)
    exe = args.payload.resolve() / 'vlc.exe'
    log = work / ('qt-startup.log' if args.gui else 'playback.log')
    if log.exists():
        log.unlink()
    command = [str(exe), '--no-one-instance', '--no-media-library',
               '--config=' + str(work / 'vlcrc'), '--no-qt-privacy-ask',
               '--no-qt-updates-notif', '--no-qt-autoload-extensions',
               '--file-logging', '--logfile=' + str(log), '--verbose=2']
    if args.gui:
        env['QT_QPA_PLATFORM'] = 'offscreen'
        command += ['--intf=qt']
    else:
        command += ['--intf=dummy', '--vout=dummy', '--no-audio', '--avcodec-hw=none',
                    '--play-and-exit', str(work / 'test-video.mp4')]
    started = time.monotonic()
    proc = subprocess.Popen(command, env=env, cwd=exe.parent, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    alive = False
    try:
        if args.gui:
            time.sleep(12)
            alive = proc.poll() is None
            proc.terminate()
        out, err = proc.communicate(timeout=40)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        raise RuntimeError('Playback did not exit within 40 seconds')
    (work / ('qt-stderr.log' if args.gui else 'playback-stderr.log')).write_bytes(err)
    text = log.read_text('utf-8', errors='replace') if log.exists() else ''
    combined = text + err.decode('utf-8', errors='replace')
    if args.gui:
        ok = alive and 'using interface module "qt"' in combined and not any(
            s in combined for s in ['failed to load component', 'QQmlApplicationEngine failed', 'cannot load plug-in'])
    else:
        ok = proc.returncode == 0 and 'using video decoder module' in combined and 'EOF reached' in combined and 'cannot load plug-in' not in combined
    result = {'ok': ok, 'operation': 'qt-startup' if args.gui else 'playback',
              'exitCode': proc.returncode, 'durationSeconds': round(time.monotonic()-started, 2),
              'log': str(log), 'qtAliveBeforeTermination': alive if args.gui else None}
    (work / ('qt-result.json' if args.gui else 'playback-result.json')).write_text(json.dumps(result, indent=2), 'utf-8')
    print(json.dumps(result))
    raise SystemExit(0 if ok else 2)


if __name__ == '__main__':
    main()
