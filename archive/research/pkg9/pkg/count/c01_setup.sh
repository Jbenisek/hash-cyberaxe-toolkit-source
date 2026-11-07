#!/usr/bin/env bash
# Step 1: copies of the counter's sources (originals untouched), hashes, the generated pair_calc_sub.c, builds.
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
W='historical-sources/~~Projects/~HashSmash/workspace'
H="$W/research/pkg7/count"; X="$W/research/h8/rule_exact"
S="$HOME/hashsmash/pkg7_count"; B="$S/bin"; O="$S/out"
mkdir -p "$B" "$O"; cd "$H" || exit 3
for f in r2_e3count.c n3x.inc pair_calc_batch.c n3r.inc pair_calc_rule.c rule_tab.py; do cp "$X/$f" "$f"; done
{ echo "sha256 (first 16) of the sources; made $(date '+%Y-%m-%d %H:%M')"
  for f in research/r2_e3count.c research/night/main/n3x.inc research/night/main/pair_calc.c research/h8/counts/pair_calc_batch.c; do
    echo "original   $(sha256sum "$W/$f" | cut -c1-16) $f"; done
  for f in r2_e3count.c n3x.inc pair_calc_batch.c n3r.inc pair_calc_rule.c rule_tab.py; do
    echo "rule_exact $(sha256sum "$X/$f" | cut -c1-16) $f   copy here $(sha256sum "$f" | cut -c1-16)"; done
  echo "lines that differ: r2_e3count.c against research/r2_e3count.c $(diff "$W/research/r2_e3count.c" r2_e3count.c | grep -c '^[<>]'); n3x.inc against research/night/main/n3x.inc $(diff "$W/research/night/main/n3x.inc" n3x.inc | grep -c '^[<>]'); pair_calc_batch.c against research/h8/counts/pair_calc_batch.c $(diff "$W/research/h8/counts/pair_calc_batch.c" pair_calc_batch.c | grep -c '^[<>]') (the include path)"
} > sources.sha
python3 -B mk_sub.py >> sources.sha || { echo "mk_sub failed"; exit 3; }
echo "generated  $(sha256sum pair_calc_sub.c | cut -c1-16) pair_calc_sub.c; lines that differ from pair_calc_rule.c: $(diff pair_calc_rule.c pair_calc_sub.c | grep -c '^[<>]')" >> sources.sha
tail -3 sources.sha | cut -c1-330
gcc -O2 -fopenmp -Wall -o "$B/pair_calc_sub" pair_calc_sub.c -lm 2> "$O/build32.log"; r1=$?
gcc -O2 -fopenmp -Wall -DWBITS=8 -o "$B/sub_bf8" sub_bf.c -lm 2> "$O/build8.log"; r2=$?
echo "build: 32-bit exit $r1 (errors $(grep -c 'error' "$O/build32.log")); 8-bit exit $r2 (errors $(grep -c 'error' "$O/build8.log"))"
grep -h -E 'error' "$O/build32.log" "$O/build8.log" | head -4 | cut -c1-230
grep -h -E 'warning' "$O/build32.log" "$O/build8.log" | grep -v -E 'unused|defined but not used' | sort -u | head -3 | cut -c1-230
