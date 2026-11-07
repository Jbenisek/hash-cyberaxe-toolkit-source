#!/bin/sh
# Build the truncated search (WSL gcc). One process; no parallel jobs.
set -e
cd "$(dirname "$0")"
gcc -O3 -march=native -std=gnu11 -Wall -o trunc_search trunc_search.c
echo built
