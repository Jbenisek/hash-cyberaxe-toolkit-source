#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Runs the preregistered jobs of prereg.md (4 at a time). Output lines go to out/*.txt
P="${HASHCYBERAXE_WORKSPACE}/research/blake3_r3/premise"
cd $P
JOBS=/root/b3run/jobs.txt
: > $JOBS
for c in 0 1 2 3; do echo "python3 -B $P/as_test.py /root/b3run 40 target $((c*120)) 120 > $P/out/as40_target_$c.txt" >> $JOBS; done
for c in 0 1 2 3; do echo "python3 -B $P/as_test.py /root/b3run 40 ideal $((c*120)) 120 > $P/out/as40_ideal_$c.txt" >> $JOBS; done
for c in 0 1 2 3; do echo "python3 -B $P/as_test.py /root/b3run 32 target $((c*1000)) 1000 > $P/out/as32_target_$c.txt" >> $JOBS; done
for c in 0 1 2 3; do echo "python3 -B $P/as_test.py /root/b3run 32 ideal $((c*1000)) 1000 > $P/out/as32_ideal_$c.txt" >> $JOBS; done
echo "/root/premise rho 32 2000 1 > $P/out/rho32.txt" >> $JOBS
echo "/root/premise rho 40 300 1 > $P/out/rho40.txt" >> $JOBS
for s in chain counter random; do for k in $(seq 0 13); do echo "/root/premise proj $s $k > $P/out/proj_${s}_$k.txt" >> $JOBS; done; done
cat $JOBS | nice -n 10 xargs -P 4 -I{} bash -c "{}"
echo ALLDONE > $P/out/ALLDONE
