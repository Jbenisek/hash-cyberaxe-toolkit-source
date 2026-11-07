#!/bin/bash
o="temporary-run-output"
for i in $(seq 1 130); do
  if grep -q ALLDONE "$o" 2>/dev/null; then break; fi
  sleep 8
done
echo "=== tables solve results ==="
grep -E "START|DONE k=|ALLDONE" "$o"
