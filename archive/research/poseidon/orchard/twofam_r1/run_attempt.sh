#!/bin/bash
# usage: run_attempt.sh seed   -> logs/attempt_<seed>.txt (exit status on the last line)
cd "$(dirname "$0")"
nice -n 10 ./twofam 1 $1 > logs/attempt_$1.txt 2>&1
echo "EXIT $?" >> logs/attempt_$1.txt
