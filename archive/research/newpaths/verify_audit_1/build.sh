#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o lk lk.c 2>&1
echo built $?
G="K2.c1 K3.d1 K3.d2 C3.a2 m0 D1.d1 K2.d2 C0.a1"
{
echo "$G"
for x in $G; do echo "$G" | tr ' ' '\n' | grep -vx "$x" | tr '\n' ' '; echo; done
} > greedy_sets.txt
echo "== plain: greedy8 then its 8 seven-subsets"; ./lk sys_fixed_plain.txt check plain < greedy_sets.txt
echo "== look : greedy8 then its 8 seven-subsets"; ./lk sys_fixed_plain.txt check look < greedy_sets.txt
