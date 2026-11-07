#!/bin/sh
# Check the GPU toolchain (one short process).
cd "$(dirname "$0")"
nvidia-smi --query-gpu=name,utilization.gpu,memory.used --format=csv
nvcc --version | tail -2
gcc --version | head -1
python3 --version
