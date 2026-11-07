#!/bin/bash
gcc --version | head -1; nproc; grep -m1 "model name" /proc/cpuinfo; grep -o -m1 -w avx2 /proc/cpuinfo; free -g | head -2
