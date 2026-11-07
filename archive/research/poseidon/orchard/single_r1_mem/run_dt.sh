#!/bin/bash
cd "$(dirname "$0")"
bash build_dtest.sh dtest_mt -DMEMTRACE || exit 1
nice -n 10 ./dtest_mt dump_110.bin > logs/dt_base.txt 2> logs/dt_base.err
echo EXIT $? >> logs/dt_base.txt
