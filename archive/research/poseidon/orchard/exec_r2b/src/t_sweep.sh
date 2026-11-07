#!/bin/bash
cd "$(dirname "$0")"
for cfg in "96 50" "96 45" "96 55" "192 50"; do set -- $cfg; echo -n "bk=$1 pct=$2  "; ( ulimit -s 64; nice -n 19 ./test_hgcd_p 195312 1 0 $2 $1 0 17 | grep -E "^hgcd" | cut -c1-100 ); done
