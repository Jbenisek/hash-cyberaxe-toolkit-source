#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# The second formula with two other solvers (tools/rule_a_sat2.py) for the rules named (default 5 4 6), three threads.
# Run after tools/rule_a_sat_all.sh. Log: evidence/rule_a_sat2_all.log. Research helper, not submitted. CPU only.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg6"
L="$P/evidence/rule_a_sat2_all.log"
export PYTHONDONTWRITEBYTECODE=1
: > "$L"
for n in ${*:-5 4 6}; do
  for s in cadical cryptominisat5; do
    t0=$(date +%s)
    echo "== rule $n, $s" >> "$L"
    python3 -B "$P/tools/rule_a_sat2.py" "$n" "$s" 3 >> "$L" 2>&1
    echo "rule $n $s: exit $? seconds $(( $(date +%s) - t0 ))" >> "$L"
  done
done
echo "done $(date +%H:%M:%S)" >> "$L"
tail -1 "$L"
