#!/bin/bash
# stops only this folder's SAT runner and its kissat children (matched by the relative cnf/ path this folder uses)
for p in $(pgrep -f 'fringe/satrun.sh'); do kill "$p"; done
sleep 1
for p in $(pgrep -f 'kissat -q cnf/'); do kill "$p"; done
sleep 1
ps -eo pid,args | grep -E 'kissat -q cnf/|satrun' | grep -v grep
echo done
