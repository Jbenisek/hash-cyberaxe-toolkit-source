#!/bin/bash
cd "$(dirname "$0")"
for cfg in "48 50" "96 50" "130 50" "190 50" "96 45" "96 55" "96 60" "48 45" "48 55"; do set -- $cfg; echo -n "bk=$1 pct=$2  "; ( ulimit -s 64; nice -n 19 ./test_hgcd_p 39062 1 0 $2 $1 | grep -E "^hgcd" | cut -c1-90 ); done
