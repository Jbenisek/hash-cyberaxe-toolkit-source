#!/bin/bash
cd "$(dirname "$0")"
timeout 110 ./split models/fixed_02_64_t0.mdl res/fixed_02_64_t0_k8.out 4 64 > res/split_fixed_02_64_t0_k8.txt
tail -3 res/split_fixed_02_64_t0_k8.txt
