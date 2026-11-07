#!/bin/bash
# probe_tools.sh - instruction counters, compilers and solver libraries available in WSL (read-only probe)
for b in valgrind perf gcc g++ cc make; do printf '%s: ' "$b"; command -v "$b" || echo none; done
ls /usr/include 2>/dev/null | grep -iE 'kissat|cadical|ccadical|crypto' ; echo "-- libs:"
ls /usr/lib/x86_64-linux-gnu 2>/dev/null | grep -iE 'kissat|cadical|cryptominisat' ; echo "-- cpu:"
grep -m1 'model name' /proc/cpuinfo; grep -m1 'cpu MHz' /proc/cpuinfo
kissat --help 2>&1 | grep -iE 'check|congruence|sweep|probe |substitute|eliminate=|preprocess|simplify=|backbone=' | head -n 20
