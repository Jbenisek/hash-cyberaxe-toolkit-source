#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o freedom3 freedom3.c || exit 1
/usr/bin/time -f "total %es" ./freedom3 < a1_keep16.txt
