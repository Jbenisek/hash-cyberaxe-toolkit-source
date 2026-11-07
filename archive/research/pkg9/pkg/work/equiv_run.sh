#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# work/tools/equiv.py in WSL: N batches in all, split over the given number of processes (at most three), each
# started with nice -n 5. Research helper, not submitted.
#
#   wsl -d Ubuntu -- bash "./research/pkg7/work/equiv_run.sh" 200000 e1 2
set -uo pipefail
ROOT="${HASHCYBERAXE_WORKSPACE}/research/pkg7"
N="$1"; SEED="$2"; SHARDS="$3"
if [ "$SHARDS" -gt 3 ]; then echo "at most three processes"; exit 2; fi
cd "$ROOT"
LOG="$HOME/hashsmash/pkg7run"; mkdir -p "$LOG"
for s in $(seq 0 $((SHARDS - 1))); do
  PYTHONDONTWRITEBYTECODE=1 nice -n 5 python3 -B work/tools/equiv.py "$N" "$SEED" "$s" "$SHARDS" > "$LOG/equiv_${SEED}_$s.out" 2>&1 &
done
wait
for s in $(seq 0 $((SHARDS - 1))); do
  echo "shard $s: $(grep -E '^different|^RESULT' "$LOG/equiv_${SEED}_$s.out" | tr '\n' ' ' | cut -c1-200)"
done
