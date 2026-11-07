#!/bin/bash
# after job7: f=2 partial, splits on table models and half 13 (2 processes)
cd "$(dirname "$0")"
./kmin_q.sh 2 1700 8 8 part_02_t0_Y5-Y13 part_02_t0_Y5-m9 part_02_t0_Y13-m9 part_02_t0_Y5-Y13-m9
( timeout 1500 ./split models/part_02_t0_Y5-Y13.mdl res/part_02_t0_Y5-Y13_k8.out 6 96 100000 > res/split_part_02_t0_Y5-Y13_k8.txt ) &
( timeout 1500 ./split models/fixed_02_64_t1.mdl res/fixed_02_64_t1_k8.out 4 64 60000 > res/split_fixed_02_64_t1_k8.txt ) &
wait
( timeout 1500 ./split models/fixed_02_64_t2.mdl res/fixed_02_64_t2_k8.out 4 64 60000 > res/split_fixed_02_64_t2_k8.txt ) &
( timeout 1500 ./split models/fixed_13_64_t0.mdl res/fixed_13_64_t0_k9.out 4 64 15000 > res/split_fixed_13_64_t0_k9.txt ) &
wait
( timeout 1500 ./split models/part_02_t0_m9.mdl res/part_02_t0_m9_k8.out 5 80 100000 > res/split_part_02_t0_m9_k8.txt ) &
( timeout 1500 ./split models/part_02_t0_Y5-Y13-m9.mdl res/part_02_t0_Y5-Y13-m9_k8.out 7 112 100000 > res/split_part_02_t0_Y5-Y13-m9_k8.txt ) &
wait
( timeout 1500 ./split models/fixed_02_55_t0.mdl res/fixed_02_55_t0_k8.out 3 64 80000 > res/split_fixed_02_55_t0_k8.txt ) &
( timeout 1500 ./split models/len_13_52_t0.mdl res/len_13_52_t0_k7.out 2 64 30000 > res/split_len_13_52_t0_k7.txt ) &
wait
for f in res/split_*.txt; do echo "$f: $(grep -E '^solutions' $f) $(grep -E '^histogram' $f)"; done > res/split_summary.txt
echo JOB9DONE >> res/split_summary.txt
