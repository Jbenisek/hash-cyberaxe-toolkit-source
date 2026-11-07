#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: the one quoted SHA-256 that fig_schema.py did not locate
P="${HASHCYBERAXE_WORKSPACE}"/research
for f in $(find "$P/night" "$P" -maxdepth 2 -name 'e3partial.c' 2>/dev/null | sort -u); do
  echo "$(sha256sum "$f" | cut -c1-16) ${f#$P/}"
done | head -4
echo "quoted: b2699a84d60a5d0f"
