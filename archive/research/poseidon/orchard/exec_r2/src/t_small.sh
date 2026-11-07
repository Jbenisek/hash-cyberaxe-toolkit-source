#!/bin/bash
cd "$(dirname "$0")"
bash build_exec.sh 2>&1 | grep -E "error|warning: unused" | head
nice -n 19 timeout 60 ./test_ntt 2>&1 | tail -8
nice -n 19 timeout 60 ./prof3
