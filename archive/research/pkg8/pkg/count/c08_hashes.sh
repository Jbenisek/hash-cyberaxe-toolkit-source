#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Step 8: sha256 (first 16 hex) of sources, binaries and result files -> hashes.txt
H="${HASHCYBERAXE_WORKSPACE}/research/pkg7/count"; S="$HOME/hashsmash/pkg7_count"
cd "$H" || exit 3
{ echo "made $(date '+%Y-%m-%d %H:%M')"
  for f in pair_calc_sub.c pair_calc_rule.c pair_calc_batch.c n3r.inc n3x.inc r2_e3count.c sub_bf.c mk_sub.py rule_tab.py sub_tab.py cost.py mk_tables.py cmp_digits.py cmp_orig.py \
           a15.out a17.out full.out bf8_sub.txt a15_totals.txt a17_totals.txt full_totals.txt a15_cmp.txt a17_cmp.txt full_cmp.txt a15_parts.tsv a17_parts.tsv full_parts.tsv \
           a15_outcomes.tsv a17_outcomes.tsv full_outcomes.tsv COST_COUNT.txt COUNT_tables.md cmp_digits.txt origall_a15.txt origall_a17.txt origall_a15_cmp.txt origall_a17_cmp.txt h8_betas_pos.txt; do
    [ -f "$f" ] && echo "$(sha256sum "$f" | cut -c1-16) $(wc -c < "$f") $f" || echo "MISSING $f"; done
  for b in pair_calc_sub sub_bf8 pair_calc_orig; do echo "$(sha256sum "$S/bin/$b" | cut -c1-16) binary $b"; done
  echo "h8_betas_pos.txt against research/h8/rule_exact/h8_betas_pos.txt: $(diff h8_betas_pos.txt ../../h8/rule_exact/h8_betas_pos.txt | grep -c '^[<>]') lines differ"
} > hashes.txt
echo "hashes.txt: $(wc -l < hashes.txt) lines, missing $(grep -c MISSING hashes.txt)"
