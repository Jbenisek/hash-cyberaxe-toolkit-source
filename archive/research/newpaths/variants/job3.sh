#!/bin/bash
# first k with a solution, for every fixed model; prints up to 200000 solutions per proc
cd "$(dirname "$0")"
for m in fixed_02_64_t0 fixed_13_64_t0 fixed_02_64_t1 fixed_13_64_t1 fixed_02_64_t2 fixed_13_64_t2 \
         fixed_02_55_t0 fixed_13_55_t0 fixed_02_55_t1 fixed_13_55_t1 fixed_02_55_t2 fixed_13_55_t2; do
  for k in 1 2 3 4 5 6 7 8 9 10; do
    line=$(./run_gdx.sh 1700 8 200000 $k $m)
    f=$(echo "$line" | sed 's/.*found=\([0-9]*\).*/\1/')
    d=$(echo "$line" | sed 's/.*procs_done=\([0-9]*\).*/\1/')
    if [ "$d" != "8" ]; then echo "$m k=$k TIMEOUT" >> res/kmin.log; break; fi
    if [ "$f" != "0" ]; then echo "$m kmin=$k found=$f" >> res/kmin.log; break; fi
  done
done
echo ALLDONE >> res/kmin.log
