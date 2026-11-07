#!/bin/bash
# lbsearch.sh GEN NAME STEP_TIME "W1 W2 ..." [generator args]
# Tries each bound in order (highest first) with kissat --unsat and --time STEP_TIME; stops at the
# first UNSAT (proved: minimum >= W+1) or a SAT (a model at or below W was found).
set -u
cd "$(dirname "$0")"
gen=$1; name=$2; step=$3; ws=$4; shift 4
for W in $ws; do
  bash runone.sh "$gen" "${name}_LB${W}" "$W" "$step" unsat "$@"
  rc=$(tail -1 runs/LOG.txt | sed -n 's/.* rc=\([0-9]*\) .*/\1/p')
  if [ "$rc" = "20" ]; then echo "$name RESULT proved_min_ge=$(( W + 1 ))" | tee -a runs/LOG.txt; exit 0; fi
  if [ "$rc" = "10" ]; then echo "$name RESULT model_found_at_or_below=$W" | tee -a runs/LOG.txt; exit 0; fi
done
echo "$name RESULT no bound proved in [$ws]" | tee -a runs/LOG.txt
