#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Step 2: brute force at 8-bit words for the counter with a cube and three-bit parities (sub_bf.c).
#   c02_bf.sh smoke        one small run (1 case of part A, 1 of part B)
#   c02_bf.sh all [T]      five runs, results in bf8_sub.txt (this folder); T threads (default 4), nice -n 5
set -uo pipefail
H="${HASHCYBERAXE_WORKSPACE}/research/pkg7/count"
S="$HOME/hashsmash/pkg7_count"; B="$S/bin"; O="$S/out"
cd "$H" || exit 3
T=${2:-4}
t0=$(date +%s)
if [ "${1:-smoke}" = smoke ]; then
  OMP_NUM_THREADS=$T nice -n 5 "$B/sub_bf8" 1 1 7 > "$O/bf_smoke.txt" 2>&1
  echo "smoke exit $? seconds $(( $(date +%s) - t0 ))"; cut -c1-420 "$O/bf_smoke.txt" | tail -7; exit 0
fi
{ echo "sources sha256: n3r.inc $(sha256sum n3r.inc | cut -c1-16) pair_calc_sub.c $(sha256sum pair_calc_sub.c | cut -c1-16) sub_bf.c $(sha256sum sub_bf.c | cut -c1-16); binary $(sha256sum "$B/sub_bf8" | cut -c1-16); $(date '+%Y-%m-%d %H:%M')"
  echo "RUN 1: sub_bf8 3 5 7001 (pruned search, cubes)"
  OMP_NUM_THREADS=$T nice -n 5 "$B/sub_bf8" 3 5 7001; echo "exit status $?"
  echo "RUN 2: sub_bf8 2 4 7002 (pruned search, cubes)"
  OMP_NUM_THREADS=$T nice -n 5 "$B/sub_bf8" 2 4 7002; echo "exit status $?"
  echo "RUN 3: H8_NOCUT=1 sub_bf8 0 4 7003 (unpruned search of pair_calc.c, cubes)"
  H8_NOCUT=1 OMP_NUM_THREADS=$T nice -n 5 "$B/sub_bf8" 0 4 7003; echo "exit status $?"
  echo "RUN 4: RULE_BF_CAPWORK=5 sub_bf8 0 4 7004 (pruned search, cubes; n3r_orig left out above 2^5 triples)"
  RULE_BF_CAPWORK=5 OMP_NUM_THREADS=$T nice -n 5 "$B/sub_bf8" 0 4 7004; echo "exit status $?"
  echo "RUN 5: SUB_BF_NOCUBE=1 sub_bf8 1 2 7005 (no cube: the counter of rule_exact with the new kinds of rules)"
  SUB_BF_NOCUBE=1 OMP_NUM_THREADS=$T nice -n 5 "$B/sub_bf8" 1 2 7005; echo "exit status $?"
} > "$O/bf8_sub.txt" 2>&1
cp "$O/bf8_sub.txt" "$H/bf8_sub.txt"
echo "seconds $(( $(date +%s) - t0 )); runs with zero differences $(grep -c 'zero differences' "$O/bf8_sub.txt") of 5; lines with a mismatch $(grep -c -E 'MISMATCH|DIFFERENCES' "$O/bf8_sub.txt")"
