#!/bin/bash
# env_check.sh: GPU, nvcc and python in WSL (read only)
nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv
nvcc --version | tail -1
python3 --version
python3 -c 'import numpy; print("numpy", numpy.__version__)' 2>&1
ps -eo pid,etime,cmd | grep -E 'ctr_toy|walk|kissat|python3' | grep -v grep | head
date
