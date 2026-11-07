#!/bin/bash
cd "$(dirname "$0")"
nice -n 10 ./certrun 2 $1 > logs/cert_r2_$1.txt 2>&1
echo "EXIT $?" >> logs/cert_r2_$1.txt
