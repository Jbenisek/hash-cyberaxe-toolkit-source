#!/bin/bash
# usage: run_new.sh seed tag -> logs/new_<seed><tag>.txt
cd "$(dirname "$0")"
mkdir -p logs
nice -n 10 ./single $1 > logs/new_$1$2.txt 2>&1
echo "EXIT $?" >> logs/new_$1$2.txt
