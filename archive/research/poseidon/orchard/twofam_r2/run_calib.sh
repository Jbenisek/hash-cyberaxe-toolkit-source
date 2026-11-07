#!/bin/bash
cd "$(dirname "$0")"
bash build.sh calib 2>&1 | grep -i error
SMALL=$(seq 3 47 | tr '\n' ' ')
nice -n 10 ./calib s $SMALL 95 190 381 762 1525 3051 6103 12207 24414 48828 97656 195312 390625 r390625 r1000 > logs/calib.txt 2>&1
echo "EXIT $?" >> logs/calib.txt
