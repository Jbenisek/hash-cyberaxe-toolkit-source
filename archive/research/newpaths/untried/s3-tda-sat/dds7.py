"""Digest-round structure after the theta6 spread, DDS middle placement (COMPUTED, exact, no search).

For every class, every kernel-keeping mid with w(chi4) <= MAXW4 and every chi4 output b4:
  a5 = L(b4); the 64 plane-0 chi6 rows are affine functions of b5 in S(a5).
  const_bad : some plane-0 row is constant over S(a5) with a value that can never give a digest collision
              -> P(collision | a5) = 0 exactly.
  forced    : number of plane-0 rows whose x=0..3 part cannot be made zero by any b5 (each such row must take a
              nonzero allowed pattern, all of which need x4 = 1 and cost >= 3 conditions).
Also the rank R of the plane-0 map (how many digest-relevant bits b5 can move).
Usage: python dds7.py <first_class> <last_class_exclusive> [max_w4=13]"""
import sys
import math
import time
import kk
import dds2 as D
from dds6 import row_forms, ALLOWED

t0 = time.time()
lo, hi = int(sys.argv[1]), int(sys.argv[2])
MAXW4 = int(sys.argv[3]) if len(sys.argv) > 3 else 13
PI = kk.RHOPI


def rank(vecs):
    piv = {}
    for v in vecs:
        while v:
            p = v.bit_length() - 1
            if p in piv:
                v ^= piv[p]
            else:
                piv[p] = v
                break
    return len(piv)


for n in range(lo, hi):
    S = set(D.classes[n])
    a3 = {PI[i] for i in S}
    mids = [b for b in D.choices(a3) if D.in_kernel(b)]
    tot = bad = 0
    forced_hist = {}
    ranks = []
    for b3 in mids:
        a4 = {PI[i] for i in b3}
        if kk.weight(a4) > MAXW4:
            continue
        for b4 in D.choices(a4):
            tot += 1
            a5 = kk.L_set(b4)
            dim, forms = row_forms(a5)
            cb = False
            forced = 0
            for z, f in forms.items():
                if all(c == 0 for c, k in f):
                    val = sum(k << x for x, (c, k) in enumerate(f))
                    if val not in ALLOWED:
                        cb = True
                # x=0..3 part cannot be zero if some combination is constant 1: check each bit alone (cheap test)
                if any(c == 0 and k for c, k in f[:4]):
                    forced += 1
            if cb:
                bad += 1
            forced_hist[forced] = forced_hist.get(forced, 0) + 1
            if len(ranks) < 50:
                ranks.append(rank([c for f in forms.values() for c, k in f]))
    print(f"class {n}: b4 cases {tot}; P(collision|a5)=0 exactly (constant forbidden plane-0 row) in {bad}; "
          f"rows with a constant-1 bit at x<=3 (histogram) {dict(sorted(forced_hist.items()))}; "
          f"plane-0 rank over S(a5) (first 50 cases) min {min(ranks)} max {max(ranks)}  [{time.time() - t0:.1f}s]",
          flush=True)
