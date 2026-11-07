#!/bin/bash
# minimize.sh GEN NAME START_W STEP_TIME TOTAL_TIME [generator args]
# GEN = b3trail.py or diag_match.py. Descending search: solve with bound W (START_W, or -1 =
# unbounded first); on SAT set W = (counted weight of the model) - 1 and repeat; stop on UNSAT
# (minimum proved), UNKNOWN, or when TOTAL_TIME seconds are used. ONE kissat at a time, each
# with --time; TOTAL_TIME is kept under 600.
set -u
cd "$(dirname "$0")"
gen=$1; name=$2; W=$3; step=$4; total=$5; shift 5
mkdir -p runs
t0=$(date +%s)
best=""
while :; do
  used=$(( $(date +%s) - t0 ))
  left=$(( total - used ))
  [ $left -lt 20 ] && { echo "$name: time budget used; best=$best"; break; }
  tl=$step; [ $tl -gt $left ] && tl=$left
  tag="${name}_W${W}"
  python3 -B "$gen" --W "$W" --out "runs/$tag" "$@" > "runs/$tag.gen.txt" 2>&1
  kissat --time="$tl" -q "runs/$tag.cnf" > "runs/$tag.sol" 2>&1
  rc=$?
  python3 -B decode.py "runs/$tag" "runs/$tag.sol" --json "runs/$tag.dec.json" > "runs/$tag.dec.txt" 2>&1
  grep -v '^v ' "runs/$tag.sol" > "runs/$tag.sol.txt"; rm -f "runs/$tag.sol" "runs/$tag.cnf"
  cw=$(grep -E '^COUNTED WEIGHT' "runs/$tag.dec.txt" | awk -F': ' '{print $2}')
  echo "$tag rc=$rc counted=${cw:-none} t=$(( $(date +%s) - t0 ))s" | tee -a runs/LOG.txt
  if [ $rc -eq 10 ]; then best=$cw; W=$(( cw - 1 )); [ $W -lt 0 ] && break; continue; fi
  if [ $rc -eq 20 ]; then echo "$name: UNSAT at W=$W -> minimum = $(( W + 1 )) (best model $best)"; break; fi
  echo "$name: UNKNOWN at W=$W (best model $best)"; break
done
echo "$name done best=$best lastW=$W" >> runs/LOG.txt
