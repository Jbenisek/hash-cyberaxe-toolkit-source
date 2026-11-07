#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
S="${HASHCYBERAXE_WORKSPACE}"/research/tools/build_pkg/scratch/pkgB3V
D=$S/work/drive.py
for p in pkg/blake3-r2/experiments/frontline.py work/frontline_base.py; do
 echo "== $p"; cp "$S/$p" /tmp/u08_F.py
 for rep in 1 2; do python3 $D /tmp/u08_F.py 256 "u08fresh$rep" ; done
done
rm -f /tmp/u08_F.py
