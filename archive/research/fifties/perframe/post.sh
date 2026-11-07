#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# after the main run: prereg check + statistics, every main E1L and E3P hit recomputed, pair listing
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perframe"
sha256sum -c PREREG.sha256 > post_prereg_check.txt 2>&1
read K1 K2 < <(python3 -B seeds.py main)
python3 -B analyse_pf.py main main_out.json --prereg > main_analyse.log 2>&1
python3 -B ref_pf.py hits $K1 $K2 main/*.hits > main_hits_check.json 2>&1
python3 -B pairs_pf.py main main_pairs.json > main_pairs.log 2>&1
cat post_prereg_check.txt main_analyse.log main_pairs.log
python3 -B -c "import json; h=json.load(open('main_hits_check.json')); print({k: h[k] for k in ('hits','ok','by_event_bit','cv_zero_words_hist_E1L','cv_zero_words_hist_E3P')})"
