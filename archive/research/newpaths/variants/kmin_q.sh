#!/bin/bash
# usage: kmin_q.sh <nprocs> <timeout> <kfrom> <kto> <model>...   first k in [kfrom,kto] with a solution
cd "$(dirname "$0")"
np=$1; to=$2; kf=$3; kt=$4; shift 4
for m in "$@"; do
  for ((k=kf; k<=kt; k++)); do
    line=$(./run_gdx.sh $to $np 200000 $k $m)
    f=$(echo "$line" | sed 's/.*found=\([0-9]*\).*/\1/')
    d=$(echo "$line" | sed 's/.*procs_done=\([0-9]*\).*/\1/')
    if [ "$d" != "$np" ]; then n=$(grep -c '^SOL' res/${m}_k${k}.out); echo "$m k=$k INCOMPLETE (sols printed before stop: $n)" >> res/kmin.log; break; fi
    if [ "$f" != "0" ]; then echo "$m kmin=$k found=$f (searched k=$kf..$k)" >> res/kmin.log; break; fi
    if [ $k == $kt ]; then echo "$m none for k=$kf..$kt" >> res/kmin.log; fi
  done
done
