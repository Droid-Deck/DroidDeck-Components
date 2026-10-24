#!/usr/bin/bash
set -euxo pipefail
cd /work
grep -q '^DisableSandbox' /etc/pacman.conf || sed -i 's/^\[options\]/[options]\nDisableSandbox/' /etc/pacman.conf
{ for m in https://ca.us.mirror.archlinuxarm.org https://fl.us.mirror.archlinuxarm.org https://de3.mirror.archlinuxarm.org https://nl.mirror.archlinuxarm.org; do echo "Server = $m/\$arch/\$repo"; done; cat /etc/pacman.d/mirrorlist; } > /etc/pacman.d/mirrorlist.new
mv /etc/pacman.d/mirrorlist.new /etc/pacman.d/mirrorlist
pacman -Syu --noconfirm --needed git zstd binutils python python-mako python-packaging python-yaml python-pycparser \
  meson ninja cmake pkgconf flex bison glslang spirv-tools spirv-headers vulkan-headers vulkan-icd-loader \
  wayland wayland-protocols libx11 libxext libxdamage libxcomposite libxrender libxres libxtst libxxf86vm libxmu \
  libxkbcommon libxcursor libxi libxrandr libxfixes libxshmfence libxcb xcb-util-wm xcb-util-errors xcb-util-renderutil \
  libdrm libinput seatd libdisplay-info hwdata xorg-xwayland pixman sdl2 luajit glm stb libdecor lcms2 libcap \
  libglvnd expat zlib elfutils
cd dd
J=$(nproc)
python3 tools/qualcomm/build_gamescope.py --jobs "$J"
python3 tools/qualcomm/build_zink.py --jobs "$J"
python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, 'tools/qualcomm')
from fetch_runtime import fetch
fetch(Path('build/qualcomm-cache'), json.loads(Path('tools/qualcomm/runtime.json').read_text())['wsi'])
PY
python3 tools/qualcomm/build_wsi.py --jobs "$J"
NEEDED=$(readelf -d build/qualcomm-gamescope/gamescope | sed -n 's/.*NEEDED.*\[\(.*\)\]/\1/p')
echo "gamescope NEEDED: $NEEDED"
MISSING=""
for lib in $NEEDED; do grep -qx "$lib" tools/gamescope/runtime-sonames.txt || MISSING="$MISSING $lib"; done
if [ -n "$MISSING" ]; then echo "ERROR: not in the runtime:$MISSING"; exit 3; fi
cd build
tar --sort=name --owner=0 --group=0 --numeric-owner --mtime=@0 --exclude='*/source' --exclude='*/source/*' \
  -cf /work/qualcomm-builds.tar qualcomm-gamescope qualcomm-zink/runtime qualcomm-wsi
cd /work
zstd -19 -f --rm qualcomm-builds.tar -o qualcomm-builds.tar.zst
sha256sum qualcomm-builds.tar.zst | tee qualcomm-builds.tar.zst.sha256
cp dd/build/qualcomm-gamescope/build.json gamescope-build.json
cp dd/build/qualcomm-zink/runtime/build.json zink-build.json
cp dd/build/qualcomm-wsi/build.json wsi-build.json
tar -tf qualcomm-builds.tar.zst --use-compress-program=unzstd
