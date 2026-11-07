#!/bin/bash
cd "$(dirname "$0")"
for m in plain tables t2; do
  timeout 2400 ./jtree sys_outhalf_$m.txt oh2_$m.txt 10 0 > jt_outhalf_$m.out &
done
wait
echo "jt_oh done $(date)" >> jt_run.log
