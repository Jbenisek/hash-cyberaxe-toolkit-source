#!/bin/bash
cd "$(dirname "$0")"
./kmin_q.sh 6 1700 1 8 fixed_02_64_t1 fixed_02_64_t2 fixed_02_55_t0 fixed_02_55_t1 fixed_02_55_t2 fixed_13_55_t0 fixed_13_55_t1 fixed_13_55_t2
./kmin_q.sh 6 1700 1 8 fixed_13_64_t1 fixed_13_64_t2
P=$(cd models && ls part_*_t0_*.mdl | grep -v -- '-' | sed 's/.mdl$//')
./kmin_q.sh 6 1700 7 8 $P
./kmin_q.sh 6 1700 9 9 fixed_13_64_t1 fixed_13_64_t2
echo JOB4DONE >> res/kmin.log
