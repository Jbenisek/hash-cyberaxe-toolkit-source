#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build and quick self-check (counter/value)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/value
cd "$D" || exit 1
gcc -O3 -march=native -o ctr_rates ctr_rates.c -lm 2> build.err || { cat build.err; exit 1; }
./ctr_rates check 3000 7 > check_out.txt
echo "built; check lines: $(grep -c TRIAL check_out.txt)"
time ./ctr_rates rates 6 16 1 1 1 > smoke_rates.txt
cat smoke_rates.txt | head -30
