#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o fullsets fullsets.c || exit 1
time ./fullsets sys_fixed_plain.txt 5 0 1 | tail -3
time ./fullsets sys_fixed_tables.txt 5 0 1 | tail -3
