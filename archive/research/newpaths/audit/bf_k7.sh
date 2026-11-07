#!/bin/bash
cd "$(dirname "$0")"
./bf_run.sh fixed plain 7 2 3000 &
./bf_run.sh fixed orig 7 2 3000 &
./bf_run.sh fixed pair 7 2 3000 &
wait
