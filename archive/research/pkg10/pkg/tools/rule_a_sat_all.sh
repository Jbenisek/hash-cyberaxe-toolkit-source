#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
echo "STOP: copy of a script of research/pkg6 inside research/pkg7; it still points at research/pkg6, which is filed and read only. Not ported yet (PROGRAM_STEP.md, section 6 item 1)."; exit 9
# The three first-stage rules against every outcome of the count (tools/rule_a_sat.py), one rule after the other,
# three solver threads; then the two completed solutions per rule. Log: evidence/rule_a_sat_all.log.
# Research helper, not submitted. CPU only.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg6"
L="$P/evidence/rule_a_sat_all.log"
export PYTHONDONTWRITEBYTECODE=1
: > "$L"
for n in ${*:-5 4 6}; do
  t0=$(date +%s)
  python3 -B "$P/tools/rule_a_sat.py" "$n" 3 >> "$L" 2>&1
  echo "rule $n: exit $? seconds $(( $(date +%s) - t0 ))" >> "$L"
  python3 -B "$P/tools/rule_a_sat.py" "$n" example >> "$L" 2>&1
  echo "rule $n example: exit $?" >> "$L"
done
echo "done $(date +%H:%M:%S)" >> "$L"
tail -1 "$L"
