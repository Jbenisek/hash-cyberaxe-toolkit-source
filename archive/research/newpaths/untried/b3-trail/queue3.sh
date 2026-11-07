#!/bin/bash
# queue3.sh: lower bounds (one kissat at a time; each bisection capped at 540 s).
cd "$(dirname "$0")"
rm -f runs/*.cnf
# Price of ONE nonzero matched last-step pair with the input rows the flag route allows in
# case Z (G4/G6 get rows a,c only; G5/G7 rows b,d only; no message difference in their words).
# (With all four rows free the pair costs <= 10: hand construction in RESULT.md.)
bash bisect.sh pair_free.py pairAC 120 300 --msg zero --rows ac
bash bisect.sh pair_free.py pairBD 120 300 --msg zero --rows bd
# Decomposition for the flag route, case Z: each pair alone, columns and round 0 free.
bash bisect.sh b3trail.py zP46 120 540 --rounds 2 --dv15 7 --msg 6,7 --s1 zero --pairs 46 --count r1d0,r1d2
bash bisect.sh b3trail.py zP57 120 540 --rounds 2 --dv15 7 --msg 6,7 --s1 zero --pairs 57 --count r1d1,r1d3
echo "queue3 done"
