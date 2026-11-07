#!/bin/bash
cd "$(dirname "$0")"
mkdir -p logs
./build.sh test_hgcd 2>&1 | head -30
./build.sh test_split 2>&1 | head -30
./build.sh test_keep 2>&1 | head -30
nice -n 10 ./test_keep 39062 > logs/test_keep.txt 2>&1
{
for args in "300 3 299" "1000 5 999" "1000 5 10" "1000 5 500" "1000 5 6" "3000 7 2999" "3000 0 100" "3000 10 600" "3000 0 2999" "5000 20 4999" "5000 20 3000" "20000 9 19999 0"; do nice -n 10 ./test_hgcd $args; done
} > logs/test_hgcd.txt 2>&1
nice -n 10 ./test_split 7 > logs/test_split.txt 2>&1
echo "EXIT $?" >> logs/test_split.txt
