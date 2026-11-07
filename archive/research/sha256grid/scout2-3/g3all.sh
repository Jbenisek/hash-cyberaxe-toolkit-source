#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# G3: (a) variant-dispersion study, one fresh uniform variant per run (R2 design), 65536 runs, master 20261012;
#     (b) pool-size check, 4096 runs with 65536 fresh variants each (2^28 variants), master 20261011;
#     (c) exact |R_j| recount of all 256 A0 against proof.md A.2 (population definition of the sampler).
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
./q3gpu2 gpusmc 20261012 0 65536 4000 2048 64 64 8 8 4 8192 1 g3_v1 1
tail -1 g3_v1.log
./q3gpu2 gpusmc 20261011 0 4096 4000 2048 64 64 8 8 4 8192 65536 g3_pool 1
tail -1 g3_pool.log
./exactR $(seq 0 255) > exactR_all.txt
awk '{d += ($9 != "+0")} END {print NR " A0 recounted, " d " differ from proof.md A.2"}' exactR_all.txt
