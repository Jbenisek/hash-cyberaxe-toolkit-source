#!/bin/bash
cd "$(dirname "$0")"
./kmin_q.sh 2 1700 1 8 len_02_52_t0 len_13_52_t0 len_13_48_t0
echo JOB8DONE >> res/kmin.log
