# VLC Juxtopposed — Windows x64

## Goal / done when
Owner request: fork https://github.com/dsojevic/vlc/tree/juxtopposed-redesign, create project, build Windows installer. References: https://www.youtube.com/watch?v=ERFeOgqk324 and https://www.figma.com/community/file/1691465999134370980/vlc-redesign.
Done when fork contains exact redesign source plus reproducible build instructions, Windows x64 installer and portable build exist with hashes, executable runs and plays real test media, installer is smoke-tested in isolated directory, dashboard registered.

## Verified
- GitHub authenticated as dedakraeveda. Fork created: https://github.com/dedakraeveda/vlc.
- Source shallow clone at 43283e42a811e8b87ac95420eecd8947f60eb4a2, branch juxtopposed-redesign. origin=dedakraeveda, upstream=dsojevic.
- README contains original design attribution (CC BY 4.0), preserve software GPL/LGPL licenses.
- C free 17.94 GiB, D free 135.31 GiB before clone. All heavy work must use D.
- WSL Ubuntu BasePath D:\WSLUbuntu verified in registry. Root 7.7 GiB used. No Docker or cross compiler installed. Debian12 is on E and not used.
- Upstream CI image registry.videolan.org/vlc-debian-win64-posix:20260611225331. Native script extras/package/win32/build.sh supports x86_64 and installer -i n.

## Milestones / defects
- GitHub native build 38450252687 succeeded in 16m24s at binary source 5eb4de6e0a; exe/zip/7z downloaded and SHA256 all verified. This first payload is NOT a deliverable: GUI crashes and four plugins cannot load.
- Real H.264 playback reaches EOF / exit 0 but plugin-loading verification fails. Required DLL is libgcc_s_seh-1.dll -> libwinpthread-1.dll. Matching compiler runtime exported from same CI image in successful run 38453092154. Merely copying DLLs does not fix loading: src/win32/plugin.c only searches System32. Desktop loader patched to include executable directory only, never CWD/PATH.
- Native GUI checked with Orca, PID 3128: assertion at mainui.cpp:179, missing QML modules. Qt static contribs exclude Qt Labs and generic Controls plugin. All 17 redesign Controls imports changed to Controls.Basic. Replaced Qt Labs FolderListModel with native QDir/QFileSystemWatcher-backed RedesignFolderModel with same roles/get/count, sorting/filtering and filesystem refresh. GUI layout unchanged. Autotools and Meson registration updated.
- Safe separate per-user NSIS installer added: unique HKCU keys/Start menu shortcut, no stock VLC registration, no associations, exact-file uninstall preserves user/non-package files. Packaging tests: 3 PASS. Compiler package test exposed quote warnings; corrected NSIS uninstall/shortcut quote literals.
- Dashboard registered as building; sync completed, D:/Desktop/project-start/VLC — Juxtopposed redesign.lnk exists.
- Local Docker image pull stopped (exact PID 1610), network too slow; cloud build succeeds. Docker/nsis dependency install is machine-local in Ubuntu on D. No local full compile completed.
- Current native rebuild: https://github.com/dedakraeveda/vlc/actions/runs/38454233593 at e6efb4be93. Earlier 38454077735 cancelled before compile to incorporate loader fix.
- D free fell from 135.31 to 98.64 GiB during turn, mostly unrelated concurrent disk work (Ubuntu root remains ~8.4GiB, downloaded task artifacts <1GiB). C ~17.57GiB. Continue checks; no cleanup of other jobs/user data authorized.

