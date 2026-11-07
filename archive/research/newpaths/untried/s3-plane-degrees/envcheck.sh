#!/bin/bash
# environment check: GPU, nvcc
nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
/usr/bin/nvcc --version | tail -2
nproc
