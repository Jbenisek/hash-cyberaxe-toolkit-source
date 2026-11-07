#!/bin/bash
cd "$(dirname "$0")"
pkill -f "twofam_dbg 2 401"
bash build.sh test_gcd 2>&1 | grep -i " error"
for d in 100 5000 20000 70000; do nice -n 10 ./test_gcd $d; done
