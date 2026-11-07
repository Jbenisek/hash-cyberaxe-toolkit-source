#!/bin/bash
cd "$(dirname "$0")"
# wait (max 60 min) for the plain k<=7 run (2 processes) to finish, then use those 2 slots for the 8-set split test
for i in $(seq 1 720); do [ -f lk2_plain_plain_desc_k7.out ] && break; sleep 5; done
gcc -O3 -march=native -Wno-unused-result -o split2 split2.c || exit 1
split -n l/2 -d sets8_plus1.txt s8_
BAL=1 timeout 3000 ./split2 sys_fixed_plain.txt < s8_00 > split2_s8_00.out &
BAL=1 timeout 3000 ./split2 sys_fixed_plain.txt < s8_01 > split2_s8_01.out &
wait
rm -f s8_0*
tail -1 split2_s8_00.out; tail -1 split2_s8_01.out
