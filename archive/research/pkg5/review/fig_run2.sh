#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: the program's self-test as quoted in the text (2,000 batches, seed 1), and a second seed of my own
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg5
R="$P/review"
cd "$P/blake3-r2" || exit 1
nice -n 10 python3 -B -s experiments/halfsearch.py --selftest 2000 1 > "$R/fig_selftest_2000_1.json" 2> "$R/fig_selftest_2000_1.err"
echo "exit $? (seed 1)"
nice -n 10 python3 -B -s experiments/halfsearch.py --selftest 3000 fig77 > "$R/fig_selftest_3000_fig77.json" 2> "$R/fig_selftest_3000_fig77.err"
echo "exit $? (seed fig77)"
python3 - "$R" <<'EOF'
import json, sys
R = sys.argv[1]
for name in ("fig_selftest_2000_1.json", "fig_selftest_3000_fig77.json"):
    j = json.load(open(R + "/" + name))
    order = ("C0 backwards", "K3", "C2 to z", "rule A", "C2, rest", "D1", "C1 to Y1", "E1, A and B", "E1 test")
    print(name, j["lanes_right"], "/", j["lanes_checked"], "passA", j["lanes_passing_rule_a"], "entered", j["batches_entering_stage_2"],
          "A", j["stage_a"], "2", j["stage_2"], "reg", j["registers"], "zero", j["zero_test_words"])
    print("  sums", [j["parts"][p]["largest_sum"] for p in order], "largest", round(j["largest_lane"] / 2**32, 5),
          "ctx/alpha", j["per_context_constants"], j["per_alpha_constants"], "members", j["members_in_list"], j["list_words"],
          "patterns", j["zero_lane_patterns_right"], j["rule_a_patterns_right"], j["rule_a_patterns_satisfied"], "same", j["same_counts_in_every_case"], j["counts_equal_table"])
EOF
