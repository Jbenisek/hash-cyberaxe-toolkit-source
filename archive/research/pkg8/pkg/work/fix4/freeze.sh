#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# FIX4 freeze: regenerate FROZEN_fix.sha256 and FROZEN_fix_note.sha256, then verify -c.
set -e
P="${HASHCYBERAXE_WORKSPACE}/research/pkg8/pkg"
cd "$P/blake3-r2"
sha256sum ./certificates/manifest.json ./claim.json ./experiments/halfsearch.py ./experiments/manifest.json ./proof.md > "$P/FROZEN_fix.sha256"
cd "$P"
sha256sum --binary submission-note-r2.md > "$P/FROZEN_fix_note.sha256"
echo '--- FROZEN_fix.sha256 ---'
cat "$P/FROZEN_fix.sha256"
echo '--- FROZEN_fix_note.sha256 ---'
cat "$P/FROZEN_fix_note.sha256"
echo '--- verify -c (from blake3-r2) ---'
cd "$P/blake3-r2" && sha256sum --quiet -c "$P/FROZEN_fix.sha256" && echo FROZEN_FIX_OK
cd "$P" && [ "$(sha256sum submission-note-r2.md | cut -c1-64)" = "$(cut -c1-64 "$P/FROZEN_fix_note.sha256")" ] && echo FROZEN_NOTE_OK
