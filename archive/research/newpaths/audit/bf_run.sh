#!/bin/bash
# usage: bf_run.sh <variant> <set> <kmax> <nproc> <timeout_s>   -> bf_<variant>_<set>_k<kmax>.out (all parts concatenated)
cd "$(dirname "$0")"
v=$1; s=$2; k=$3; np=$4; to=$5
out="bf_${v}_${s}_k${k}"
start=$(date +%s)
for ((p=0; p<np; p++)); do
  timeout "$to" ./bf "rules_${v}_len64_${s}.txt" "$k" "$p" "$np" > "${out}.part$p" 2>&1 &
done
wait
cat ${out}.part* > "${out}.out"; rm -f ${out}.part*
end=$(date +%s)
echo "$v $s kmax=$k nproc=$np: $((end-start)) s; parts done: $(grep -c DONE ${out}.out)/$np; covering sets found: $(grep -c FOUND ${out}.out)" >> bf_summary.log
