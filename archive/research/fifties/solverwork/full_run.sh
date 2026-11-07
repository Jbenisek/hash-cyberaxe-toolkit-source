#!/bin/bash
# full_run.sh (fifties/solverwork): every listed step of both walks (2^29 proposals per stream, 8 streams), 20 workers.
cd "$(dirname "$0")"
python3 -B solver_measure.py run P 1000000 20 > full_run_P.log 2>&1
python3 -B solver_measure.py run R 1000000 20 > full_run_R.log 2>&1
echo done
