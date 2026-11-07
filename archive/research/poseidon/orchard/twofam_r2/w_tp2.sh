#!/bin/bash
cd "$(dirname "$0")"
nice -n 10 ./test_pow 390625 1234567891011 > logs/test_pow_390625.txt 2>&1
