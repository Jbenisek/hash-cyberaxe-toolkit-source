#!/bin/sh
# run_range.sh <init> <eLo> <eHi> <out.bin> [Tdump]  -- one search process, timed.
cd "$(dirname "$0")"
start=$(date +%s)
./trunc_search "$@"
rc=$?
end=$(date +%s)
echo "rc=$rc wall=$((end - start))s args=$*"
