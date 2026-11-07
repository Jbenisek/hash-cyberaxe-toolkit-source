#!/bin/bash
# usage: bfrun.sh <variant> <kmax> <nproc> <timeout_s>  -> bf_<variant>_k<kmax>.out ; summary line in bf_summary.log
cd "$(dirname "$0")"
v=$1; k=$2; np=$3; to=$4
out="bf_${v}_k${k}"
start=$(date +%s)
for ((p=0; p<np; p++)); do
  timeout "$to" ./bf "rules_${v}_len64.txt" "$k" "$p" "$np" > "${out}.part$p" 2>&1 &
done
wait
cat ${out}.part* > "${out}.out"; rm -f ${out}.part*
end=$(date +%s)
echo "$v kmax=$k nproc=$np: $((end-start)) s; parts done: $(grep -c DONE ${out}.out)/$np; covering sets found: $(grep -c FOUND ${out}.out)" >> bf_summary.log
