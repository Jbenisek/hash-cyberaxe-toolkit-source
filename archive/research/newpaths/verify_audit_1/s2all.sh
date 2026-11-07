#!/bin/bash
cd "$(dirname "$0")"
split -n l/2 -d covers7all.txt c7all_
timeout 2400 ./split2 sys_fixed_plain.txt < c7all_00 > split2_all_00.out &
timeout 2400 ./split2 sys_fixed_plain.txt < c7all_01 > split2_all_01.out &
wait
PLAIN=1 timeout 600 ./split2 sys_fixed_plain.txt < covers8p.txt > split2_plain8_v2.out
rm -f c7all_*
tail -1 split2_all_00.out; tail -1 split2_all_01.out; tail -1 split2_plain8_v2.out
