#!/bin/bash
cd "$(dirname "$0")"
for a in "3000 3 1" "2001 0 1" "777 40 1" "5000 7 1" "1200 1 1"; do ( ulimit -s 64; nice -n 19 ./test_hgcd_p $a | grep -E "HGCD|hgcd:" ); done
