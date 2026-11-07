#!/bin/bash
# stops this folder's bf runs only: matched by this folder's rule-file names (rules_plusA_len64.txt,
# rules_fixedAcv2_len64.txt), which no other folder uses
for p in $(pgrep -f 'fringe/bfrun.sh'); do kill "$p"; done
for p in $(pgrep -f 'bf rules_(plusA|fixedAcv2)_len64\.txt'); do kill "$p"; done
sleep 1
ps -eo pid,args | grep -E 'bf rules_(plusA|fixedAcv2)_len64' | grep -v grep
echo done
