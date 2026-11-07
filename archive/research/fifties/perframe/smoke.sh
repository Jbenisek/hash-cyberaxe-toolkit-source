#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perframe"
mkdir -p dbg
read K1 K2 < <(python3 -B seeds.py debug)
for a in 0 1; do for g in 1 2; do
./perframe val $a $g $([ $g = 1 ] && echo $K1 || echo $K2) 0 2 8 16 dbg/s_a${a}_g${g}.bin
done; done
python3 -B ref_pf.py val $K1 $K2 dbg/s_a0_g1.bin dbg/s_a1_g1.bin dbg/s_a0_g2.bin dbg/s_a1_g2.bin
