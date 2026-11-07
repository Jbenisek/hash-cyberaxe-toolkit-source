#!/bin/bash
# usage: ls_run.sh tag iters restarts printmax sys... ; one lsearch process per system (max 8)
cd "$(dirname "$0")"
tag=$1; it=$2; re=$3; pm=$4; shift 4
seed=1
for s in "$@"; do
  timeout 3000 ./lsearch sys_$s.txt $seed $it $re $pm > ls_${tag}_$s.out &
  seed=$((seed+1))
done
wait
echo "ls $tag done $(date)" >> ls_run.log
