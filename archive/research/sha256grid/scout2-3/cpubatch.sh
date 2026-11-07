#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# CPU fallback lane (no GPU): full PREREG_v3 parameters, fresh 4096-variant pool per run.
# usage: cpubatch.sh lane master seconds   (lane 0/1 takes run indices lane, lane+2, ...)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
lane=$1; master=$2; deadline=$(( $(date +%s) + $3 ))
echo $$ > cpubatch_lane${lane}.pid
r=$lane
while [ "$(date +%s)" -lt "$deadline" ]; do
  ./q3gpu cpusmc "$master" "$r" 4000 2048 64 64 8 8 4 8192 4096 >> "cpu_m${master}_lane${lane}.log" 2>&1
  r=$((r + 2))
done
echo "# lane $lane done $(date)" >> "cpu_m${master}_lane${lane}.log"
