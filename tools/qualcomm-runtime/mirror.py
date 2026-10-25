"""Download the bridge and WSI archives that runtime.json pins and keep them only when they match the pins.

usage: mirror.py <runtime.json> <output directory>
Writes the archives, mirror.json (name, sha256, size, original URL) and MIRROR.md for the release notes.
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path


def entries(lock):
    bridge = lock['provenance']['producer_commit'][:8]
    return [(f'hybris-runtime-{bridge}.tzst', lock, 'libhybris Vulkan bridge runtime'),
            (Path(lock['wsi']['url']).name, lock['wsi'], 'ARM Vulkan WSI layer archive')]


def main(lock_path, output):
    lock = json.loads(Path(lock_path).read_text())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    mirrored = []
    for name, pin, what in entries(lock):
        with urllib.request.urlopen(pin['url'], timeout=300) as source:
            data = source.read()
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != pin['size'] or digest != pin['sha256']:
            raise SystemExit(f'{pin["url"]}: got {len(data)} bytes sha256 {digest}, pinned {pin["size"]} {pin["sha256"]}')
        (output / name).write_bytes(data)
        mirrored.append(dict(name=name, what=what, sha256=digest, size=len(data), source=pin['url']))
    (output / 'mirror.json').write_text(json.dumps(mirrored, indent=2) + '\n')
    lines = ['Mirrored unchanged from [wallentx/DroidDeck](https://github.com/wallentx/DroidDeck) (credit: wallentx), '
             'checked against the pins in `tools/qualcomm/runtime.json`:', '']
    lines += [f'- `{m["name"]}` - {m["what"]}, {m["size"]} bytes, sha256 `{m["sha256"]}`, from {m["source"]}' for m in mirrored]
    (output / 'MIRROR.md').write_text('\n'.join(lines) + '\n')
    for m in mirrored:
        print(m['name'], m['sha256'], m['size'])


if __name__ == '__main__':
    main(*sys.argv[1:])
