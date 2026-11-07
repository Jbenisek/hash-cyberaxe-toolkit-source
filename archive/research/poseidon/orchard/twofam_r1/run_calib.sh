#!/bin/bash
cd "$(dirname "$0")"
nice -n 10 ./calib 4 9 19 38 76 152 305 610 1220 2441 4882 9765 19531 39062 78125 r78125 r1000 > logs/calib.txt 2>&1
