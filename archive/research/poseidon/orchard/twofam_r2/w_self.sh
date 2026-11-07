#!/bin/bash
cd "$(dirname "$0")"
bash build.sh twofam && (time nice -n 10 ./twofam selftest 2>&1 | tail -12)
