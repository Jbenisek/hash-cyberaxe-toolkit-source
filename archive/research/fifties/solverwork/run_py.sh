#!/bin/bash
# run_py.sh (fifties/solverwork): run one python script of this folder with its arguments.
cd "$(dirname "$0")"
python3 -B "$@"
