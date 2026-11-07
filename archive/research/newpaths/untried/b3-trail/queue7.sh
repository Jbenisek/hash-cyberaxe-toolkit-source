#!/bin/bash
# queue7.sh: case-Z lower bounds for the counter routes (one kissat at a time, each < 10 min).
#   w_r1 >= SubA + pairBD (pairBD >= 21 proved; G5/G7 keep rows b,d and no message difference
#   in all three routes), SubA = min of w(r1c0)+w(r1c2)+w(r1d0)+w(r1d2) under words 0,2,5,7.
cd "$(dirname "$0")"
rm -f runs/*.cnf
# counter + flags, every legal even t < 2^32 (chunk vs parent), counter absorbed by dm0, dm1
bash lbsearch.sh b3trail.py zSubA_CF 150 "45 40" --rounds 2 --ctr-free lo --ctr-even --dv15 7 --msg 0,1,6,7 --s1 zero --pairs 46 --count r1c0,r1c2,r1d0,r1d2
# counter only (generic cell), every nonzero t < 2^32
bash lbsearch.sh b3trail.py zSubA_C 150 "45 40" --rounds 2 --ctr-free lo --msg 0,1 --s1 zero --pairs 46 --count r1c0,r1c2,r1d0,r1d2
# CF, t = 2^31: last step for the hand column trail (round 0: 6 + 0; columns: G0 2, G2 10)
bash bisect.sh diag_match.py diagCF31 100 300 --u 00000001,00000000,80000011,00000000,00020000,00000000,20230202,00000000,01000000,00000000,11810100,00000000,01000000,00000000,11800100,00000000 --dm 80000000,80000000,0,0,0,0,1,1,0,0,0,0,0,0,0,0
echo "queue7 done"
