#!/bin/bash
cd "$(dirname "$0")"
bash build.sh calib 2>&1 | grep -i error
nice -n 10 ./calib s 5 11 23 40 47 95 190 2>&1
