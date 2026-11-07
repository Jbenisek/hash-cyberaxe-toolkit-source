#!/bin/sh
# K3 over structured dx6 (signed digits on one residue class mod 4), every distinct dS3 looked up in -S2.
# Args: flags mindigits maxdigits classmask tag stride   (one process; own binary copy)
cd "$(dirname "$0")"
cp kpipe kpipe_st
start=$(date +%s)
./kpipe_st k3struct "$1" 5be0cd19 s2_iv.bin "$2" "$3" "k3struct_$5.txt" "$4" "$6" > "k3struct_$5.out" 2>&1
echo "exit=$? wall=$(( $(date +%s) - start ))s" >> "k3struct_$5.out"
tail -5 "k3struct_$5.out"
