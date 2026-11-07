#!/bin/bash
set -e
cd "$(dirname "$0")"
gcc -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=undefined -Wall -Wextra -o test_pallas_san test_pallas.c pallas.c
timeout 600 ./test_pallas_san . | grep -v "^speed"
