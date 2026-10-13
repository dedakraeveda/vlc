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

## Next / not done
Wait for rebuild, diagnose failures, download to dist/verified (do not overwrite first artifacts). Verify plugins + real playback, real GUI window screenshot/interactions, custom installer install/uninstall in exact scratch directory with own registry keys, verify stock VLC untouched. Locally regenerate installer if needed to apply final packaging quote fix. Publish verified installer/portable as GitHub release, update README/task-state/dashboard and source commits. Qt offscreen is not supported by this static Qt image; do not count it as visual proof.

