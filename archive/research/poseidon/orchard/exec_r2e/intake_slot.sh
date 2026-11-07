#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# intake_slot.sh SLOT: organizer intake of a staged slot (output kept in logs/intake_raw.txt); run through research/tools/fast/intake_paused.sh
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
S=$(echo "$1" | tr A-Z a-z); cd "/root/hashsmash/yukon/pos_$S/pareto" || exit 1
O="${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/exec_r2e/logs/intake_raw.txt"
date > "$O"; nice -n 10 python3 -B ../scripts/pareto_pipeline.py --family poseidon intake >> "$O" 2>&1; echo "rc=$?" >> "$O"; date >> "$O"
grep -o '"status": "[a-z_]*"' "$O" | tail -2; tail -3 "$O" | cut -c1-300
