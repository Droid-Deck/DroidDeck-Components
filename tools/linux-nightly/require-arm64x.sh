#!/usr/bin/env bash
set -euo pipefail
for f in "$@"; do
  headers=$(llvm-readobj --file-headers "$f")
  loadcfg=$(llvm-readobj --coff-load-config "$f")
  grep -q -E 'IMAGE_FILE_MACHINE_ARM64X|IMAGE_FILE_MACHINE_ARM64 \(0xAA64\)' <<<"$headers" || { echo "::error::$f is not ARM64X"; exit 1; }
  grep -q CHPEMetadata <<<"$loadcfg" || { echo "::error::$f has no ARM64EC half"; exit 1; }
done
