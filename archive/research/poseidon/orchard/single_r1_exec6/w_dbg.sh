#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard/single_r1_exec6 || exit 1
CF="-O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -DDBG"
gcc $CF -o /tmp/calib6/dbg single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c > logs/dbg_gcc.txt 2>&1
ulimit -s 64; timeout 200 /tmp/calib6/dbg 1 > logs/dbg_run.txt 2>&1; echo "EXIT $?" >> logs/dbg_run.txt
