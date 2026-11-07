#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# one_cube.sh MASK VALUE  (untried/b3-heur; research only)
# Same call as counter_next/stack/run_cube.sh (team binary pair_calc_sub, run read-only), but the beta list and the
# output live in THIS folder and nothing is appended to the stack folder's log.
set -uo pipefail
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/b3-heur"
B="$HOME/hashsmash/pkg7_count/bin/pair_calc_sub"
ARGS="fdb77cfd 0a08818b fffffff8 8127c181 830303cf"; Y11=7af77f38
S8="00010000:0,00020000:0,00000001:0,00000002:1,00000404:1,00000808:1,01001008:0,02002040:0"
CM=$1; CV=$2
t0=$(date +%s.%N)
OMP_NUM_THREADS=1 nice -n 5 "$B" $ARGS "$D/beta_star.lst" $Y11 -rule $S8 -cube $CM $CV -mode both > "$D/base_${CM}_${CV}.out" 2> "$D/base_${CM}_${CV}.err"
rc=$?
t1=$(date +%s.%N)
echo "$CM $CV exit $rc seconds $(echo "$t1 - $t0" | bc) OUTR $(grep -c '^OUTR' "$D/base_${CM}_${CV}.out")"
