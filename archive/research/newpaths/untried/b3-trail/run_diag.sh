#!/bin/bash
# run_diag.sh NAME W TIME KCONF U DM : last-step-only model (diag_match.py), ONE kissat with --time.
set -u
cd "$(dirname "$0")"
name=$1; W=$2; tl=$3; kconf=$4; U=$5; DM=$6
mkdir -p runs
start=$(date +%s)
python3 -B diag_match.py --W "$W" --out "runs/$name" --u "$U" --dm "$DM" > "runs/$name.gen.txt" 2>&1
cat "runs/$name.gen.txt"
kopt=""
[ "$kconf" = "sat" ] && kopt="--sat"
[ "$kconf" = "unsat" ] && kopt="--unsat"
kissat --time="$tl" -q $kopt "runs/$name.cnf" > "runs/$name.sol" 2>&1
rc=$?
echo "kissat($kconf) exit $rc (10=SAT 20=UNSAT 0=UNKNOWN) after $(( $(date +%s) - start )) s"
python3 -B decode.py "runs/$name" "runs/$name.sol" --json "runs/$name.dec.json" > "runs/$name.dec.txt" 2>&1
grep -E 'solver:|TOTAL|collision|invalid' "runs/$name.dec.txt"
grep -v '^v ' "runs/$name.sol" > "runs/$name.sol.txt"; rm -f "runs/$name.sol"
rm -f "runs/$name.cnf"
echo "$name W=$W tl=$tl kconf=$kconf diag U=$U DM=$DM rc=$rc secs=$(( $(date +%s) - start ))" >> runs/LOG.txt
