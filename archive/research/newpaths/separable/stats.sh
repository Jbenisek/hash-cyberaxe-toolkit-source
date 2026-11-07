#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o split split.c || exit 1
for s in fixed_plain fixed_tables; do
  for k in 1 2 3; do ./split sys_$s.txt stats $k; done
done
