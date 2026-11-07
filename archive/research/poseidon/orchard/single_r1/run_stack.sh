#!/bin/bash
# the complete run under a 64 KiB stack limit
cd "$(dirname "$0")"
ulimit -s 64
nice -n 10 ./single 102 > logs/stack64_102.txt 2>&1
echo "EXIT $?" >> logs/stack64_102.txt
