#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o flats flats.c 2>&1
echo built $?
