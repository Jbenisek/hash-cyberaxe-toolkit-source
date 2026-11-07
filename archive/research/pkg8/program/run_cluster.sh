#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Run both self-tests of research/pkg8/program/halfsearch_cluster.py and save the JSON lines in the WSL scratch.
# Pure Python standard library; CPU only; no network, no GPU, no yukon, .key never read.
DIR="${HASHCYBERAXE_WORKSPACE}/research/pkg8/program"
OUT="$HOME/hashsmash/pkg8"
mkdir -p "$OUT"
cd "$DIR" || exit 2

nice -n 5 python3 halfsearch_cluster.py --selftest 2000 1 > "$OUT/base_selftest.json"
echo "baseline --selftest 2000 exit=$?"

nice -n 5 python3 halfsearch_cluster.py --cluster-selftest 50000 pkg8 > "$OUT/cluster_selftest.json"
echo "cluster --cluster-selftest 50000 exit=$?"

python3 - "$OUT/base_selftest.json" "$OUT/cluster_selftest.json" <<'PY'
import json, sys
b = json.load(open(sys.argv[1]))
print("baseline: lanes_right %d/%d  stageA %d+%d  stage2 %d+%d  registers %d"
      % (b["lanes_right"], b["lanes_checked"], b["stage_a"]["operations"], b["stage_a"]["loads"],
         b["stage_2"]["operations"], b["stage_2"]["loads"], b["registers"]))
c = json.load(open(sys.argv[2]))
print("cluster: trials %d  h1 %d  k8 %d  gate %d  packedSA %d/%d  packedS2 %d/%d  const %s"
      % (c["trials_checked"], c["h1_equals_tl_ref"], c["k8_equals_tl_ref"], c["gate_equals_H4_of_tl_ref"],
         c["packed_stage_a_flag_equals_scalar"], c["packed_lanes"],
         c["packed_stage_2_word_equals_reference"], c["packed_lanes"], c["new_counts_constant"]))
PY
