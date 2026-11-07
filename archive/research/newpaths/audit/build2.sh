#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o bf3 bf.c 2>&1
echo built $?
