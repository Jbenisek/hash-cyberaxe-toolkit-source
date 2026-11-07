#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# One run of the second formula: rule and solver as arguments (for a repeat). Appends to evidence/rule_a_sat2_all.log.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg6"
L="$P/evidence/rule_a_sat2_all.log"
export PYTHONDONTWRITEBYTECODE=1
t0=$(date +%s)
echo "== rule $1, $2 (repeat)" >> "$L"
python3 -B "$P/tools/rule_a_sat2.py" "$1" "$2" 3 >> "$L" 2>&1
echo "rule $1 $2: exit $? seconds $(( $(date +%s) - t0 ))" >> "$L"
tail -4 "$L" | cut -c1-200
