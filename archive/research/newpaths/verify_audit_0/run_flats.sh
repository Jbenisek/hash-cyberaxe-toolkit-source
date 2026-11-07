#!/bin/bash
# usage: run_flats.sh <sysfile> <kmax> <mode> <timeout_s> <tag>
cd "$(dirname "$0")"
start=$(date +%s)
timeout "$4" ./flats "$1" "$2" "$3" > "flats_$5.out" 2>&1
rc=$?
end=$(date +%s)
echo "$5: sys=$1 kmax=$2 mode=$3 rc=$rc $((end-start)) s; $(grep RESULT flats_$5.out)" >> flats_summary.log
