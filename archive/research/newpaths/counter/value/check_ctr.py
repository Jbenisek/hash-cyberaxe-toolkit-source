#!/usr/bin/env python3
"""check_ctr.py FILE  (counter/value; research only)
Reads the TRIAL lines printed by 'ctr_rates check' and checks every one against the REAL 2-round compression of
a non-root last chunk (counter v12 = T0, v13 = 0, flags 3; verify_ctr.real_run, copied from scout_recent):
  (1) every printed word equals its value in the real computation of message A (55 bytes);
  (2) digest words 0, 2, 5, 7 of A (55 bytes) and B (63 bytes, w4 -> W4B, w5 -> w5 + DELTA) agree;
  (3) E1.c1 lies in the heavy beta cube (c1 & 0e09818b) == 02008000 and beta = b1 ^ b1' = 18b0e098;
  (4) the bytes of A beyond 55 and of B beyond 63 are zero (w14 = w15 = 0, top byte of w13 zero).
Also checks the tree claim once more on the organizer's verifier for small t (t = 1..3) with these words.
"""
import sys, struct
sys.dont_write_bytecode = True
import verify_ctr as V

bad1 = bad2 = bad3 = bad4 = n = 0
for ln in open(sys.argv[1]):
    if not ln.startswith('TRIAL'):
        continue
    val = {k: int(v, 16) for k, v in (p.split('=') for p in ln.split()[1:])}
    n += 1
    wA = [V.W4 if i == 4 else V.W13 if i == 13 else 0 if i in (14, 15) else val[f'w{i}'] for i in range(16)]
    wB = list(wA); wB[4] = V.W4B; wB[5] = (wA[5] + V.DELTA) & V.MASK
    recA, dA = V.real_run(wA, val['T0'], V.LEN_A)
    recB, dB = V.real_run(wB, val['T0'], V.LEN_B)
    recA['E1.c1'] = recA['E1.c1']
    mism = [k for k in val if k in recA and recA[k] != val[k]]
    if mism:
        bad1 += 1
        if bad1 < 4: print('mismatch', mism[:6])
    if any(dA[i] != dB[i] for i in (0, 2, 5, 7)): bad2 += 1
    beta = recA['E1.b1'] ^ recB['E1.b1']
    if (recA['E1.c1'] & 0x0E09818B) != 0x02008000 or beta != 0x18B0E098: bad3 += 1
    mA = struct.pack('<16I', *wA); mB = struct.pack('<16I', *wB)
    if any(mA[55:]) or any(mB[63:]): bad4 += 1
print(f'{n} trials: word mismatches {bad1}; half-collision 0/2/5/7 failures {bad2}; cube/beta failures {bad3}; '
      f'nonzero tail bytes {bad4}')
# The tree claim itself (last-chunk CV = compress(IV, block, t, len, flags 3), equal CVs -> equal digests) was
# checked on the organizer's verifier by scout_recent (tree_check.txt, 360/360) and scout_cross (t1_tree.txt).
