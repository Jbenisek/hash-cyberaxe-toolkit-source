#!/bin/bash
# run.sh NAME W TIME_SECONDS [extra b3trail.py args]
# Builds the CNF, runs ONE kissat with --time (no wrapper), decodes, deletes the CNF.
set -u
cd "$(dirname "$0")"
name=$1; W=$2; tl=$3; shift 3
mkdir -p runs
start=$(date +%s)
python3 -B b3trail.py --W "$W" --out "runs/$name" "$@" > "runs/$name.gen.txt" 2>&1
cat "runs/$name.gen.txt"
kissat --time="$tl" -q "runs/$name.cnf" > "runs/$name.sol" 2>&1
rc=$?
echo "kissat exit $rc (10=SAT 20=UNSAT 0=UNKNOWN) after $(( $(date +%s) - start )) s"
python3 -B decode.py "runs/$name" "runs/$name.sol" --json "runs/$name.dec.json" > "runs/$name.dec.txt" 2>&1
grep -E 'solver:|TOTAL|collision|invalid' "runs/$name.dec.txt"
grep -v '^v ' "runs/$name.sol" > "runs/$name.sol.txt"; rm -f "runs/$name.sol"
rm -f "runs/$name.cnf"
echo "$name W=$W tl=$tl args=$* rc=$rc secs=$(( $(date +%s) - start ))" >> runs/LOG.txt
