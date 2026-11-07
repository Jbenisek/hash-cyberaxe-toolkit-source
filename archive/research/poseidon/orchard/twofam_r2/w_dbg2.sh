#!/bin/bash
cd "$(dirname "$0")"
setsid nohup bash -c 'timeout 2400 nice -n 10 ./twofam_dbg 2 401 > logs/dbg401.txt 2>&1' > /dev/null 2>&1 < /dev/null &
sleep 1; pgrep -a twofam_dbg