## Latest milestone (after second rebuild)
- Run 38454233593 SUCCESS 26m7s, binary source e6efb4be93. Artifacts downloaded with all SHA256 verified.
- REAL Windows H.264 playback with --no-hw-dec: PASS, exit0, 4.53 sec, decoder avcodec + EOF, no plugin-load errors. Loader fix and exact compiler DLLs work.
- Native Orca snapshot PID17032/window22282768 shows only video, not redesign. Log proves root cause: RedesignPlayer -> RedesignPlayerView -> RedesignVolume unavailable, `Canvas is not a type`. Qt contrib explicitly disables quick_canvas. Replaced Canvas with the same existing SVG-image mechanism used by RedesignIcon; volume path/colors/fill preserved.
- Test process17032 closed/terminated after verified target identity. No blanket process termination. Firewall prompt appeared; no firewall allow/config change performed.
- Second payload moved to dist/failed-gui-canvas, so launch.py cannot open it as verified.
- Discovered native portable-profile support in src/win32/dirs.c. Installer/ZIP now include portable/README.txt, native resolver isolates configuration/cache/media-library. Uninstall removes only package files, retains subsequently created profile files. Shortcut points to that profile, no APPDATA/global VLC changes.
- Agent CLI (capabilities/status/preflight/plan/apply/verify) added. capabilities + exact GH identity preflight PASS; artifact integrity and runtime evidence are separate. launch.py points ONLY at final dist/verified/portable/VLC-Juxtopposed/vlc.exe.
- Current rebuild: https://github.com/dedakraeveda/vlc/actions/runs/38458425797 at 55a567101f. Includes Canvas fix, correct NSIS quotes and isolated profile in installer/ZIP. Prior binary/UI is not deliverable.

## Fourth compatibility issue / current source
- Run38458425797 SUCCESS 19m4s, source55a567101f. GUI now instantiates and real native controls work: Show library changes tree to Home/Videos/Music/etc.; Pause changes to Play. Canvas/type errors gone.
- Native screenshot reveals all data-URI SVG icons blank. GUI shuts down its main loop/log normally, but process hangs on exit; reproduced with both --play-and-exit and real Close button.
- Source diagnosis: Qt6.8.3 contrib has FEATURE_qml_network=OFF. Qt qquickpixmapcache.cpp treats any non-file/non-qrc/non-image-provider URL (including data:) as a network job; without qml_network, such jobs do not run. Reference: https://codebrowser.dev/qt6/qtdeclarative/src/quick/util/qquickpixmapcache.cpp.html (processJobs/processJob). Blank icons + shutdown hang are consistent with pending data: image jobs.
- Added RedesignSvgImageProvider using the SAME existing native ImageHelper SVG handler; no network, no Qt rebuild, no asset/style replacement. Bounded input64KiB/output4096px, rejects external image/href/DOCTYPE. RedesignIcon/volume now use image://redesignsvg/. Registered in MainUI. Current new patch still needs compile/runtime verification.
- Closed only confirmed firewall prompts HWND10094622 and27330870 owned byPickerHost11164 through WM_CLOSE; permission was not allowed. Both handles verified destroyed. Native screenshots may contain OS overlays; do not publish the full-screen capture (includes unrelated notifications). Keep only a clean bounded target-window image later.
- Test process20664 confirmed target; after Close it remained alive8sec, then was terminated. Failed payload moved to dist/failed-inline-svg. No launcher points to it.
- Added profile exclusion to packaging scripts (only portable/README.txt may ship), CLI concurrency/dirty-source/auth safeguards and14 unit tests, all PASS. Code changes since55 are not yet binary-tested.

## Next / not done
Commit fourth SVG provider patch and start native rebuild; diagnose if needed; download to dist/verified. Playback recheck, real Qt GUI startup/playback to normal exit with QML warnings checked (verify_runtime.py --gui now uses REAL Windows window, not unsupported offscreen). Native screenshot and UI interactions must show redesign, not only video. Custom installer install/uninstall in exact task scratch directory; own HKCU registry keys/shortcut must be absent before test and removed after, stock VLC registry and profile unchanged. Publish verified installer/portable release, update docs/task-state/dashboard and commit/push. Clean only exact task-created failed artifacts after process identity checks. C17.54/D97.49GiB after second artifact download; D unrelated growth stabilized.


