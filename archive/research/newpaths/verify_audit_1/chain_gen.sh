#!/bin/bash
cd "$(dirname "$0")"
# wait (max 90 min) for the plain look k<=6 run to finish, then run look + gen rules k<=6 with 6 processes
for i in $(seq 1 1080); do [ -f lk2_plain_look_desc_k6.out ] && break; sleep 5; done
./run2.sh gen 6 6 look desc ../audit/rules_fixed_len64_gen.txt 5400
