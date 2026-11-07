#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: the package's own self-test, once as quoted in proof.md 6.5 (2000, seed 1)
# and once on a seed the package never used. Output to review/math_selftest_*.json; a few fields are printed.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg5/blake3-r2/experiments/halfsearch.py"
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
python3 -B -s "$P" --selftest 2000 1 > "$R/math_selftest_2000_1.json"; echo "exit $?"
python3 -B -s "$P" --selftest 20000 mathlens > "$R/math_selftest_20000_mathlens.json"; echo "exit $?"
python3 -B - "$R/math_selftest_2000_1.json" "$R/math_selftest_20000_mathlens.json" <<'EOF'
import json, sys
for p in sys.argv[1:]:
    d = json.load(open(p))
    print(d["cases"], d["lanes_right"], d["lanes_checked"], d["stage_a"], d["stage_2"], "ruleA", d["lanes_passing_rule_a"],
          "entered", d["batches_entering_stage_2"], "reg", d["registers"], "largest", round(d["largest_lane"] / 2**32, 3),
          "sums", [d["parts"][k].get("largest_sum") for k in d["parts"] if "largest_sum" in d["parts"][k]],
          d["zero_lane_patterns_right"], d["rule_a_patterns_right"], d["rule_a_patterns_satisfied"])
EOF
