#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o split split.c 2>&1 | grep -v warning | head -5; echo built
