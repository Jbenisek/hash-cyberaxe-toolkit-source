#!/bin/bash
cd "$(dirname "$0")"
bash build_base.sh single_dump '-DDUMP_D="dump_110.bin"' && nice -n 10 ./single_dump 110 > logs/base_dump_110.txt 2>&1; echo EXIT $? >> logs/base_dump_110.txt
