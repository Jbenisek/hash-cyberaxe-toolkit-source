#!/bin/bash
cd "$(dirname "$0")"
for d in 140000 270000 ; do
setsid nohup bash -c "nice -n 10 ./test_gcd $d > logs/test_gcd_$d.txt 2>&1" > /dev/null 2>&1 < /dev/null &
done
sleep 1; pgrep -a test_gcd
