#!/bin/bash
cd "$(dirname "$0")"
./build.sh test_keep 2>&1 | head
nice -n 10 ./test_keep 39062 > logs/test_keep.txt 2>&1
nice -n 10 ./test_keep 19531 >> logs/test_keep.txt 2>&1
bash run_stack.sh
