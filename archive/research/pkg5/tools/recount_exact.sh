#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Recount of the exact class-rate parts quoted in pkg5, pair by pair, with the night's calculator (source
# research/night/main/pair_calc.c). The pin, the class and the list of betas come from tools/pkg5_data.py (the
# betas with a nonzero part in the night's .total file, and the betas counted outside that list).
#
# The calculator is built here afresh from its source with ONE change, in what it writes with -o: for every
# outcome it also writes the two factors in full instead of two-decimal logarithms,
#     E1 = the number of triples (c1, b1, a2) with this beta for which E1 produces (tau, eps)  [P1 * 2^(96 - k)]
#     N3 = the number of quadruples (Y4, h1, Y9, w8) for which E3 produces the outcome.
# Nothing that is computed is changed. Kept in evidence/pairs_recount_<eta>.txt, which the .total file does not have:
#   - the calculator's complete output lines, with the number of outcomes that went through the E3 counter's
#     random-subset branch ("sampled") and the number of outcomes for which the exact E1 count fell back to
#     the product formula ("formula fallbacks"); both must be 0 for the word "exact";
#   - a line OUTS per beta: of the outcomes with a nonzero E3 count ("positive" in the PAIR line), how many
#     have a nonzero exact E1 count as well ("nonzero") and how many have an exact E1 count of zero ("zero");
#   - a line OUTX per outcome with a nonzero product: tau, eps, E1 and N3 as integers.
# CPU only, four threads. Research helper, not submitted.
#
#   wsl -d Ubuntu -- bash './research/pkg5/tools/recount_exact.sh'
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
SRC="${HASHCYBERAXE_WORKSPACE}/research/night/main"
OUT="$PKG/evidence"
TMP="$HOME/hashsmash/pkg5-recount"
mkdir -p "$OUT" "$TMP"
# the patched copy: a global array for the exact E1 probability and one changed output line
{
  echo 'static double g_px[1 << 20];'
  sed -e 's|outs\[i\].lp1 = p > 0.0 ? log2(p) : -999.0;|{ outs[i].lp1 = p > 0.0 ? log2(p) : -999.0; if (i < (1 << 20)) g_px[i] = p; }|' \
      -e 's|if (outs\[i\].n3 > 0.0) fprintf(f, "OUT %08x %08x log2P1 %.2f log2N3 %.2f\\n", outs\[i\].tau, outs\[i\].eps, outs\[i\].lp1, log2(outs\[i\].n3));|if (outs[i].n3 > 0.0) fprintf(f, "OUT %08x %08x log2P1 %.2f log2N3 %.2f E1 %.0f N3 %.0f\\n", outs[i].tau, outs[i].eps, outs[i].lp1, log2(outs[i].n3), i < (size_t)(1 << 20) \&\& outs[i].lp1 > -900.0 ? g_px[i] * exp2(96.0 - __builtin_popcount(rol(g_beta, ROT2) \& LOWBITS)) : 0.0, outs[i].n3);|' \
      "$SRC/pair_calc.c"
} > "$TMP/pair_calc_exact.c"
if [ "$(grep -c 'g_px\[i\]' "$TMP/pair_calc_exact.c")" != 2 ]; then echo "the two lines to change were not found in pair_calc.c"; exit 3; fi
gcc -O2 -fopenmp -I "$SRC" -o "$TMP/pair_calc_exact" "$TMP/pair_calc_exact.c" -lm 2> "$TMP/build.log" || { echo "build failed"; head -5 "$TMP/build.log"; exit 3; }
eval "$(PYTHONDONTWRITEBYTECODE=1 python3 -B "$PKG/tools/pkg5_data.py" --recount-env)"
FILE="$OUT/pairs_recount_$ETA.txt"
NEW="$TMP/recount_new.txt"
{ echo "SOURCE pair_calc.c sha256 $(sha256sum "$SRC/pair_calc.c" | cut -c1-64), rebuilt with one changed output line (tools/recount_exact.sh)"; } > "$NEW"
for beta in $BETAS; do
  start=$(date +%s)
  rm -f "$TMP/outs.txt"
  OMP_NUM_THREADS=4 timeout 3600 "$TMP/pair_calc_exact" "$D3" "$D11" "$DELTA" "$Y3" "$ETA" "$beta" 31 -y11 "$Y11" -o "$TMP/outs.txt" > "$TMP/one.txt" 2>&1
  status=$?
  all=$(grep -c '^OUT' "$TMP/outs.txt" 2>/dev/null || true)
  zero=$(grep -c '^OUT .* log2P1 -999\.00 ' "$TMP/outs.txt" 2>/dev/null || true)
  { cat "$TMP/one.txt"
    echo "OUTS $ETA $beta written ${all:-0} nonzero $(( ${all:-0} - ${zero:-0} )) zero ${zero:-0}"
    grep -v ' log2P1 -999\.00 ' "$TMP/outs.txt" 2>/dev/null | awk -v e="$ETA" -v b="$beta" '$1 == "OUT" {print "OUTX", e, b, $2, $3, "E1", $9, "N3", $11}'
    echo "DONE $beta exit $status seconds $(( $(date +%s) - start ))"; } >> "$NEW"
done
cp "$NEW" "$FILE"
rm -f "$TMP/one.txt" "$TMP/outs.txt" "$NEW"
grep -c '^EXACT-E1' "$FILE" | sed 's/^/pairs counted: /'
grep -E 'sampled [1-9]|fallbacks [1-9]' "$FILE" | cut -c1-200 | sed 's/^/NOT EXACT: /'
awk '/^OUTS/ {w += $5; n += $7; z += $9} END {printf "outcomes with a nonzero E3 count: %d; of them exact E1 count nonzero %d, zero %d\n", w, n, z}' "$FILE"
