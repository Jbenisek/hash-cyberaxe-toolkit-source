#!/bin/bash
# usage: jt_run.sh prog sys maxC file...   one process per file (caller keeps <= 8 total)
cd "$(dirname "$0")"
prog=$1; sys=$2; mc=$3; shift 3
for f in "$@"; do
  if [ "$prog" = jtree ]; then timeout 5400 ./jtree sys_$sys.txt $f $mc 0 > jt_${sys}_$f.out &
  else timeout 5400 ./kdiag2 sys_$sys.txt $f > kd2_${sys}_$f.out & fi
done
wait
echo "$prog $sys $* done $(date)" >> jt_run.log
