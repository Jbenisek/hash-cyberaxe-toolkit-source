#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard/exec_r2_line2 || exit 1
CF="-O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -DARENA=167772160"
gcc $CF -o /tmp/r2l2/trace single.c w_common_trace.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c || exit 2
( ulimit -s 64; date; nice -n 19 /tmp/r2l2/trace 1 > /tmp/r2l2/trace_out.txt 2> /tmp/r2l2/trace_ev.txt; echo "EXIT $?" >> /tmp/r2l2/trace_out.txt; date )
