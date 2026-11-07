#!/bin/bash
cd "$(dirname "$0")"
timeout 110 ./stagecheck models/cv_fixed_02_64_t0.mdl res/stage_fixed02.txt 4 > res/stage_fixed02.out; tail -2 res/stage_fixed02.out
timeout 110 ./stagecheck models/cv_part_02_Y5.mdl res/stage_Y5.txt 5 > res/stage_Y5.out; tail -2 res/stage_Y5.out
