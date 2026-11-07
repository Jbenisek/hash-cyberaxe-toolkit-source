#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Regenerate the evidence files of this package with the program as it now is (its run length was lengthened for
# the clusters: one constant, which no measurement below depends on, but the files carry the program's hash and
# must match it). Each tool writes its own file under work/evidence. Research helper; nothing is submitted.
#   regen_evidence.sh            the quick tools
#   regen_evidence.sh slow       the long ones as well
set -uo pipefail
P="${HASHCYBERAXE_WORKSPACE}/research/pkg9/pkg"
cd "$P" || exit 1
run() { name=$1; shift; printf '%-22s' "$name"; t0=$(date +%s)
  if timeout 1500 python -B "work/tools/$name.py" "$@" > "work/evidence/.$name.tmp" 2>&1; then
    mv "work/evidence/.$name.tmp" "work/evidence/$name.txt"; echo "ok $(( $(date +%s) - t0 ))s"
  else
    echo "FAILED $(( $(date +%s) - t0 ))s (file kept as .$name.tmp)"; fi; }
for q in check_program counts register_peaks lane_bound tracer_counts every_use text_scan ref_compare \
         class_loop plan_negative selftest_small time_experiments; do run "$q"; done
if [ "${1:-}" = slow ]; then for q in lemma_a_enum equiv; do run "$q"; done; fi
