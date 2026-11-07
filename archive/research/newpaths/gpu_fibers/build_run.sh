#!/bin/bash
cd "$(dirname "$0")"
nvcc -O3 -arch=sm_86 -o fibers_w4 fibers_w4.cu 2>&1 | grep -v -i warning | head -5
nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader
