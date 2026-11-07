#!/bin/bash
# runone.sh GEN NAME W TIME_SECONDS KCONF [generator args]
# One bounded solve: build with GEN (b3trail.py / diag_match.py / pair_free.py), ONE kissat with
# --time (KCONF default|sat|unsat), decode, delete the CNF, log the outcome.
set -u
cd "$(dirname "$0")"
gen=$1; name=$2; W=$3; tl=$4; kconf=$5; shift 5
mkdir -p runs
start=$(date +%s)
python3 -B "$gen" --W "$W" --out "runs/$name" "$@" > "runs/$name.gen.txt" 2>&1
kopt=""
[ "$kconf" = "sat" ] && kopt="--sat"
[ "$kconf" = "unsat" ] && kopt="--unsat"
kissat --time="$tl" -q $kopt "runs/$name.cnf" > "runs/$name.sol" 2>&1
rc=$?
python3 -B decode.py "runs/$name" "runs/$name.sol" --json "runs/$name.dec.json" > "runs/$name.dec.txt" 2>&1
grep -v '^v ' "runs/$name.sol" > "runs/$name.sol.txt"; rm -f "runs/$name.sol" "runs/$name.cnf"
cw=$(grep -E '^COUNTED WEIGHT' "runs/$name.dec.txt" | awk -F': ' '{print $2}')
echo "$name W=$W kconf=$kconf rc=$rc counted=${cw:-none} secs=$(( $(date +%s) - start )) gen=$gen $*" | tee -a runs/LOG.txt
