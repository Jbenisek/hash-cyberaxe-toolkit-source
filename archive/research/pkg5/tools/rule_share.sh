#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Rule A and the entries into stage 2 on real trials in the layout of proof.md 6.4: builds tools/rule_share.c under
# a name of its own, checks it against the real compression, runs it and keeps the output as
# evidence/rule_share_<seed>.txt (first line: the check of the vectors; then one line per run and a summary).
# CPU only. Research helper, not submitted.
#
#   wsl -d Ubuntu -- bash './research/pkg5/tools/rule_share.sh' [RUNS CONTEXTS ALPHAS SEED THREADS]
#
# Defaults: 24 runs, 1,024 contexts per run, 16 values of alpha per context, seed 20261006, 4 threads. A run is
# CONTEXTS * ALPHAS * 65,536 trials: every member of the class, in batch order, for every sampled context and alpha.
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
T="$HOME/hashsmash/pkg5-author"
RUNS="${1:-24}"; CTX="${2:-1024}"; AL="${3:-16}"; SEED="${4:-20261006}"; TH="${5:-4}"
OUT="$PKG/evidence/rule_share_$SEED.txt"
mkdir -p "$T"
gcc -O2 -fopenmp -o "$T/pkg5_rule_share" "$PKG/tools/rule_share.c" -lm 2> "$T/rule_share_build.log" || { echo "build failed"; head -5 "$T/rule_share_build.log"; exit 3; }
"$T/pkg5_rule_share" vectors 20000 7 | python3 -B "$PKG/tools/rule_share_vectors.py" > "$T/rule_share_vectors.out" 2>&1
status=$?
tail -1 "$T/rule_share_vectors.out" | cut -c1-240
if [ "$status" != 0 ]; then echo "the C program does not agree with the real compression; nothing written"; exit 4; fi
t0=$(date +%s)
OMP_NUM_THREADS="$TH" nice -n 5 "$T/pkg5_rule_share" "$RUNS" "$CTX" "$AL" "$SEED" > "$T/rule_share_$SEED.out" || { echo "run failed"; exit 5; }
{ echo "SOURCE tools/rule_share.c sha256 $(sha256sum "$PKG/tools/rule_share.c" | cut -c1-64) arguments $RUNS $CTX $AL $SEED seconds $(( $(date +%s) - t0 )) threads $TH"
  tail -1 "$T/rule_share_vectors.out"
  cat "$T/rule_share_$SEED.out"; } > "$OUT"
tail -1 "$OUT" | cut -c1-420
head -1 "$OUT" | cut -c1-200
