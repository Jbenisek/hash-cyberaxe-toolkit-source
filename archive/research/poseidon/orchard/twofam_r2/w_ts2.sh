#!/bin/bash
cd "$(dirname "$0")"
nice -n 10 ./test_split > logs/test_split.txt 2>&1; tail -n 1 logs/test_split.txt
