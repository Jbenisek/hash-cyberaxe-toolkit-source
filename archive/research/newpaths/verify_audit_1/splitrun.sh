#!/bin/bash
cd "$(dirname "$0")"
# canonical (sorted words) unique 7-sets
cat greedy7_a.txt greedy7_b.txt | while read -r l; do echo $l | tr ' ' '\n' | sort | tr '\n' ' '; echo; done | sort -u > covers7.txt
wc -l covers7.txt
split -n l/2 -d covers7.txt c7part_
timeout 110 ./split sys_fixed_plain.txt split < c7part_00 > split_00.out &
timeout 110 ./split sys_fixed_plain.txt split < c7part_01 > split_01.out &
wait
rm -f c7part_*
tail -1 split_00.out; tail -1 split_01.out
