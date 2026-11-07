#!/bin/bash
# positive control: my exhaustive search restricted to the one first-pair (80,72) must find the known set 0 21 23 32 34 60 72 80
cd "$(dirname "$0")"
timeout 110 ./vs my_fixed.txt full 8 1691 100000 > pc8.out
grep -c "FULL k=8" pc8.out
grep "FULL k=8: 80 72 60 34 32 23 21 0" pc8.out || echo "KNOWN SET NOT FOUND"
tail -1 pc8.out
