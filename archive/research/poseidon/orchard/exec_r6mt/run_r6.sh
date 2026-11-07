#!/bin/bash
# Poseidon r6 counted run (cloud box /root/hs/mt/run_r6_T<T>), modelled on run_r5.sh. NOT STARTED by anyone: the owner decides.
#   usage: bash /root/hs/mt/run_r6.sh [T]      T = threads incl. main (default 30; the program accepts up to NT_MAX = 96)
# Foreground. Refuses to start twice (start.txt) and refuses if less than 45 GiB of RAM is available (the 36.5 GB arena is touched up to ~35 GB).
T=${1:-30}
D=/root/hs/mt/run_r6_T$T
mkdir -p $D || exit 1; cd $D || exit 1
[ -e start.txt ] && { echo "start.txt exists: already started"; exit 3; }
AV=$(awk '/MemAvailable/ {print int($2/1048576)}' /proc/meminfo)
[ "$AV" -ge 45 ] || { echo "only $AV GiB available, need 45"; exit 4; }
cp /root/hs/mt/final_r6/single . || exit 1
date -u > start.txt
python3 /root/hs/mt/memmeter/memmeter.py --label counted -- bash -c "ulimit -s 64; exec ./single 1 $T > run.tmp 2>&1" > mem.tmp 2> mem.err
rc=$?
date -u > end.txt
exit $rc
