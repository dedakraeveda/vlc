#!/usr/bin/env bash
set -euo pipefail
SOURCE=$(cd -- "$(dirname -- "$0")/.." && pwd)
PAYLOAD=$(realpath "$1")
OUTPUT=$(realpath -m "$2")
WORK=$(realpath -m "$3")
mkdir -p "$OUTPUT" "$WORK"
# Static contrib archives can still contain GCC's shared exception unwinder.
for name in libgcc_s_seh-1.dll libwinpthread-1.dll; do
    path=$(x86_64-w64-mingw32-gcc -print-file-name="$name")
    test -f "$path"
    cp "$path" "$PAYLOAD/"
done
x86_64-w64-mingw32-gcc --version > "$PAYLOAD/COMPILER.txt"
find /usr/share/doc -path '*mingw*' -name copyright -exec sh -c 'echo "===== $1 ====="; cat "$1"' sh {} \; > "$PAYLOAD/COMPILER-LICENSES.txt"
test -s "$PAYLOAD/COMPILER-LICENSES.txt"
cp "$SOURCE/COPYING.LIB" "$PAYLOAD/COPYING.LIB.txt"
cp "$SOURCE/WINDOWS-REDESIGN.md" "$PAYLOAD/WINDOWS-REDESIGN.txt"
mkdir -p "$PAYLOAD/portable"
cp "$SOURCE/packaging/PROFILE-README.txt" "$PAYLOAD/portable/README.txt"
python3 "$SOURCE/packaging/build_installer.py" --payload "$PAYLOAD" \
    --output "$OUTPUT/VLC-Juxtopposed-4.0-dev-win64-Setup.exe" --work "$WORK"
python3 "$SOURCE/packaging/portable_archive.py" --payload "$PAYLOAD" \
    --output "$OUTPUT/VLC-Juxtopposed-4.0-dev-win64-portable.zip"
cd "$OUTPUT"
sha256sum *.exe *.zip > SHA256SUMS
