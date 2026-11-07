#!/bin/bash
cd "$(dirname "$0")"
timeout 1300 python3 ihs2.py models/outhalf_02_64_t0.mdl 12 16 1200 outhalf02 20
tail -4 res/ihs_outhalf02.log
