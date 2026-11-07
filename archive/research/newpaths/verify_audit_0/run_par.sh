#!/bin/bash
# usage: run_par.sh <sysfile> <kmax> <mode> <nparts> <timeout_s> <tag>
cd "$(dirname "$0")"
start=$(date +%s)
for ((p=0; p<$4; p++)); do
  timeout "$5" ./flats "$1" "$2" "$3" 200000000 "$p" "$4" > "flats_$6.part$p" 2>&1 &
done
wait
cat flats_$6.part* > "flats_$6.out"; rm -f flats_$6.part*
end=$(date +%s)
echo "$6: sys=$1 kmax=$2 mode=$3 parts=$4 $((end-start)) s; parts finished: $(grep -c RESULT flats_$6.out)/$4; covers: $(grep -c 'RESULT kmin' flats_$6.out)" >> flats_summary.log
