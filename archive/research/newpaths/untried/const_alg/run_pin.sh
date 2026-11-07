#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_pin.sh NAME KMAX [BUDGET=1140] [W=2] [SYSTIMEOUT=120] [SAMPLE=300]
# One pin through the atlas pipeline (ctr_count.py: research/paths scripts imported unchanged, outputs here):
#   filter (betas with k <= KMAX) -> sys (kissat on those with a passing outcome) -> satcount -> report.
# W processes at nice 5 (the brief allows at most 2). The calculator step gets what is left of BUDGET seconds
# (minus 45 s for the report), so the whole run stays under 20 minutes. Log: status.txt; own PID: pids.txt.
# Started with setsid, so the whole run is one process group that can be stopped by its own PGID (never by name).
export PYTHONDONTWRITEBYTECODE=1
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
cd "$D" || exit 3
n=$1; K=$2; BUD=${3:-1140}; W=${4:-2}; TO=${5:-120}; SMP=${6:-300}
T0=$(date +%s)
echo "$(date +%H:%M:%S) run_pin $n K<=$K budget ${BUD}s W=$W pid $$ pgid $(ps -o pgid= $$ | tr -d ' ')" >> "$D/pids.txt"
for step in filter sys satcount report; do
  [ -f "$D/STOP" ] && { echo "$(date +%H:%M:%S) STOP file, $n ends before $step" >> "$D/status.txt"; exit 0; }
  t0=$(date +%s)
  case $step in
    filter)   r=$(nice -n 5 python3 -B ctr_count.py filter "$n" "$W" "$K" 2>> "$D/run.err" | tail -1);;
    sys)      r=$(nice -n 5 python3 -B ctr_count.py sys "$n" "$W" "$TO" "$SMP" "$K" 2>> "$D/run.err" | tail -1);;
    satcount) left=$(( BUD - (t0 - T0) - 45 ))
              if [ "$left" -lt 30 ]; then r="satcount $n: SKIPPED, budget used up before the calculator step"
              else r=$(nice -n 5 python3 -B ctr_count.py satcount "$n" "$W" "$left" 2>> "$D/run.err" | tail -1); fi;;
    report)   r=$(nice -n 5 python3 -B ctr_count.py report "$n" 2>> "$D/run.err" | tail -1);;
  esac
  echo "$(date +%H:%M:%S) [${step} $(( $(date +%s) - t0 ))s] $(echo "$r" | cut -c1-700)" >> "$D/status.txt"
done
echo "$(date +%H:%M:%S) run_pin $n done in $(( $(date +%s) - T0 ))s" >> "$D/status.txt"
