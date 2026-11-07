#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o bf bf.c 2>&1
echo built $?
