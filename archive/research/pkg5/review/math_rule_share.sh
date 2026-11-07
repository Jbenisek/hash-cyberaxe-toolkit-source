#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: rule A and stage-2 entries in the layout of proof.md 6.4 (CPU, 5 threads).
#   math_rule_share.sh RUNS CONTEXTS ALPHAS SEED
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
T="$HOME/hashsmash/pkg5-review-math"
mkdir -p "$T"
gcc -O2 -fopenmp -o "$T/math_rule_share" "$R/math_rule_share.c" -lm 2> "$T/build.log" || { echo "build failed"; head -5 "$T/build.log"; exit 3; }
"$T/math_rule_share" vectors 20000 7 | python3 -B "$R/math_rule_vectors.py" 2>&1 | tail -2
t0=$(date +%s)
OMP_NUM_THREADS=5 "$T/math_rule_share" "${1:-24}" "${2:-1024}" "${3:-16}" "${4:-20261006}" > "$R/math_rule_share_${4:-20261006}.txt"
tail -1 "$R/math_rule_share_${4:-20261006}.txt" | cut -c1-600
echo "seconds $(( $(date +%s) - t0 ))"
