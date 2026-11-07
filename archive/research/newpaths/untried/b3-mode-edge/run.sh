#!/bin/sh
# Run one kpipe job: run.sh <outfile> <kpipe args...>   (stdout goes to <outfile>, also echoed)
cd "$(dirname "$0")"
out="$1"; shift
start=$(date +%s)
./kpipe "$@" > "$out" 2>&1
rc=$?
end=$(date +%s)
echo "exit=$rc wall=$((end - start))s" >> "$out"
cat "$out"
