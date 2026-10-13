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

## Plan / next
Use Ubuntu WSL on D and upstream CI container. Keep source/build/docker data on D-backed distro; export artifacts to project dist. Fetch enough git history for contrib SHA; reuse exact prebuilt contribs if available, otherwise compile. Check disk between stages.

## Not done
Build, installer, runtime smoke, dashboard registration.
