#!/bin/bash
cd "$(dirname "$0")"
for k in 1 2 3 4 5 6; do ./run_gdx.sh 600 8 50 $k fixed_02_64_t2 fixed_13_64_t2 > /dev/null; done
grep t2 res/summary.log
./run_gdx.sh 1500 8 200 8 fixed_02_64_t0 fixed_13_64_t0 fixed_02_64_t1 fixed_13_64_t1
