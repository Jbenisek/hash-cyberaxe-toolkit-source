#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Build gen and write both sample sets. Seeds fixed; output is deterministic.
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/data" || exit 1
gcc -O2 -Wall -o gen gen.c 2>&1 | head -30
mkdir -p rand ctx
/usr/bin/time -f "rand: %e s" ./gen rand rand 1048576 0x5045525350310001 > rand/gen_out.txt 2>&1; echo "rand exit $?" >> rand/gen_out.txt
/usr/bin/time -f "ctx: %e s" ./gen ctx ctx 16 16 1024 0x5045525350310002 > ctx/gen_out.txt 2>&1; echo "ctx exit $?" >> ctx/gen_out.txt
cat rand/gen_out.txt ctx/gen_out.txt
ls -l rand ctx
