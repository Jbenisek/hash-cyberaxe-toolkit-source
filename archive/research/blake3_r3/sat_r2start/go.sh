#!/bin/bash
# S043: 6 single-thread kissat runs (nice 10, 11 h cap each). Writes runs/*.out. Ends when all finish.
cd "$(dirname "$0")"; mkdir -p runs; chmod +x kissat
run(){ o=$1; f=$2; shift 2; nice -n 10 timeout 39900 ./kissat --time=39600 "$@" $f > runs/$o.out 2> runs/$o.err; echo EXIT:$? >> runs/$o.out; }
run w16a w16.cnf &
run w16b w16.cnf --sat --seed=1 &
run w32a w32.cnf &
run w32b w32.cnf --sat --seed=1 &
run w48a w48.cnf &
run w48b w48.cnf --sat --seed=1 &
wait; echo ALLDONE > runs/FINISH.txt; grep -H "^s " runs/*.out >> runs/FINISH.txt
