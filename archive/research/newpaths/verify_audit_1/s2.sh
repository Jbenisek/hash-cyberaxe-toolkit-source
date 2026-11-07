#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o split2 split2.c || exit 1
./split2 sys_fixed_plain.txt costtest
