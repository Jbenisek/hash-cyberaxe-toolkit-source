#!/bin/bash
cd "$(dirname "$0")"
bash build_base.sh single_mem || exit 1
nice -n 10 ./single_mem 110 > logs/mem_110.txt 2>&1 &
P1=$!
nice -n 10 ./single_mem 103 > logs/mem_103.txt 2>&1 &
P2=$!
wait $P1; echo EXIT $? >> logs/mem_110.txt
wait $P2; echo EXIT $? >> logs/mem_103.txt
