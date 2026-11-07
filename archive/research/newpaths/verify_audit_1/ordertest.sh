#!/bin/bash
cd "$(dirname "$0")"
R=../audit/rules_fixed_len64_orig.txt
P=../audit/rules_fixed_len64_pair.txt
for ss in 5 6 7; do
  timeout 100 ./lk sys_fixed_plain.txt ordertest 150 $ss - | tail -3 &
  timeout 100 ./lk sys_fixed_plain.txt ordertest 150 $ss $R | tail -3 &
done
wait
