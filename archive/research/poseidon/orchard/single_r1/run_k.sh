#!/bin/bash
cd "$(dirname "$0")"
for k in "$@"; do bash ./build_k.sh $k; nice -n 10 ./test_keep_$k 39062 >> logs/basek.txt 2>&1; echo "K=$k" >> logs/basek.txt; done
echo DONE >> logs/basek.txt
