#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard/single_r1_exec7 || exit 1
CF="-O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
mkdir -p /tmp/calib6
gcc $CF -DARENA=12582912 -o /tmp/calib6/single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c 2> logs/calib_gcc.err || { echo BUILD FAILED; head -30 logs/calib_gcc.err; exit 2; }
head -c 2000 logs/calib_gcc.err
( ulimit -s 64; nice -n 19 /tmp/calib6/single 1 > logs/calib_run.txt 2>&1; echo "EXIT $?" >> logs/calib_run.txt )
grep -E "ARENA|SUMMARY|RECONCILE|EXIT" logs/calib_run.txt
