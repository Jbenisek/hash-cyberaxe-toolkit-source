#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# per-coset rank runs: many cubes on the SAME coset, to get the span of the top-degree parts on one fixed coset
# args of cubes run: W40 SEED NCUBES K DIRMODE TSHARE DSHARE NVEC OUTPREFIX
set -e
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/s3-plane-degrees"
cd "$D"
./cubes run w40.txt 502 12000  2 span 2400 1 12000 runs/pcrank_k2
./cubes run w40.txt 504 12000  4 span 2400 1 12000 runs/pcrank_k4
./cubes run w40.txt 507 12000  7 span 2400 1 12000 runs/pcrank_k7
./cubes run w40.txt 508 12000  8 span 2400 1 12000 runs/pcrank_k8
./cubes run w40.txt 516 1200  16 span 600  1 1200  runs/pcrank_k16
