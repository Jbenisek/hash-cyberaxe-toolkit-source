#!/bin/bash
cd "$(dirname "$0")"
timeout 3000 ./jtree sys_fixed_plain.txt ls8_plain.txt 3 0 > jt_fixed_plain_ls8.out
timeout 3000 ./kdiag sys_fixed_plain.txt ls8_plain.txt > kd_fixed_plain_ls8.out
timeout 3000 ./jtree sys_fixed_tables.txt ls8_plain.txt 3 0 > jt_fixed_tables_ls8plain.out
timeout 3000 ./jtree sys_fixed_t2.txt ls8_t2.txt 3 0 > jt_fixed_t2_ls8.out
timeout 3000 ./kdiag sys_fixed_t2.txt ls8_t2.txt > kd_fixed_t2_ls8.out
echo "jt_seq done $(date)" >> jt_run.log
