#!/bin/bash
# usage: run.sh <tag> <kmax> <nproc> <mode> <order> <rules|-> <timeout_s>
cd "$(dirname "$0")"
tag=$1; k=$2; np=$3; mode=$4; ord=$5; rules=$6; to=$7
out="lk_${tag}_${mode}_${ord}_k${k}"
start=$(date +%s)
for ((p=0; p<np; p++)); do
  timeout "$to" ./lk sys_fixed_plain.txt "$k" "$p" "$np" "$mode" "$ord" "$rules" > "${out}.part$p" 2>&1 &
done
wait
cat ${out}.part* > "${out}.out"; rm -f ${out}.part*
end=$(date +%s)
echo "$tag mode=$mode order=$ord kmax=$k nproc=$np rules=$rules: $((end-start)) s; parts done: $(grep -c DONE ${out}.out)/$np; covers found: $(grep -c FOUND ${out}.out)" >> lk_summary.log
