#!/bin/bash
# queue2.sh: strictly sequential jobs (one process at a time; each capped under 600 s).
cd "$(dirname "$0")"
rm -f runs/*.cnf
# Case Z (zero state difference after round 0), columns free, both output pairs, best-of-three:
#  zCfree: counter difference only, any nonzero t in v12 (the generic counter cell; illegal as a
#          route without a 2^128 tree match, measured for the number only)
bash bisect.sh b3trail.py zCfree 100 300 --rounds 2 --ctr-free lo --msg 0,1 --s1 zero
#  zCF31: legal chunk-vs-parent route, t = 2^31, flags 3 vs 4
bash bisect.sh b3trail.py zCF31 100 300 --rounds 2 --dv12 0x80000000 --dv15 7 --msg 0,1,6,7 --s1 zero
#  zF: legal root route, flags 11 vs 12
bash bisect.sh b3trail.py zF 100 300 --rounds 2 --dv15 7 --msg 6,7 --s1 zero
# Case NZ (state difference after round 0 nonzero), flags only: look for ANY characteristic of
# weight <= 62 with the solver tuned for satisfiable instances.
bash run2.sh r2_flagNZ_W62 62 420 sat --rounds 2 --dv15 7 --s1 nonzero
python3 -B make_hand_dec.py > runs/hand_checks.txt 2>&1
# (verify.py needs numpy: run it with the Windows python after this queue)
echo "queue2 done"
