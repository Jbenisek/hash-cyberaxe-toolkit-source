#!/bin/bash
# bisect.sh GEN NAME STEP_TIME TOTAL_TIME [generator args]
# GEN = b3trail.py or diag_match.py. First an unbounded solve (W=-1) for an upper bound hi,
# then bisection on [lo, hi): W = (lo+hi)/2; SAT -> hi = counted weight of the model;
# UNSAT -> lo = W+1 (proved); UNKNOWN -> lo = W+1 but the bound is marked unproved.
# ONE kissat at a time, each with --time; TOTAL_TIME kept under 600 s.
set -u
cd "$(dirname "$0")"
gen=$1; name=$2; step=$3; total=$4; shift 4
mkdir -p runs
t0=$(date +%s)
lo=0; hi=-1; proved=0; W=-1
while :; do
  used=$(( $(date +%s) - t0 )); left=$(( total - used ))
  [ $left -lt 15 ] && { echo "$name: time budget used"; break; }
  tl=$step; [ $tl -gt $left ] && tl=$left
  tag="${name}_W${W}"
  python3 -B "$gen" --W "$W" --out "runs/$tag" "$@" > "runs/$tag.gen.txt" 2>&1
  kissat --time="$tl" -q "runs/$tag.cnf" > "runs/$tag.sol" 2>&1
  rc=$?
  python3 -B decode.py "runs/$tag" "runs/$tag.sol" --json "runs/$tag.dec.json" > "runs/$tag.dec.txt" 2>&1
  grep -v '^v ' "runs/$tag.sol" > "runs/$tag.sol.txt"; rm -f "runs/$tag.sol" "runs/$tag.cnf"
  cw=$(grep -E '^COUNTED WEIGHT' "runs/$tag.dec.txt" | awk -F': ' '{print $2}')
  echo "$tag rc=$rc counted=${cw:-none} t=$(( $(date +%s) - t0 ))s" | tee -a runs/LOG.txt
  if [ $rc -eq 10 ]; then hi=$cw
  elif [ $rc -eq 20 ]; then
    if [ $W -lt 0 ]; then echo "$name: UNSAT without bound"; break; fi
    lo=$(( W + 1 )); proved=$lo
  else
    if [ $W -lt 0 ]; then echo "$name: UNKNOWN without bound"; break; fi
    lo=$(( W + 1 ))
  fi
  [ $hi -ge 0 ] && [ $lo -ge $hi ] && break
  W=$(( (lo + hi) / 2 ))
  [ $W -ge $hi ] && W=$(( hi - 1 ))
done
echo "$name RESULT best_found=$hi proved_lower_bound=$proved last_lo=$lo" | tee -a runs/LOG.txt
