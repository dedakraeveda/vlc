#!/usr/bin/env bash
# Run inside D-backed WSL Ubuntu, from this project's Windows directory.
set -euo pipefail
PROJECT=$(cd -- "$(dirname -- "$0")" && pwd)
WORK=/root/vlc-juxtopposed
IMAGE=registry.videolan.org/vlc-debian-win64-posix:20260611225331
mkdir -p "$WORK" "$PROJECT/dist/local" "$PROJECT/build-logs"
if [ ! -d "$WORK/src/.git" ]; then
    git clone --no-hardlinks "$PROJECT" "$WORK/src"
else
    git -C "$WORK/src" fetch "$PROJECT" juxtopposed-redesign
    git -C "$WORK/src" merge --ff-only FETCH_HEAD
fi
mkdir -p "$WORK/build"
docker pull "$IMAGE"
docker run --name vlc-juxtopposed-build --rm --user root \
    --memory=10g --cpus=6 \
    -v "$WORK/src:/src" -v "$WORK/build:/build" -v "$PROJECT/dist/local:/artifacts" \
    -e JOBS=6 -e WINEDEBUG=-all -e WINEPREFIX=/build/wine \
    "$IMAGE" bash -lc '
        set -euo pipefail
        git config --global --add safe.directory /src
        export VLC_CONTRIB_SHA="$(cd /src; extras/ci/get-contrib-sha.sh win64)"
        export VLC_PREBUILT_CONTRIBS_URL="https://artifacts.videolan.org/vlc/win64/vlc-contrib-x86_64-w64-mingw32-${VLC_CONTRIB_SHA}.tar.zst"
        cd /build
        /src/extras/package/win32/build.sh -a x86_64 -p -i r
        bash /src/packaging/finish-build.sh /build/win64/vlc-4.0.0-dev /artifacts /build/nsis-work
    ' 2>&1 | tee "$PROJECT/build-logs/windows-build.log"
test -f "$PROJECT/dist/local/VLC-Juxtopposed-4.0-dev-win64-Setup.exe"
