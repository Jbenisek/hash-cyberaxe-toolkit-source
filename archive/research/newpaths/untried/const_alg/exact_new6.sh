#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exact_new6.sh: the calculator on the beta that the counter-objective solver returned for the new delta-6 pin
# (pinctr.log, seed 61): one process, nice 5, time limit 600 s. Output appended to exact.log.
export PYTHONDONTWRITEBYTECODE=1
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
cd "$D" || exit 3
echo "$(date +%H:%M:%S) exact_new6 pid $$" >> "$D/pids.txt"
nice -n 5 python3 -B exact_beta.py c972a031 bf0ab0ef 00000006 9b472fe7 e035a78c a031fb8f 13140f5f 600 >> "$D/exact.log" 2>> "$D/run.err"
echo "$(date +%H:%M:%S) exact_new6 done" >> "$D/exact.log"
