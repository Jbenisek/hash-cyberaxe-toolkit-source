#!/bin/bash
cd "$(dirname "$0")"
rm -f single
./build.sh single 2>&1 | head -40
size single > logs/size.txt
cat logs/size.txt
