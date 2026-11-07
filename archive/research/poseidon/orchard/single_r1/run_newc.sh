#!/bin/bash
cd "$(dirname "$0")"
nice -n 10 ./single_c $1 > logs/newc_$1$2.txt 2>&1
echo "EXIT $?" >> logs/newc_$1$2.txt
