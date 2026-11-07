#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_sat.sh - sanity checks, then kissat --time=600 on {55,63,L3} for L3 in 47 59 61 62 (parallel; own PIDs only).
D="${HASHCYBERAXE_WORKSPACE}"/research/fifties/angles/a4
cd "$D" || exit 1
mkdir -p sat
# sanity 1: documented pins with L3=63 must be SAT; sanity 2: documented pins with L3=59 must be UNSAT (M2)
python3 c3cnf.py gen 63 sat/sanity63.cnf --fixpins
python3 c3cnf.py gen 59 sat/sanity59.cnf --fixpins
kissat -q --time=60 sat/sanity63.cnf > sat/sanity63.out; echo "sanity63 exit $?"
kissat -q --time=60 sat/sanity59.cnf > sat/sanity59.out; echo "sanity59 exit $?"
grep '^s ' sat/sanity63.out sat/sanity59.out
pids=()
for L in 47 59 61 62; do
  python3 c3cnf.py gen $L sat/c3_$L.cnf
  ( /usr/bin/time -f "L=$L wall %e s" kissat -q --time=600 sat/c3_$L.cnf > sat/c3_$L.out 2> sat/c3_$L.time ) &
  pids+=($!)
done
echo "pids ${pids[*]}" > sat/pids.txt
wait "${pids[@]}"
for L in 47 59 61 62; do
  cat sat/c3_$L.time
  python3 c3cnf.py check $L sat/c3_$L.out sat/c3_$L.cnf
done
