#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o lk2 lk2.c 2>&1; echo built lk2 $?
gcc -O3 -march=native -Wno-unused-result -o split split.c 2>&1; echo built split $?
