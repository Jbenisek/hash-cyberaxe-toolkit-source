#!/bin/bash
cd "$(dirname "$0")"
pkill -f "cv_run.sh"; pkill -f "gdcv models"; sleep 1
gcc -O3 -march=native -o stagecheck stagecheck.c 2>&1 | grep -i error
timeout 110 ./stagecheck models/cv_part_02_Y13.mdl res/stage_Y13.txt 5 | tee res/stage_Y13.out | tail -4
