#!/bin/bash
cd "$(dirname "$0")"
setsid nohup bash run_attempt.sh 2 404 > /dev/null 2>&1 < /dev/null &
sleep 1; pgrep -a twofam
