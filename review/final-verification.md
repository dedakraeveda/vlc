# Windows x64 acceptance evidence

Compiled source: `41e927845202cf2c6f64a864f2f7037ba336857d`.
CI: https://github.com/dedakraeveda/vlc/actions/runs/38470541761 — success.

- SHA256 Setup: b5b0d7b573950508cb8a276e97a6c1d9f177dc2e098df9c6b9e3e3dbbd8b3780
- SHA256 ZIP: 511dd7fffd6cf4a5426f8a457d0b0ed3df820d709185cd3376cd4f1b2ca968b3
- Real H.264 software decode/EOF: exit0, 4.42s, no timeout, source revision from native log41e9278452.
- Real Qt + decoder + EOF: exit0, 4.94s, no timeout; Qt alive during playback; no QML/provider errors.
- Real visible native Window1440x820, test PID33328: all icons visible, Pause->Play label observed, library->Music exposes Songs/Albums/Artists/Genres, Queue contains actual test-video.mp4, real Close followed by process disappearance with NO external kill. See player-final.png/library-final.png/queue-final.png and visual-result.json.
- Real per-user NSIS install at exact D task scratch path: all538 delivered files match portable ZIP; .lnk target/arguments/working-directory correct; own HKCU registration correct; installed H.264 playback exit0/4.47s; silent uninstall removes package files/shortcut/own keys, preserves both task-created user sentinels; stock VLC registry+profile metadata unchanged before/after. No real user media was used.
- Packaging/CLI unittest suite:14 passed. Python compileall passed. Agent CLI verify confirms artifact hashes; it does not stand in for runtime tests.

Scope: Windows11 x64 preview, not certification of every VLC4 feature. HiDPI,
light theme, network/DVD/Blu-ray and exhaustive saved-preference behavior are
not claimed. Native frontend performs library cleanup and CRT fflush BEFORE
self process termination to avoid static Qt DLL loader-lock finalization deadlock.
Embedded libVLC unchanged; no observer kills a successful test.
