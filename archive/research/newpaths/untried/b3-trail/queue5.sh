#!/bin/bash
# queue5.sh: tighten the case-Z bound for the flag route (one kissat at a time, each < 10 min).
cd "$(dirname "$0")"
rm -f runs/*.cnf
# exact minimum of the two round-1 column calls (round 0 forced to absorb, no output condition)
bash bisect.sh b3trail.py zCOLS 60 240 --rounds 2 --dv15 7 --msg 6,7 --s1 zero --pairs none --count r1c0,r1c2
# pair bounds with the WLOG symmetry cut w(P) <= W/2
bash lbsearch.sh pair_free.py pairACh 150 "31 29 27" --msg zero --rows ac --half
bash lbsearch.sh pair_free.py pairBDh 150 "31 29 27 25" --msg zero --rows bd --half
echo "queue5 done"
