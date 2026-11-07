#!/bin/bash
# queue1.sh: strictly sequential jobs (one kissat at a time; each bisection capped at 540 s).
cd "$(dirname "$0")"
rm -f runs/*.cnf
# 0. flags, last step only, for the cheapest column trail (dm6 = dm7 = 1, columns by hand)
bash bisect.sh diag_match.py diagF11 120 540 --u 00000001,00000000,00000011,00000000,00020000,00000000,20220202,00000000,01000000,00000000,11010100,00000000,01000000,00000000,11000100,00000000 --dm 0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0
# 1. generic counter t = 2^31 (counter only), last step for the hand column trail
#    (round 0 absorbed for free by dm0 = dm1 = 2^31; round-1 G2 with y = 2^31 costs 1)
bash bisect.sh diag_match.py diagC31 120 540 --u 00000000,00000000,80000000,00000000,00000000,00000000,00010000,00000000,00000000,00000000,00800000,00000000,00000000,00000000,00800000,00000000 --dm 80000000,80000000,0,0,0,0,0,0,0,0,0,0,0,0,0,0
echo "queue1 done"
