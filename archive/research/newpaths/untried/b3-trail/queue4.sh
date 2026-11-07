#!/bin/bash
# queue4.sh: strictly sequential (one kissat at a time; each run under 10 minutes).
cd "$(dirname "$0")"
rm -f runs/*.cnf
# Lower bounds for one matched last-step pair with case-Z rows (UNSAT at W => price >= W+1).
bash lbsearch.sh pair_free.py pairAC 120 "30 25 20" --msg zero --rows ac
bash lbsearch.sh pair_free.py pairBD 120 "30 25 20" --msg zero --rows bd
# counter+flag route: G4 also receives dm1 as x
bash lbsearch.sh pair_free.py pairACx 120 "25 20" --msg Px --rows ac
# Best found (upper bounds), case Z, columns free, both output pairs:
bash bisect.sh b3trail.py zCF31 100 300 --rounds 2 --dv12 0x80000000 --dv15 7 --msg 0,1,6,7 --s1 zero
bash bisect.sh b3trail.py zCfree 100 300 --rounds 2 --ctr-free lo --msg 0,1 --s1 zero
bash bisect.sh b3trail.py zF 100 240 --rounds 2 --dv15 7 --msg 6,7 --s1 zero
# Case NZ, flags only: any characteristic of weight <= 62? (solver tuned for SAT)
bash run2.sh r2_flagNZ_W62 62 360 sat --rounds 2 --dv15 7 --s1 nonzero
python3 -B make_hand_dec.py > runs/hand_checks.txt 2>&1
echo "queue4 done"
