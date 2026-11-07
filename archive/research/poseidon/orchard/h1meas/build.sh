#!/bin/bash
# build h1meas (WSL): gcc -O2, our pallas.c
set -e
cd "$(dirname "$0")"
gcc -O2 -march=native -Wall -Wextra -o /root/h1meas/h1meas h1meas.c ../impl/pallas.c
