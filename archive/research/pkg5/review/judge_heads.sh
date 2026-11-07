#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# hostile-judge lens: first lines of the evidence files, into one file (read-only)
P="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
OUT="$P/review/judge_heads.out"
{
  for f in evidence/pairs_recount_e7c1815f.txt evidence/calc2_total_e7c1815f.txt evidence/calc2_recount_e7c1815f.txt \
           evidence/calc2_flagged_e7c1815f.txt evidence/followup/pinB3_rules.txt evidence/followup/followup_cost.txt \
           evidence/followup/batch4_two_class_filed_1200000_s51.json evidence/selftest_1200000_61.json \
           evidence/selftest_1200000_62.json evidence/validation_log.txt evidence/followup/toy2_10.txt \
           evidence/pinB_e7c1815f.total blake3-r2/experiments/manifest.json; do
    echo "=================== $f ($(wc -l < "$P/$f") lines)"
    head -c 6000 "$P/$f" | cut -c1-700 | head -40
    echo
    echo "------- tail"
    tail -n 6 "$P/$f" | cut -c1-700
  done
  echo "=================== pinB3_sat.txt head/tail"
  head -n 8 "$P/evidence/followup/pinB3_sat.txt" | cut -c1-500
  tail -n 12 "$P/evidence/followup/pinB3_sat.txt" | cut -c1-500
  echo "=================== toy2_8 tail"
  tail -n 15 "$P/evidence/followup/toy2_8.txt" | cut -c1-500
} > "$OUT" 2>&1
wc -l "$OUT" | cut -d' ' -f1
