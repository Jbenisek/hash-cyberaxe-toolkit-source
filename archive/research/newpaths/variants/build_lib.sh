#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -shared -fPIC -o libgd.so libgd.c && echo lib-ok
