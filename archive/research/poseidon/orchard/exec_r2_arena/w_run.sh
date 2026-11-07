#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build with ARENA (arg1, default 64 MiB) and run once under a 64 KiB stack, nice 10; writes to /root/arena_r2/<arena>
A=${1:-67108864}; XF=${2:-}; D=/root/arena_r2/$A$3; mkdir -p $D
cd "${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/exec_r2_arena"
gcc -O3 -march=native -static -DARENA=$A $XF -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -o $D/single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c -lm 2>&1 | head -20
size $D/single > $D/size.txt; cat $D/size.txt
cd $D; ( ulimit -s 64; ATRACE=$D/trace.txt nice -n 10 /usr/bin/time -v -o $D/time.txt ./single 1 > $D/run.txt 2>&1; echo "EXIT $?" >> $D/run.txt )
grep -E "peak|SUMMARY|PEAKLIVE|RECONCILE|EXIT" $D/run.txt | tail -8; grep -E "Maximum resident" $D/time.txt
