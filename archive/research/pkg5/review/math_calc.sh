#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost, part (a): the count once more with the calculator binary as it is
# (~/hashsmash/bin/night_pair_calc2, only executed). Constants typed from proof.md 3.2 / 6.1 / Section 10:
#   DY3 = 815924bf, DY11 = 4285247f, delta = fffffffe, Y3 = 3f52eda0, Y11 = 5ebf5bc0, eta = e7c1815f.
#   math_calc.sh mass     every beta with a nonzero part in evidence/pinB_e7c1815f.total, with its outcomes (-o)
#   math_calc.sh sample   the three betas the report flags, and every 17th other beta of the list (parts must be 0)
# At most 2 processes with one thread each.
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
R="$PKG/review"
CALC="$HOME/hashsmash/bin/night_pair_calc2"
TMP="$HOME/hashsmash/pkg5-review-math"
mkdir -p "$TMP"
export CALC TMP
ARGS='815924bf 4285247f fffffffe 3f52eda0 e7c1815f'
export ARGS
t0=$(date +%s)
case "${1:-mass}" in
  mass)
    BETAS=$(awk 'NF == 4 && $4 > 0 {print $1}' "$PKG/evidence/pinB_e7c1815f.total")
    printf '%s\n' $BETAS | xargs -P 2 -I{} bash -c 'OMP_NUM_THREADS=1 timeout 3600 "$CALC" $ARGS {} 31 -y11 5ebf5bc0 -o "$TMP/o_{}.txt" > "$TMP/p_{}.txt" 2>&1; echo "DONE {} exit $?" >> "$TMP/p_{}.txt"'
    { echo "BINARY sha256 $(sha256sum "$CALC" | cut -c1-64)"
      for b in $BETAS; do cat "$TMP/p_$b.txt"; sed "s/^OUT/OUT $b/" "$TMP/o_$b.txt"; done; } > "$R/math_calc2_mass.txt"
    for b in $BETAS; do rm -f "$TMP/p_$b.txt" "$TMP/o_$b.txt"; done
    echo "betas $(echo $BETAS | wc -w), EXACT-E1 lines $(grep -c '^EXACT-E1' "$R/math_calc2_mass.txt"), OUT lines $(grep -c '^OUT ' "$R/math_calc2_mass.txt"), of them with E1 nonzero $(grep '^OUT ' "$R/math_calc2_mass.txt" | grep -vc 'log2P1 -999')"
    grep -cE 'sampled [1-9]|fallbacks [1-9]|exit [1-9]' "$R/math_calc2_mass.txt" | sed 's/^/lines with a fallback or a failure: /'
    awk '/^EXACT-E1/ {for (i = 1; i <= NF; i++) if ($i == "part") s += $(i + 1)} END {printf "sum of the parts %.1f\n", s}' "$R/math_calc2_mass.txt"
    ;;
  sample)
    LIST=$( { echo c81cd8b3; echo f81c2873; echo f81c28b3; awk 'NF == 4 && $4 == 0 && NR % 17 == 3 {print $1}' "$PKG/evidence/pinB_e7c1815f.total"; awk 'NF == 2 && NR % 97 == 5 {print $1}' "$PKG/evidence/pinB_e7c1815f.total"; } | sort -u)
    printf '%s\n' $LIST | xargs -P 2 -I{} bash -c 'r=$(OMP_NUM_THREADS=1 timeout 3600 "$CALC" $ARGS {} 31 -y11 5ebf5bc0 2>&1); echo "{} positive=$(echo "$r" | grep -oE "positive [0-9]+" | head -1 | cut -d" " -f2) part=$(echo "$r" | grep "^EXACT" | grep -oE "class-rate part [0-9.]+" | cut -d" " -f3) $(echo "$r" | grep -oE "sampled [1-9][0-9]*|fallbacks [1-9][0-9]*" | tr " \n" "=,") lines=$(echo "$r" | wc -l)" >> "$TMP/sample.txt"'
    sort "$TMP/sample.txt" > "$R/math_calc2_sample.txt"; rm -f "$TMP/sample.txt"
    echo "betas in the sample $(wc -l < "$R/math_calc2_sample.txt"); with part= empty (no eps) $(grep -c 'part= ' "$R/math_calc2_sample.txt"); with part=0.0 $(grep -c 'part=0.0 ' "$R/math_calc2_sample.txt"); with a remark $(grep -cE 'sampled|fallbacks' "$R/math_calc2_sample.txt")"
    grep -vE 'part=0.0 |part= ' "$R/math_calc2_sample.txt" | head -3
    ;;
esac
echo "seconds $(( $(date +%s) - t0 ))"
