#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exact_new8.sh: both calculators on the beta that the counter-objective solver returned for the new delta-8 pin N8a
# (pinctr.log, seed 52): the atlas's h8_pair_calc_batch (exact_beta.py) and the night's night_pair_calc (one thread),
# side by side = 2 processes, nice 5, 600 s limit each. Output appended to exact.log.
export PYTHONDONTWRITEBYTECODE=1
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
cd "$D" || exit 3
echo "$(date +%H:%M:%S) exact_new8 pid $$" >> "$D/pids.txt"
nice -n 5 python3 -B exact_beta.py aac82f8d 5d37f74f fffffff8 aa9c4839 f2a00058 30f35548 8f1e3580 600 > "$D/scratch/exact_n8a_batch.out" 2>> "$D/run.err" &
r=$(OMP_NUM_THREADS=1 nice -n 5 timeout 600 "$HOME/hashsmash/bin/night_pair_calc" aac82f8d 5d37f74f fffffff8 aa9c4839 30f35548 8f1e3580 31 -y11 f2a00058 2>&1)
st=$?
wait
cat "$D/scratch/exact_n8a_batch.out" >> "$D/exact.log"
echo "night_pair_calc N8a 8f1e3580 exit $st: $(echo "$r" | grep -E 'positive|^EXACT' | tr '\n' ' ' | cut -c1-600)" >> "$D/exact.log"
echo "$(date +%H:%M:%S) exact_new8 done" >> "$D/exact.log"
