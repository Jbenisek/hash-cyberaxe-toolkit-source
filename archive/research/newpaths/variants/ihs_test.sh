#!/bin/bash
cd "$(dirname "$0")"
timeout 110 python3 ihs.py models/fixed_02_64_t0.mdl 6 9 100 test02t0
tail -5 res/ihs_test02t0.log
