#!/bin/bash
pkill -f "variants/job3.sh"
pkill -f "run_gdx.sh 1700 8 200000"
sleep 1
pkill -f "./gdx models/fixed_02_64_t1"
pkill -f "./gdx models/fixed_13_64_t1"
sleep 1
ps -eo pid,etime,args | grep -E 'gdx|job3' | grep -v grep | head
