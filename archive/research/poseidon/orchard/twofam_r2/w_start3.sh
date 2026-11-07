#!/bin/bash
cd "$(dirname "$0")"
for s in 405; do
setsid nohup bash run_attempt.sh 2 $s > /dev/null 2>&1 < /dev/null &
done
sleep 1; pgrep -a twofam
