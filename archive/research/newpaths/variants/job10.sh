#!/bin/bash
# outhalf: collect local-search solutions at the best size, then split analysis (F=12, N=2^64)
cd "$(dirname "$0")"
gcc -O3 -march=native -o ls_all ls_all.c 2>/dev/null
gcc -O3 -march=native -o split16 split.c 2>/dev/null
for m in outhalf_02_64_t0 outhalf_13_64_t0; do
  timeout 200 ./ls_all models/$m.mdl 150 5 > res/lsall_$m.out
done
for m in outhalf_02_64_t0 outhalf_13_64_t0; do
  # keep distinct sets (sorted) at k=16
  grep '^SOL' res/lsall_$m.out | awk 'NF==17' | while read -r a rest; do echo "SOL $(echo $rest | tr ' ' '\n' | sort -n | tr '\n' ' ')"; done | sort -u > res/lsall_${m}_k16.sol
  echo "$m distinct 16-sets: $(wc -l < res/lsall_${m}_k16.sol)"
  timeout 1500 ./split16 models/$m.mdl res/lsall_${m}_k16.sol 12 64 40 > res/split_${m}_ls16.txt
  tail -2 res/split_${m}_ls16.txt
done
echo JOB10DONE
