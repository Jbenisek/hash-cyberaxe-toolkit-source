#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# period-k ('tandem repeat') follow-up: d-palindrome check at w=32 and the exhaustive period-k characteristic scan
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
gcc -O3 -march=native -o nature2 nature.c -lm 2> build2.err || { cat build2.err; exit 1; }
gcc -O3 -march=native -o p4enum p4enum.c 2> build3.err || { cat build3.err; exit 1; }
echo "quick4 pid $$ start $(date)" >> pids.txt
{
timeout 300 ./nature2 dpal 32 88888888 201 268435456
timeout 300 ./nature2 dpal 32 11111111 202 268435456
timeout 300 ./nature2 dpal 12 888 203 16777216
timeout 300 ./nature2 dpal 16 aaaa 204 16777216
timeout 300 ./nature2 dpal 16 8888 205 16777216
./p4enum p1_basis.txt
./p4enum p2_basis.txt
timeout 3000 ./p4enum p4_basis.txt
} > quick4.out 2>&1
echo "quick4 done $(date)" >> pids.txt
