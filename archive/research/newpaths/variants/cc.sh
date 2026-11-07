#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o ls_all ls_all.c 2>&1 | grep -E "error" | head -5
