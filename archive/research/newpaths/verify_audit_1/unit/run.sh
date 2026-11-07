#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o ../split2 ../split2.c || exit 1
echo "toy2 (expect 1 join condition, cost 64):"; echo "x y u v" | PLAIN=1 ../split2 toy2.txt
echo "toy1:"; echo "x y u v" | PLAIN=1 ../split2 toy1.txt
