#!/bin/bash
cd "$(dirname "$0")"
bash build.sh test_pow 2>&1 | grep -i " error"
for a in "1000 1234567891011" "100000 1234567891011" "200000 1234567891011"; do nice -n 10 ./test_pow $a; done
