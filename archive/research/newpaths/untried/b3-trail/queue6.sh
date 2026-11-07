#!/bin/bash
# queue6.sh (replaces the tail of queue4 and queue5; one kissat at a time, each run < 10 min).
# Flag route, case Z: w_r1 = w(cols) + w(G4,G6) + w(G5,G7) >= SubA + pairBD, where
# SubA = min over valid trails meeting digest words 0,2,5,7 of w(r1c0)+w(r1c2)+w(r1d0)+w(r1d2).
cd "$(dirname "$0")"
rm -f runs/*.cnf
# 1. exact minimum of the two round-1 column calls (no output condition)
bash bisect.sh b3trail.py zCOLS 60 200 --rounds 2 --dv15 7 --msg 6,7 --s1 zero --pairs none --count r1c0,r1c2
# 2. SubA lower bound
bash lbsearch.sh b3trail.py zSubA 150 "45 40 35" --rounds 2 --dv15 7 --msg 6,7 --s1 zero --pairs 46 --count r1c0,r1c2,r1d0,r1d2
# 3. pairBD lower bound with the WLOG symmetry cut w(P) <= W/2
bash lbsearch.sh pair_free.py pairBDh 150 "29 27 25" --msg zero --rows bd --half
# 4. best found (upper bounds), case Z, columns free, both output pairs
bash bisect.sh b3trail.py zCF31 100 300 --rounds 2 --dv12 0x80000000 --dv15 7 --msg 0,1,6,7 --s1 zero
bash bisect.sh b3trail.py zCfree 100 300 --rounds 2 --ctr-free lo --msg 0,1 --s1 zero
python3 -B make_hand_dec.py > runs/hand_checks.txt 2>&1
echo "queue6 done"
