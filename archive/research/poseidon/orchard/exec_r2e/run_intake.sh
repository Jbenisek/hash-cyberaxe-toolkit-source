#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_intake.sh SLOT: intake with my own solver binaries frozen meanwhile (tools/fast/intake_paused.sh), then the outcome file
H="${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/exec_r2e"
bash "${HASHCYBERAXE_WORKSPACE}/research/tools/fast/intake_paused.sh" "$H/intake_slot.sh" "$1"
echo "--- outcome ---"
S=$(echo "$1" | tr A-Z a-z)
cat /root/hashsmash/yukon/pos_$S/pareto/.yukon/work/tracks/poseidon-pareto/pareto-outcome.json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print({k:d.get(k) for k in ('outcome','status','intake','error') if k in d})" 2>/dev/null
