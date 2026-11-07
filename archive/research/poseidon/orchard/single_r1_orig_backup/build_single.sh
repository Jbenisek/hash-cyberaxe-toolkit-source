#!/bin/bash
cd "$(dirname "$0")"
./build.sh single 2>&1 | head -40
ls -la single
