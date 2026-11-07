#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# count-cost reviewer: the calculator ~/hashsmash/bin/night_pair_calc2, executed as it is (never rebuilt or written),
# on the heaviest betas of class 830303cf (pin H8). Two processes. Output: review/count-cost_calc2.out
set -uo pipefail
CALC="$HOME/hashsmash/bin/night_pair_calc2"
R="${HASHCYBERAXE_WORKSPACE}/research/pkg6/review"
TMP="$R/count-cost_calc2_tmp"; mkdir -p "$TMP"
[ -x "$CALC" ] || { echo "no calculator at $CALC"; exit 3; }
export CALC TMP D3=fdb77cfd D11=0a08818b DELTA=fffffff8 Y3=8127c181 Y11=7af77f38 ETA=830303cf
BETAS="18b0e098 18d0e098 18b1a098 18d1a098 18b3e098 18d3e098 18d1a398 19f1a098"
t0=$(date +%s)
printf '%s\n' $BETAS | xargs -P 2 -I{} bash -c 'OMP_NUM_THREADS=1 timeout 2400 "$CALC" $D3 $D11 $DELTA $Y3 $ETA {} 31 -y11 $Y11 -o "$TMP/out_{}.txt" > "$TMP/pair_{}.txt" 2>&1; echo "DONE {} exit $?" >> "$TMP/pair_{}.txt"'
{ echo "BINARY night_pair_calc2 sha256 $(sha256sum "$CALC" | cut -c1-64), executed as it is; seconds $(( $(date +%s) - t0 ))"
  for b in $BETAS; do cat "$TMP/pair_$b.txt"; [ -f "$TMP/out_$b.txt" ] && sed "s/^OUT/OUT $b/" "$TMP/out_$b.txt"; done; } > "$R/count-cost_calc2.out"
echo "betas $(echo $BETAS | wc -w), EXACT-E1 lines $(grep -c '^EXACT-E1' "$R/count-cost_calc2.out"), outcome lines $(grep -c '^OUT ' "$R/count-cost_calc2.out"), nonzero exits $(grep -c -E 'exit [1-9]' "$R/count-cost_calc2.out"), seconds $(( $(date +%s) - t0 ))"
grep '^EXACT-E1' "$R/count-cost_calc2.out" | awk '{for (i = 1; i <= NF; i++) if ($i == "part") printf "%s %s; ", $3, $(i + 1)} END {print ""}' | cut -c1-400
