#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
bash test/run_bench.sh base d > test/out/chain_base_d.log 2>&1 &
bash test/run_bench.sh new c 1 > test/out/chain_new_c.log 2>&1
bash test/run_bench.sh base c 1 > test/out/chain_base_c.log 2>&1
wait
