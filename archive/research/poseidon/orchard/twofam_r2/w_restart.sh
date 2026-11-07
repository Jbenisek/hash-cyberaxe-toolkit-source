#!/bin/bash
cd "$(dirname "$0")"
pkill -f "^./twofam [12] 40[0-3]" 
sleep 1
mkdir -p logs/aborted && mv logs/attempt_r* logs/aborted/ 2>/dev/null
bash build.sh twofam 2>&1 | grep -i error
for a in "1 400" "2 401" "2 402" "2 403"; do
  setsid nohup bash run_attempt.sh $a > /dev/null 2>&1 < /dev/null &
done
sleep 2; pgrep -a twofam
