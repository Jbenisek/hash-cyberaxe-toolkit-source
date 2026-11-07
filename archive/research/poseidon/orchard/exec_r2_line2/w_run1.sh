#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# RR=1 comparison run: old (exec_r2_line, libc) then new (nolibc); sequential, nice 19
D="${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard
mkdir -p /tmp/r2l2
cd $D/exec_r2_line || exit 1
gcc -O3 -march=native -static -DRR=1 -o /tmp/r2l2/old1 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c -lm 2>/tmp/r2l2/gcc_old.err || { echo OLD BUILD FAILED; head /tmp/r2l2/gcc_old.err; exit 2; }
cd $D/exec_r2_line2 || exit 1
( ulimit -s 64; date; nice -n 19 /tmp/r2l2/new1 1 > /tmp/r2l2/new1.txt 2>&1; echo "EXIT $?" >> /tmp/r2l2/new1.txt; date )
( ulimit -s 64; date; nice -n 19 /tmp/r2l2/old1 1 > /tmp/r2l2/old1.txt 2>&1; echo "EXIT $?" >> /tmp/r2l2/old1.txt; date )
