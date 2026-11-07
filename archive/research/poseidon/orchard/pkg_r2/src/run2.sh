#!/bin/bash
cd "$(dirname "$0")"
./build.sh test_hgcd.c hgcd.c || exit 1
./test_hgcd
