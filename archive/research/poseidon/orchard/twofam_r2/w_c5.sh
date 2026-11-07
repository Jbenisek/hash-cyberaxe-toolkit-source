#!/bin/bash
cd "$(dirname "$0")"
setsid nohup bash run_cert.sh 505 > /dev/null 2>&1 < /dev/null &
sleep 1; pgrep -a certrun
