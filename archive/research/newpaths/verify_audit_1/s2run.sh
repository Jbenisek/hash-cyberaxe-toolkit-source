#!/bin/bash
cd "$(dirname "$0")"
timeout 1500 ./split2 sys_fixed_plain.txt < covers7.txt > split2_look7.out &
PLAIN=1 timeout 1500 ./split2 sys_fixed_plain.txt < covers8p.txt > split2_plain8.out &
wait
tail -1 split2_look7.out; tail -1 split2_plain8.out
