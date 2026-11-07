#!/bin/bash
pkill -f "variants/job4.sh"; pkill -f "kmin_q.sh"; pkill -f "run_gdx.sh 1700 6"
sleep 1; pkill -f "./gdx models/fixed_02_55_t1"; sleep 1
ps -eo args | grep -E 'gdx|job4|kmin_q' | grep -v grep | head -3
