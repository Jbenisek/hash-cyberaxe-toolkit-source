#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: sizes and sha256 of the package files (read only)
P="${HASHCYBERAXE_WORKSPACE}"/research
O="$P/pkg5/review/fig_sizes.out"
{
for f in blake3-r2/proof.md blake3-r2/claim.json submission-note-r2.md blake3-r2/experiments/halfsearch.py blake3-r2/experiments/manifest.json blake3-r2/certificates/manifest.json src/proof_head.md src/proof_evidence.md src/claim.json src/note.md src/manifest.json; do
  for k in pkg4 pkg5; do
    if [ -f "$P/$k/$f" ]; then
      echo "$k $f lines=$(wc -l < "$P/$k/$f") bytes=$(wc -c < "$P/$k/$f") sha=$(sha256sum "$P/$k/$f" | cut -d' ' -f1)"
    else
      echo "$k $f MISSING"
    fi
  done
done
} > "$O" 2>&1
wc -l "$O"
