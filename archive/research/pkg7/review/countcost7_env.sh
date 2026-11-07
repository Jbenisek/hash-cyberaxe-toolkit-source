#!/bin/bash
which gcc python3 nproc 2>&1 | head -5
nproc
uptime
for t in ganak sharpSAT d4 approxmc cryptominisat5 kissat cadical; do which $t 2>/dev/null; done
ls ~/hashsmash | head -30
