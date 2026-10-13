# VLC Juxtopposed — Windows x64

## Current status — acceptance PASSED
DONE: https://github.com/dedakraeveda/vlc/releases/tag/juxtopposed-win64-preview-1 — published non-draft prerelease,3 assets. Compiled source41e9278452, run38470541761 SUCCESS21m52s. Verified installer/portable in dist/verified; failed builds below are historical, NOT deliverables. See review/final-verification.md and RELEASE-NOTES.md. Live published asset sizes+SHA256 match local files; actual public SHA256SUMS downloaded and verified.

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

## Fourth build / shutdown diagnosis
- Run38463055545 SUCCESS, source db6279df2c. Downloaded installer/ZIP with verified CI SHA256; extracted fresh dist/verified.
- Native screenshot PID32552 HWND9897344, bounded1080x700: ALL SVG icons visible, actual video, full controls and volume gradient correct. No QML/provider errors. SVG patch fixes rendering, but did NOT fix shutdown.
- Both --play-and-exit and real Close finish libVLC/Qt cleanup and logging, yet leave ONE main thread alive. No active playback/UI threads remain.
- Diagnosed only own process thread30912 via GetThreadContext and module-matched stack pointers (no memory dump/environment content). RIP ntdll+0x1625e4; caller pointers libqt_plugin+0x33bec/+0x33eb6. Disassembly shows semaphore/multiple-object wait inside static Qt DLL finalization, reached after process-wide thread teardown. Process32552 terminated only after this diagnosis.
- Added standalone MinGW WinVLC self-TerminateProcess ONLY after libvlc_release, crash-handler release and argv cleanup. Avoids unsafe DLL_PROCESS_DETACH under loader lock; embedded libVLC unchanged. Microsoft explicitly documents this deadlock and recommends TerminateProcess when peer thread state is unknown: https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-exitprocess . New native frontend must be rebuilt/verified; do not claim normal DLL destructors run.
- Runtime helper now uses file stderr + proc.wait (no inherited-pipe false timeout), reports timedOut; turns off upstream crash dump, autoresize/resume. Source frontend WinVLC hardcodes shared crashdump path, so launcher/NSIS shortcut now pass --no-crashdump; direct portable launch must do so too. Profile/registry tests use a real temporary install, Win32 COM shortcut assertions, actual installed playback and uninstall sentinels. verify_installer.py implemented but NOT YET RUN.
- Updated user/build docs and finish-build to include actual README attribution. Final packaging includes new shortcut flags and explicit working directory.

## Independent review and current build
- Gemini/AGY plan review attempted via official AskAntigravity; blocked by Antigravity account regional eligibility. No credential/proxy/region change attempted. Alternative official Claude Code CLI read-only restricted/safe mode succeeded; review/independent-review.md contains actual code+image review.
- Reviewer confirms all visible SVG controls, seek/time alignment, volume shape/colors; no visual basic-scenario blocker. Runtime must still prove process exit and saved state. Important finding: fflush(NULL) required before self-TerminateProcess to preserve buffered CRT output; added.
- Original icon paths unchanged vs upstream43283e42: only source URL scheme changed. Existing light-theme/alpha/HiDPI caveats are inherited/advisory, not reason to replace the requested original design.
- DESIGN.md records original QML token system and explicit native/desktop/DOM exceptions. Clean review/player-native.png contains only generated test media + own UI (external transparent frame cropped); no OS notifications.
- Run38468422179 at71c931490f cancelled at16m34s to include required CRT flush before release. CURRENT RUN: https://github.com/dedakraeveda/vlc/actions/runs/38470541761 at41e9278452. Full native compile, final per-user installer/README attribution and shortcut flags all included; no local binary patching.

## Final verified results
- Fresh CI artifacts downloaded, both SHA256 verified; no local binary patching. Source41e9278452.
- Portable H.264 decoder+EOF exit0/4.42s/no timeout; Qt startup+decoder+EOF exit0/4.94s/no timeout. Runtime helper now additionally requires decoder and EOF for GUI success.
- Actual final native UI PID33328 HWND114820178 at1440x820: all SVG icons/volume rendered, Pause becomes Play, Show library adds navigation, Music adds Songs/Albums/Artists/Genres, Queue lists actual synthetic test-video.mp4. Real Close removes process; NO external termination. No leftover vlc.exe processes. Actual images only own content, cropped external transparent margin: review/*-final.png.
- verify_installer.py --authorized PASS: actual per-user install to exact D scratch,538 files match ZIP, .lnk target/args/workingdir + own HKCU verified, installed H.264 playback exit0/4.47s, uninstall removes own files/keys/link and preserves user sentinels; stock VLC registry/profile metadata unchanged. No silent replacement of existing installation. Shortcut contents validated, not an asserted ShellExecute/manual wizard test.
- Python compileall PASS,14 unittest PASS, agent_cli verify confirms both hashes. PE certificate directory absent for Setup+vlc.exe: unsigned.
- Two real independent Claude Code read-only image/code reviews; second finds no basic-scenario code/image blocker. Important doc finding fixed in DESIGN.md; original upstream icon paths unchanged, remaining light-theme/HiDPI/global-finalizer caveats documented, not silently refactored.
- Dashboard active, registry description updated, sync.py run. Folder shortcut intentionally opens project/artifacts rather than a generated console/browser launcher. WSL dependencies/partial Docker cache are machine-local on D; never transferred devices. No complete local compile claimed.
- Disk C17.94GiB before task ->15.77GiB near finish; D135.31->100.13GiB with concurrent unrelated work. Task heavy downloads/extraction, archives/build temp on D; final dist/verified383,217,517 bytes including extracted payload. Historical failed payloads remain isolated on D; own installer sentinels remain in D scratch, actual installed package removed. No other user data or OpenAICodexTray directories touched.

## Delivery complete / rollback
- Source/evidence commit ec7d85f712 pushed; release tag juxtopposed-win64-preview-1 created without rewriting prior tags. Binary native source remains41e9278452; later commits are docs/verification only.
- Live GitHub release3 uploaded assets; digest+size exact for all3. Public215-byte SHA256SUMS fetched via download_with_progress, verifiedSHA90a078975a0126a7808ca52c1a8bf1e82bc5e0347de305d811cc147f5f7a8887.
- Final dashboard sync completed; actual shortcut D:/Desktop/project-start/Projects/Folders/VLC — Juxtopposed redesign.lnk targets existing C:/Windows/explorer.exe with quoted existing project folder argument. No generated console/browser launcher used.
- Finish disk C15.73GiB/D100.13GiB. C remains below20GiB; all task heavy files on verified D, no unrelated cleanup performed. Final assets+extracted payload ~365.5MiB on D; historical failed outputs and D WSL partial image/dependencies retained for diagnostics, own uninstall sentinel files retained.
- No remaining acceptance blocker. Known preview limits are explicit in RELEASE-NOTES. Gemini regional block was handled via existing Claude Code CLI, no auth/proxy mutation; AGY group loaded for this session only. No Pi resource files or cross-device credentials changed.
- Rollback: uninstall only own app, preserve profile; revert fork commits only if requested. Experimental VLC4, no exhaustive all-codec/network/HiDPI/preferences certification.


