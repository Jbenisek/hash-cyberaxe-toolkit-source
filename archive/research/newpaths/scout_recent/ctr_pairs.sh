#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# ctr_pairs.sh COUNTER PIN_EXTRA TMO TARGET..   (scout_recent; at most 2 kissat processes at a time)
# For each TARGET: is there a basis that contains Y4 AND TARGET (two prescribed residual words per trial)?
# COUNTER=0 is the team's original system (counter word fixed at 0); COUNTER=1 adds the chunk-counter
# low word T0 as a free unknown in K0's d input (non-root chunk at index t); COUNTER=2 adds T1 too.
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/scout_recent"
export PYTHONDONTWRITEBYTECODE=1
export COUNTER="$1"; export PIN_EXTRA="$2"; TMO="$3"; shift 3
printf '%s\n' "$@" | xargs -P 2 -I{} bash -c "r=\$(python3 -B basis_sat_ctr.py Y4,{} --time $TMO 2>&1 | head -1 | cut -c1-400); echo \"COUNTER=$COUNTER PIN_EXTRA=$PIN_EXTRA Y4+{}: \$r\""
