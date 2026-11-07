#!/bin/bash
cd "$(dirname "$0")"
nice -n 10 ./single_cap6 $1 > logs/cap6_$1$2.txt 2>&1
echo "EXIT $?" >> logs/cap6_$1$2.txt
