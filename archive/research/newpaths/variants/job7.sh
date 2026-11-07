#!/bin/bash
# local search upper bounds (2 processes at a time)
cd "$(dirname "$0")"
M="outhalf_02_64_t0 outhalf_13_64_t0 outhalf_02_64_t1 outhalf_13_64_t1 outhalf_02_64_t2 outhalf_13_64_t2 outhalf_02_55_t0 outhalf_13_55_t0 outhalf_02_55_t2 outhalf_13_55_t2 cust_02_E0in_E2out cust_02_E2in_E0out cust_02_E0out_E2out cust_13_E1in_E3out cust_13_E3in_E1out cust_13_E1out_E3out b1_o4 b1_o0 b1_o4_o5 b1_o4_s0 b1_o4_o5_o6 b1_o4_o5_o6_o7 b1_o0_o1_o2_o3 b1_s0_s1_s2_s3 b1_o4_o5_s0_s1 b1_o0_o4_o1_o5"
./ls_run.sh 60 2 $M > res/ls_job7.txt
echo JOB7DONE >> res/ls_job7.txt
