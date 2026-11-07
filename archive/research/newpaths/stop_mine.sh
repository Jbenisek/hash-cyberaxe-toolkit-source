#!/bin/bash
# stop only the main session's three rerun solves, matched by their own CNF file names
for f in gd_fixedT_len64_k5_T100.cnf gd_fixedT_len64_k6_T50.cnf gd_fixed_len64_k6_T50.cnf; do
  pkill -f "kissat -q --time=3600 $f" && echo "stopped $f"
done
