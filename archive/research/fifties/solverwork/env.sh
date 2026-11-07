#!/bin/bash
# env.sh (fifties/solverwork): report CPU count, python, nvcc and GPU load. Read-only.
nproc
python3 --version
/usr/bin/nvcc --version | tail -1
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv
