# VLC Juxtopposed — Windows x64

Fork: https://github.com/dedakraeveda/vlc/tree/juxtopposed-redesign
Upstream: https://github.com/dsojevic/vlc/tree/juxtopposed-redesign
Original source revision: `43283e42a811e8b87ac95420eecd8947f60eb4a2`.

This is the native VLC 4 development tree with Juxtopposed's Qt/QML redesign,
not an Electron wrapper or a skin for VLC 3. It is an unofficial experimental build.
Preserve README's Juxtopposed CC BY 4.0 credit, COPYING and COPYING.LIB.

Design references:
- https://www.youtube.com/watch?v=ERFeOgqk324
- https://www.figma.com/community/file/1691465999134370980/vlc-redesign

## Build

GitHub Actions: run **Windows x64 redesign** on `juxtopposed-redesign`.
Download the `vlc-juxtopposed-win64` artifact after successful completion.
The workflow uses the image/version declared by this source tree's upstream CI,
exact contrib source SHA, and VLC's own NSIS packaging (not a substitute installer).
The installer is unsigned; no Windows code-signing identity is available.

Local machine: Ubuntu WSL2 lives at `D:\WSLUbuntu`, with Docker Engine installed
inside that distro. From the project directory inside WSL:

```sh
bash build-local.sh
```

Source/build/image storage: `/root/vlc-juxtopposed` and `/var/lib/docker`,
`/var/lib/containerd` inside the D-backed Ubuntu VHDX. Outputs: `dist/`.
Wine prefix is task-local. No Docker Desktop or C-backed build is used.
The image is about 2.4 GB compressed; allow 25–40 GB peak space for image,
contribs, compilation, packaging and temporary data. Local compilation is
limited to 6 CPUs / 10 GiB RAM. On a clean system, install Docker first.

## Verification status

See `TASK-STATE.md` for actual verified milestones. A running/queued workflow
is not a successful build. Installer and playback tests are not yet complete.

## Safety / rollback

Do not replace the user's existing VLC installation or change file associations
for smoke tests. Use a separate portable directory and explicit test profile.
Remove only task-created smoke files when finished. Fork/local commits are
additive; upstream UI code remains unchanged. No automatic profile migration.
