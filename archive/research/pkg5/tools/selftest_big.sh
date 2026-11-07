#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# The self-test of the program in the package with many batches: N batches for each seed text given, one process per
# seed text. Each run prints the program's one JSON line, kept as evidence/selftest_<N>_<seed>.json together with the
# exit status and the SHA-256 of the program that ran. tools/pkg5_data.py quotes these files only while the program
# still has that SHA-256. CPU only, one thread per seed text. Research helper, not submitted.
#
#   wsl -d Ubuntu -- bash './research/pkg5/tools/selftest_big.sh' N seed [seed ...]
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
PROGRAM="$PKG/blake3-r2/experiments/halfsearch.py"
N="$1"; shift
SHA=$(sha256sum "$PROGRAM" | cut -c1-64)
TMP="$HOME/hashsmash/pkg5-selftest"; mkdir -p "$TMP"
cp "$PROGRAM" "$TMP/halfsearch_$SHA.py"
for seed in "$@"; do
  ( t0=$(date +%s)
    PYTHONDONTWRITEBYTECODE=1 nice -n 5 python3 -B -s "$TMP/halfsearch_$SHA.py" --selftest "$N" "$seed" > "$TMP/selftest_${N}_$seed.out" 2> "$TMP/selftest_${N}_$seed.err"
    status=$?
    { echo "PROGRAM sha256 $SHA exit $status seconds $(( $(date +%s) - t0 ))"; cat "$TMP/selftest_${N}_$seed.out"; } > "$PKG/evidence/selftest_${N}_$seed.json"
  ) &
done
wait
for seed in "$@"; do head -1 "$PKG/evidence/selftest_${N}_$seed.json" | sed "s/^/seed $seed: /"; done
