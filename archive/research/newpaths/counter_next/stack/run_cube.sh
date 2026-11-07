#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_cube.sh NAME MASK VALUE   (counter_next/stack; research only)
# Exact E3 count of beta* = 18b0e098 alone over one cube of e1 = Y3 + Y4 (pin H8, class 830303cf), with the team's
# counting binary pair_calc_sub (built 2026-10-06 from research/pkg10/pkg/count/pair_calc_sub.c; run read-only).
# Rules: S8 (= filed rule A) so that the rule-A kept part is printed too.  Output: cube_NAME.out in this folder.
set -uo pipefail
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/counter_next/stack"
B="$HOME/hashsmash/pkg7_count/bin/pair_calc_sub"
ARGS="fdb77cfd 0a08818b fffffff8 8127c181 830303cf"; Y11=7af77f38
S8="00010000:0,00020000:0,00000001:0,00000002:1,00000404:1,00000808:1,01001008:0,02002040:0"
echo "18b0e098 11" > "$D/beta_star.lst"
NAME=$1; CM=$2; CV=$3
t0=$(date +%s)
OMP_NUM_THREADS=1 nice -n 5 "$B" $ARGS "$D/beta_star.lst" $Y11 -rule $S8 -cube $CM $CV -mode both > "$D/cube_$NAME.out" 2> "$D/cube_$NAME.err"
echo "$NAME $CM $CV exit $? seconds $(( $(date +%s) - t0 )) OUTR $(grep -c '^OUTR' "$D/cube_$NAME.out")" >> "$D/cube_runs.log"
