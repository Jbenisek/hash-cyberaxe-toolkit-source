#!/bin/sh
# Build the GPU stage scanners (one process).
set -e
cd "$(dirname "$0")"
nvcc -O3 -arch=sm_86 -std=c++17 -o kpipe kpipe.cu 2>&1 | grep -v "Wno-deprecated" || true
ls -la kpipe
