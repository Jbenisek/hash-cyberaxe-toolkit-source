#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: the package's batch on fresh seeds against the organizer's complete hash.
#   math_batch.sh N SEED1 [SEED2 ...]     at most 4 processes at a time
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
N="$1"; shift
t0=$(date +%s)
printf '%s\n' "$@" | xargs -P 4 -I{} python3 -B "$R/math_batch.py" "$N" {} "$R/math_batch_{}.json"
echo "exit $? seconds $(( $(date +%s) - t0 ))"
