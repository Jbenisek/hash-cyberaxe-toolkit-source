#!/bin/bash
cd "$(dirname "$0")"
timeout 115 python3 ihs2.py models/fixed_02_64_t0.mdl 5 9 105 t02
tail -4 res/ihs_t02.log
