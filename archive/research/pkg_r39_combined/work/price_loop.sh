#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# price_loop.sh : owner 10-28 'optimize' - every 10 min: stage new pin39b pairs (advice check), run their 14 tail runs (LANES=2), rank all by mean_lin
W="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work; cd $W
while true; do
  python3 tail_var_gen_mid1028.py > /dev/null 2>&1
  LANES=2 bash tail_var_run_mid1028.sh > /dev/null 2>&1
  for d in tail_var/p_pin39b_*; do [ -f $d/out_14.json ] && echo "$(python3 tail_stats_dir.py $d 2>/dev/null | grep -o 'mean_lin [-0-9.]*' | awk '{print $2}')	$(basename $d)"; done | sort -t$'\t' -k1,1 -g -r > TAIL_RANK.tsv
  echo "$(date '+%H:%M') ranked $(wc -l < TAIL_RANK.tsv); best: $(head -1 TAIL_RANK.tsv)" >> price_loop.log
  sleep 600
done
