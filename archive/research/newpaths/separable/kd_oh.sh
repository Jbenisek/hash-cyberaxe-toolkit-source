#!/bin/bash
cd "$(dirname "$0")"
for m in plain tables t2; do
  timeout 3000 ./kdiag2 sys_outhalf_$m.txt oh16_$m.txt > kd2_outhalf_$m.out &
done
wait
echo "kd_oh done $(date)" >> jt_run.log
