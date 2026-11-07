#!/usr/bin/env bash
# Step 5: the ORIGINAL calculator (research/night/main/pair_calc.c with n3x.inc and research/r2_e3count.c, built
# here from the untouched originals) with its own option -sub, on the heaviest betas of the cube.
#   c05_orig.sh NAME EXTRA_MASK EXTRA_VALUE BETA [BETA...]     (extra bits only: cube mask without the class mask)
# Prints the class-rate part per beta as the original prints it (double precision).
set -uo pipefail
W='historical-sources/~~Projects/~HashSmash/workspace'
H="$W/research/pkg7/count"; S="$HOME/hashsmash/pkg7_count"; B="$S/bin"; O="$S/out"
NAME=$1; XM=$2; XV=$3; shift 3
if [ ! -x "$B/pair_calc_orig" ]; then
  ( cd "$W/research/night/main" && gcc -O2 -fopenmp -o "$B/pair_calc_orig" pair_calc.c -lm 2> "$O/build_orig.log" ) || { echo "build of the original failed"; head -3 "$O/build_orig.log"; exit 3; }
fi
echo "original pair_calc.c sha256 $(sha256sum "$W/research/night/main/pair_calc.c" | cut -c1-16), binary $(sha256sum "$B/pair_calc_orig" | cut -c1-16)" > "$H/orig_$NAME.txt"
t0=$(date +%s)
printf '%s\n' "$@" | xargs -P 4 -I{} sh -c "OMP_NUM_THREADS=1 nice -n 5 timeout 900 '$B/pair_calc_orig' fdb77cfd 0a08818b fffffff8 8127c181 830303cf {} 31 -y11 7af77f38 -sub $XM $XV > '$O/orig_${NAME}_{}.txt' 2>&1; echo \"exit \$? beta {}\" >> '$O/orig_${NAME}_{}.txt'"
for b in "$@"; do grep -E '^(PAIR|EXACT-E1|exit)' "$O/orig_${NAME}_$b.txt" | cut -c1-260 >> "$H/orig_$NAME.txt"; done
echo "seconds $(( $(date +%s) - t0 ))"; grep -E '^EXACT-E1' "$H/orig_$NAME.txt" | cut -c1-200 | head -8
