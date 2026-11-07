#!/bin/bash
cd "$(dirname "$0")"
echo "toy3 (separable post-join check: expect sepPost=1, max join 1):"; echo "x u" | PLAIN=1 ../split2 toy3.txt
echo "toy4 (xor check on a modular-sum word: expect sepPost=0, postFilters=1, max join 0):"; echo "x u" | PLAIN=1 ../split2 toy4.txt
