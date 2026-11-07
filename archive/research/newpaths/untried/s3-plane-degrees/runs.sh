#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# main GPU runs: per-bit cube-sum statistics at every stage, cube dims 1..9, 15, 16, 17
# args of cubes run: W40 SEED NCUBES K DIRMODE TSHARE DSHARE NVEC OUTPREFIX
set -e
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/s3-plane-degrees"
cd "$D"
mkdir -p runs
# random independent span directions, a fresh random coset per cube
./cubes run w40.txt 101 20000  1 span 1 1 4000 runs/span_k1
./cubes run w40.txt 102 20000  2 span 1 1 4000 runs/span_k2
./cubes run w40.txt 103 20000  3 span 1 1 4000 runs/span_k3
./cubes run w40.txt 104 20000  4 span 1 1 4000 runs/span_k4
./cubes run w40.txt 105 20000  5 span 1 1 4000 runs/span_k5
./cubes run w40.txt 106 20000  6 span 1 1 4000 runs/span_k6
./cubes run w40.txt 107 200000 7 span 1 1 4000 runs/span_k7
./cubes run w40.txt 108 400000 8 span 1 1 6000 runs/span_k8
./cubes run w40.txt 109 20000  9 span 1 1 2000 runs/span_k9
./cubes run w40.txt 115 8000  15 span 1 1 2000 runs/span_k15
./cubes run w40.txt 116 8000  16 span 1 1 2000 runs/span_k16
./cubes run w40.txt 117 400   17 span 1 1 400  runs/span_k17
# random k-subsets of the 40 basis vectors (monomial coefficients)
./cubes run w40.txt 202 20000  2 basis 1 1 4000 runs/basis_k2
./cubes run w40.txt 204 20000  4 basis 1 1 4000 runs/basis_k4
./cubes run w40.txt 207 200000 7 basis 1 1 4000 runs/basis_k7
./cubes run w40.txt 208 400000 8 basis 1 1 4000 runs/basis_k8
./cubes run w40.txt 216 4000  16 basis 1 1 1000 runs/basis_k16
# per-coset: 300 cosets x 64 cubes on the same coset (all vectors kept)
./cubes run w40.txt 302 19200  2 span 64 1 19200 runs/coset_k2
./cubes run w40.txt 304 19200  4 span 64 1 19200 runs/coset_k4
./cubes run w40.txt 308 19200  8 span 64 1 19200 runs/coset_k8
./cubes run w40.txt 307 19200  7 span 64 1 19200 runs/coset_k7
# t-dependence of the top-degree part: 500 direction sets, each on 16 cosets
./cubes run w40.txt 402 8000   2 span 1 16 8000 runs/tdep_k2
./cubes run w40.txt 404 8000   4 span 1 16 8000 runs/tdep_k4
./cubes run w40.txt 408 8000   8 span 1 16 8000 runs/tdep_k8
./cubes run w40.txt 416 1600  16 span 1 16 1600 runs/tdep_k16
ls -la runs | head -80
