#!/bin/bash
# usage (PowerShell): wsl bash ./research/poseidon/orchard/impl/build_test.sh
set -e
cd "$(dirname "$0")"
gcc -O2 -Wall -Wextra -o test_pallas test_pallas.c pallas.c
timeout 300 ./test_pallas .
