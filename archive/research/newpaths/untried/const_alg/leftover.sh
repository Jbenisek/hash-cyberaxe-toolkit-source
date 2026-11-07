#!/usr/bin/env bash
# leftover.sh: read-only; lists any process whose command line names this folder (none should be left).
date +%H:%M:%S
ps -eo pid=,etimes=,args= | grep -F 'untried/const_alg' | grep -v -E 'grep|leftover.sh' | cut -c1-200
echo "end of list"
