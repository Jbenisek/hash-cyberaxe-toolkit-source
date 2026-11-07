#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Step 6: exact tables and the comparison with GPT Sol's files for one run, or the cost table.
#   c06_tab.sh a15 | a17 | full | cost
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
H="${HASHCYBERAXE_WORKSPACE}/research/pkg7/count"
cd "$H" || exit 3
case "${1:-a15}" in
  a15|a17) python3 -B sub_tab.py "$1.out" "$1" "$1" F5,old6,S6,S7,S8,S9,p5,p4 > "tab_$1.log" 2>&1; echo "tables $1 exit $?"; grep -E '^(R |total R|rule|outcomes with|betas|gpt_sol|RESULT|outcomes of)' "tab_$1.log" | cut -c1-250 ;;
  full)    python3 -B sub_tab.py full.out full full F5,old6,K7,K8,S6,S7,S8,p5 > tab_full.log 2>&1; echo "tables full exit $?"; grep -E '^(R |total R|rule|outcomes with|betas|RESULT|outcomes of)' tab_full.log | cut -c1-250 ;;
  cost)    python3 -B cost.py ;;
esac
