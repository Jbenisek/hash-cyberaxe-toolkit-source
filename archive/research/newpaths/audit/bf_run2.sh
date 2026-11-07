#!/bin/bash
# usage: bf_run2.sh <variant> <set> <kmax> <nproc> <timeout_s> [look]   (bf2 = bf.c with the lookahead option)
cd "$(dirname "$0")"
v=$1; s=$2; k=$3; np=$4; to=$5; mode=${6:-none}
out="bf_${v}_${s}_${mode}_k${k}"
start=$(date +%s)
for ((p=0; p<np; p++)); do
  timeout "$to" ./bf2 "rules_${v}_len64_${s}.txt" "$k" "$p" "$np" "$mode" > "${out}.part$p" 2>&1 &
done
wait
cat ${out}.part* > "${out}.out"; rm -f ${out}.part*
end=$(date +%s)
echo "$v $s mode=$mode kmax=$k nproc=$np: $((end-start)) s; parts done: $(grep -c DONE ${out}.out)/$np; covering sets found: $(grep -c FOUND ${out}.out)" >> bf_summary.log
