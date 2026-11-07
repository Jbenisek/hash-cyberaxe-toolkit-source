#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o flats2 flats2.c 2>&1
echo built $?