#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
S="${HASHCYBERAXE_WORKSPACE}"/research/tools/build_pkg/scratch/pkgB3V
nproc; cat /proc/loadavg
cp "$S/pkg/blake3-r2/experiments/frontline.py" /tmp/u08_F.py
for rep in 3 4 5; do /usr/bin/time -f "cpu_user=%U wall=%e" python3 $S/work/drive.py /tmp/u08_F.py 256 "u08fresh$rep" | cut -c1-90; done
rm -f /tmp/u08_F.py
