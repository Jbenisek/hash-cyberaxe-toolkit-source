#!/bin/bash
# usage: run_attempt.sh r seed   -> logs/attempt_r<r>_<seed>.txt (exit status on the last line)
cd "$(dirname "$0")"
nice -n 10 ./twofam $1 $2 > logs/attempt_r$1_$2.txt 2>&1
echo "EXIT $?" >> logs/attempt_r$1_$2.txt
