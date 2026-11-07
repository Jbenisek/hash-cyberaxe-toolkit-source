#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer (count and cost): build and run the own counter. usage: build | bf CASES | run | status
set -u
H="${HASHCYBERAXE_WORKSPACE}/research/pkg7/review"
S="$HOME/hashsmash/p7_countcost"
mkdir -p "$S"
case "${1:-status}" in
build)
  gcc -O2 -o "$S/cnt" "$H/count-cost_p7_cnt.c" 2>&1 | head -8; ls -la "$S/cnt" | cut -c1-80 ;;
bf)
  for s in 1 2 3 4; do nice -n 5 "$S/cnt" bf $((7100 + s)) "${2:-4}" > "$S/bf_$s.txt" 2>&1 & done
  wait
  cat "$S"/bf_[1-4].txt > "$H/count-cost_p7_bf8.txt"
  grep -c "equal$" "$H/count-cost_p7_bf8.txt"; grep -c DIFFERENT "$H/count-cost_p7_bf8.txt"; grep "^bf seed" "$H/count-cost_p7_bf8.txt" ;;
run)
  awk -F'\t' 'NR>1 {print $1, $2, $3}' "$H/../count/a15_outcomes.tsv" > "$S/list.txt"
  wc -l < "$S/list.txt"
  split -n l/4 -d "$S/list.txt" "$S/part_"
  for p in 00 01 02 03; do nice -n 5 "$S/cnt" run < "$S/part_$p" > "$S/out_$p.txt" 2>&1 & done
  wait
  cat "$S"/out_0[0-3].txt > "$H/count-cost_p7_own32.tsv"
  wc -l < "$H/count-cost_p7_own32.tsv" ;;
one)
  echo "$2 $3 $4" | "$S/cnt" run ;;
status)
  ls -la "$S" | tail -12; uptime ;;
esac
# added: the whole class (mask 03cf8303) on the outcomes of count/full_outcomes.tsv
if [ "${1:-}" = "runfull" ]; then
  awk -F'\t' 'NR>1 {print $1, $2, $3}' "$H/../count/full_outcomes.tsv" > "$S/listf.txt"
  split -n l/4 -d "$S/listf.txt" "$S/partf_"
  for p in 00 01 02 03; do nice -n 5 "$S/cnt" run 03cf8303 030c0303 < "$S/partf_$p" > "$S/outf_$p.txt" 2>&1 & done
  wait
  cat "$S"/outf_0[0-3].txt > "$H/count-cost_p7_own32_full.tsv"
  wc -l < "$H/count-cost_p7_own32_full.tsv"
fi
