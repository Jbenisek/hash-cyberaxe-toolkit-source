#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
echo "STOP: copy of a script of research/pkg6 inside research/pkg7; it still points at research/pkg6, which is filed and read only. Not ported yet (PROGRAM_STEP.md, section 6 item 1)."; exit 9
# The third formula on all outcomes (tools/rule_formula3_h8.py), DRAT proofs for the kept outcomes with their check
# (tools/rule_drat_h8.py) and the controls of the checker (tools/rule_drat_control_h8.py). Two workers, CPU only.
# Run after tools/rule_a_sat_all.sh and a build (the first program reads the table of kept outcomes in proof.md).
# Log: evidence/rule_drat_all.log. Research helper, not submitted.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg6"
L="$P/evidence/rule_drat_all.log"
export PYTHONDONTWRITEBYTECODE=1
: > "$L"
for s in "rule_formula3_h8.py 2" "rule_drat_h8.py 2 12" "rule_drat_control_h8.py"; do
  t0=$(date +%s)
  echo "== $s" >> "$L"
  python3 -B "$P/tools/"$s 2>&1 | cut -c1-400 >> "$L"
  echo "$s: exit ${PIPESTATUS[0]} seconds $(( $(date +%s) - t0 ))" >> "$L"
done
echo "done $(date +%H:%M:%S)" >> "$L"
grep -c ": exit 0 " "$L"
tail -1 "$L"
