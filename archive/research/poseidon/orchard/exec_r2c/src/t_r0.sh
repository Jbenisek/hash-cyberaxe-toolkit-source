#!/bin/bash
cd "$(dirname "$0")"
nice -n 19 timeout 58 ./exec_attack 0 3 1 0 1
