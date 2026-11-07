#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# convert every PDF in papers/ to text (pdftotext if present)
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/scout_cross/papers || exit 1
which pdftotext || { echo "no pdftotext"; exit 0; }
for f in *.pdf; do
  t="${f%.pdf}.txt"
  [ -s "$t" ] || timeout 60 pdftotext -layout "$f" "$t"
  echo "$t $(wc -l < "$t")"
done
