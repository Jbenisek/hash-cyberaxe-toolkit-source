#!/bin/bash
cd "$(dirname "$0")"
bash build.sh test_split 2>&1 | grep -i error
nice -n 10 ./test_split 2>&1 | grep -v "taylor\|gcd degree" | tail -40
