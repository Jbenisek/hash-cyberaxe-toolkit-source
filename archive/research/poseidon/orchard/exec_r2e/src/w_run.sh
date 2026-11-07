#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build (static) and run the counted run once; logs to ../logs
set -u
HERE="${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/exec_r2e"
mkdir -p /root/b_r2e "$HERE/logs"
cd "$HERE/src"
gcc -O3 -march=native -static -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -o /root/b_r2e/exec_attack exec_attack.c common.c ntt.c poly.c lean.c line.c euclid.c hgcd.c pallas.c -lm > "$HERE/logs/gcc.txt" 2>&1 || { echo BUILD FAILED; head -30 "$HERE/logs/gcc.txt"; exit 2; }
size /root/b_r2e/exec_attack > "$HERE/logs/size.txt"
if [ "${1:-}" = build ]; then echo built; exit 0; fi
cd /root/b_r2e
( ulimit -s 64; nice -n 10 /usr/bin/time -v -o "$HERE/logs/time_v.txt" ./exec_attack 1 > "$HERE/logs/exec_run.tmp" 2>&1; echo "EXIT $?" >> "$HERE/logs/exec_run.tmp" )
mv "$HERE/logs/exec_run.tmp" "$HERE/logs/exec_run.txt"
