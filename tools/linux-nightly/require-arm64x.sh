#!/usr/bin/env bash
set -euo pipefail
for f in "$@"; do
  llvm-readobj --file-headers "$f" | grep -q -E 'IMAGE_FILE_MACHINE_ARM64X|IMAGE_FILE_MACHINE_ARM64 \(0xAA64\)' || { echo "::error::$f is not ARM64X"; exit 1; }
  llvm-readobj --coff-load-config "$f" | grep -q CHPEMetadata || { echo "::error::$f has no ARM64EC half"; exit 1; }
done
