#!/bin/bash
cd "$(dirname "$0")"
start=$(date +%s)
./fibers_w4 3 b 9 e > fibers_w4_q1.txt 2>&1
echo "elapsed $(( $(date +%s) - start )) s" >> fibers_w4_q1.txt
