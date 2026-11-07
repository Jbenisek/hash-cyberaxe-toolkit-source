#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o vmaxcl vmaxcl.c && timeout 600 ./vmaxcl vsys_fixed.txt > vmaxcl.out 2>&1
cat vmaxcl.out
