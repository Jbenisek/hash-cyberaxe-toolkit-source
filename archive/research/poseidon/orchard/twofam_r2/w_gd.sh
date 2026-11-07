#!/bin/bash
cd "$(dirname "$0")"
bash build.sh test_gcd_dump 2>&1 | grep -i " error"
setsid nohup bash -c 'nice -n 10 ./test_gcd_dump 4000 0 > logs/gcd_dump_b.txt 2>&1' > /dev/null 2>&1 < /dev/null &
sleep 1; pgrep -a test_gcd_dump
