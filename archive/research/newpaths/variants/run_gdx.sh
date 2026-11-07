#!/bin/bash
# usage: run_gdx.sh <timeout_s> <nprocs> <maxprint> <k> <model>...   (models by name in models/, without .mdl)
cd "$(dirname "$0")"
to=$1; np=$2; mp=$3; k=$4; shift 4
for m in "$@"; do
  out="res/${m}_k${k}.out"; : > "$out"
  start=$(date +%s)
  for ((p=0; p<np; p++)); do
    ( timeout "$to" ./gdx "models/$m.mdl" "$k" "$p" "$np" "$mp" > "res/${m}_k${k}.p$p"; echo "exit=$?" >> "res/${m}_k${k}.p$p" ) &
  done
  wait
  cat res/${m}_k${k}.p* > "$out"; rm -f res/${m}_k${k}.p*
  tot=$(grep -h '^DONE' "$out" | sed 's/.*found=\([0-9]*\).*/\1/' | paste -sd+ | bc)
  nd=$(grep -c '^DONE' "$out")
  echo "$m k=$k procs_done=$nd/$np found=$tot secs=$(( $(date +%s) - start ))" | tee -a res/summary.log
done
