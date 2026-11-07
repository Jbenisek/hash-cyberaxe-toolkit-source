#!/bin/bash
cd "$(dirname "$0")"
nvcc -O3 -arch=sm_86 -std=c++17 -o mp mp.cu ../pallas.o 2> build.log
rc=$?; grep -E "error" build.log | head -20; exit $rc
