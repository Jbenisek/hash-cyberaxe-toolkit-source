#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: every beta of the package's list (evidence/pinB_e7c1815f.total, 4,272 betas):
# does the seven-word system with Y4 in the class have a solution with that beta at all?  cadical, 5 threads.
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
L="${HASHCYBERAXE_WORKSPACE}/research/pkg5/evidence/pinB_e7c1815f.total"
t0=$(date +%s)
python3 -B "$R/math_seven.py" any cadical 5 300 $(cut -d' ' -f1 "$L") 2>&1 | cut -c1-300 | tail -1
A="$R/math_seven_any_cadical.txt"
echo "lines $(wc -l < "$A"); SAT $(grep -c ' SAT ' "$A"); UNSAT $(grep -c ' UNSAT ' "$A"); undecided $(grep -c ' ? ' "$A")"
# the betas with SAT must be the 39 betas with a nonzero part, and the betas with a part must all be SAT
comm -3 <(grep ' SAT ' "$A" | cut -d' ' -f2 | sort) <(awk 'NF == 4 && $4 > 0 {print $1}' "$L" | sort) | wc -l | sed 's/^/betas where SAT and "has a part" differ: /'
echo "seconds $(( $(date +%s) - t0 ))"
