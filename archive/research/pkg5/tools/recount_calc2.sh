#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Recount for the fifth package with the main session's calculator as it is, the binary ~/hashsmash/bin/night_pair_calc2
# (built by the main session from research/night/main/pair_calc.c; it is only executed here, never rebuilt or written).
# The pin and the class come from tools/pkg5_data.py.
#
#   recount_calc2.sh mass   the betas with a nonzero part: the calculator's own lines and, with -o, every outcome
#                           with a nonzero E3 count (two-decimal logarithms). Kept in evidence/calc2_recount_<eta>.txt.
#   recount_calc2.sh all    every beta of the list of the package (the per-beta file of the count, evidence/pinB_<eta>.total):
#                           one line "beta k positive part" per beta, as in that file. Kept in evidence/calc2_total_<eta>.txt.
#                           Betas already in the file are skipped, so the run can be continued.
# CPU only: PAR betas at a time (default 3) with 2 threads each. Research helper, not submitted.
#
#   wsl -d Ubuntu -- bash './research/pkg5/tools/recount_calc2.sh' mass
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
CALC="$HOME/hashsmash/bin/night_pair_calc2"
TMP="$HOME/hashsmash/pkg5-recount"
mkdir -p "$TMP"
[ -x "$CALC" ] || { echo "no calculator at $CALC"; exit 3; }
eval "$(PYTHONDONTWRITEBYTECODE=1 python3 -B "$PKG/tools/pkg5_data.py" --recount-env)"
export CALC TMP D3 D11 DELTA Y3 Y11 ETA
SHA=$(sha256sum "$CALC" | cut -c1-64)
case "${1:-mass}" in
  mass)
    FILE="$PKG/evidence/calc2_recount_$ETA.txt"
    t0=$(date +%s)
    printf '%s\n' $BETAS | xargs -P "${PAR:-3}" -I{} bash -c 'OMP_NUM_THREADS=2 timeout 3600 "$CALC" $D3 $D11 $DELTA $Y3 $ETA {} 31 -y11 $Y11 -o "$TMP/out_{}.txt" > "$TMP/pair_{}.txt" 2>&1; echo "DONE {} exit $?" >> "$TMP/pair_{}.txt"'
    { echo "BINARY night_pair_calc2 sha256 $SHA, executed as it is (tools/recount_calc2.sh mass)"
      for b in $BETAS; do
        cat "$TMP/pair_$b.txt"
        [ -f "$TMP/out_$b.txt" ] && sed "s/^OUT/OUT $b/" "$TMP/out_$b.txt"
      done; } > "$TMP/calc2_recount.txt"
    cp "$TMP/calc2_recount.txt" "$FILE"
    for b in $BETAS; do rm -f "$TMP/pair_$b.txt" "$TMP/out_$b.txt"; done
    echo "betas $(echo $BETAS | wc -w), EXACT-E1 lines $(grep -c '^EXACT-E1' "$FILE"), outcome lines $(grep -c '^OUT ' "$FILE"), seconds $(( $(date +%s) - t0 ))"
    grep -E 'sampled [1-9]|fallbacks [1-9]|exit [1-9]' "$FILE" | cut -c1-160 | sed 's/^/NOT EXACT: /' | head -5
    awk '/^EXACT-E1/ {for (i = 1; i <= NF; i++) if ($i == "part") s += $(i + 1)} END {printf "sum of the parts %.1f\n", s}' "$FILE"
    ;;
  all)
    LIST="$PKG/evidence/pinB_$ETA.total"
    FILE="$PKG/evidence/calc2_total_$ETA.txt"
    WORK="$TMP/calc2_total_$ETA.txt"
    [ -f "$FILE" ] && [ ! -f "$WORK" ] && cp "$FILE" "$WORK"
    touch "$WORK"
    export WORK
    t0=$(date +%s)
    cut -d' ' -f1 "$LIST" | grep -v -x -F -f <(cut -d' ' -f1 "$WORK") | \
      xargs -P "${PAR:-3}" -I{} bash -c 'r=$(OMP_NUM_THREADS=2 timeout 3600 "$CALC" $D3 $D11 $DELTA $Y3 $ETA {} 31 -y11 $Y11 2>&1); echo "{} $(echo "$r" | grep -oE "wt_beta [0-9]+" | head -1 | cut -d" " -f2) $(echo "$r" | grep -oE "positive [0-9]+" | head -1 | cut -d" " -f2) $(echo "$r" | grep "^EXACT" | grep -oE "class-rate part [0-9.]+" | cut -d" " -f3) $(echo "$r" | grep -oE "sampled [1-9][0-9]*|fallbacks [1-9][0-9]*" | tr " \n" "=,")" >> "$WORK"'
    sort "$WORK" > "$FILE"
    echo "binary sha256 $SHA; betas in the list $(wc -l < "$LIST"), in the result $(wc -l < "$FILE"), seconds $(( $(date +%s) - t0 ))"
    awk 'NF >= 4 {s += $4; n++; if ($4 > 0) p++} NF == 2 {z++} END {printf "evaluated %d, no eps %d, with a part %d, sum %.1f\n", n, z, p, s}' "$FILE"
    ;;
  flagged)
    # the betas of the whole-list recount whose line carries a remark (an outcome through the random-subset branch of
    # the E3 count, or an E1 count by the product formula): the calculator's own lines and every outcome with a
    # nonzero E3 value, as in "mass". Kept in evidence/calc2_flagged_<eta>.txt.
    FILE="$PKG/evidence/calc2_flagged_$ETA.txt"
    FL=$(awk 'NF > 4 {print $1}' "$PKG/evidence/calc2_total_$ETA.txt")
    { echo "BINARY night_pair_calc2 sha256 $SHA, executed as it is (tools/recount_calc2.sh flagged)"
      for b in $FL; do
        rm -f "$TMP/outf_$b.txt"
        OMP_NUM_THREADS=2 timeout 3600 "$CALC" $D3 $D11 $DELTA $Y3 $ETA $b 31 -y11 $Y11 -o "$TMP/outf_$b.txt" 2>&1
        echo "DONE $b exit $?"
        [ -f "$TMP/outf_$b.txt" ] && sed "s/^OUT/OUT $b/" "$TMP/outf_$b.txt"
        rm -f "$TMP/outf_$b.txt"
      done; } > "$FILE"
    echo "flagged betas: $(echo $FL | wc -w); outcome lines $(grep -c '^OUT ' "$FILE"), of them with an exact E1 count of zero $(grep -c '^OUT .* log2P1 -999\.00 ' "$FILE")"
    grep -E '^(PAIR|EXACT)' "$FILE" | cut -c1-230
    ;;
  *) echo "usage: recount_calc2.sh mass|all|flagged"; exit 2 ;;
esac
