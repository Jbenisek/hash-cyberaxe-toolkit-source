#!/bin/bash
# MITM split analysis of the k=8 solutions of the partial (f=1) models: F=5, members needed 2^80
cd "$(dirname "$0")"
for f in res/part_02_t0_*_k8.out; do
  m=$(basename $f _k8.out)
  n=$(grep -c '^SOL' $f)
  [ "$n" = "0" ] && continue
  ( timeout 1200 ./split models/$m.mdl $f 5 80 100000 > res/split_${m}_k8.txt ) &
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 1; done
done
wait
for f in res/split_part_02_*; do echo "$f: $(grep -E '^solutions' $f)"; done > res/split_partial_summary.txt
echo JOB6DONE >> res/split_partial_summary.txt
