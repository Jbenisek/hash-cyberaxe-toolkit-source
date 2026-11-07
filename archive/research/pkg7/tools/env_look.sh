#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# What the rule-A tools need: solvers, the encoder research/r2_sat.py, load. Prints at most ten lines.
R="${HASHCYBERAXE_WORKSPACE}/research"
echo "nproc $(nproc) load $(cut -d' ' -f1-3 /proc/loadavg)"
for t in kissat cadical cryptominisat5 approxmc python3; do printf '%s: %s\n' "$t" "$(command -v $t || echo MISSING)"; done
ls -la "$R/r2_sat.py" 2>&1 | cut -c1-120
ps -eo pcpu,comm --sort=-pcpu | head -4 | tr '\n' ';'; echo
