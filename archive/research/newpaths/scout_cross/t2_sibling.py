"""TEST 1b + TEST 2 on toy 2-round BLAKE3 (xtoy.Toy).
Length-sibling pairs (fringe angle 3): base message M with block length b1, partner M' with length
b2 = b1 ^ 8 and m4, m5 adjusted so that K2's output - hence the whole round-0 state X - is identical.
The pair then differs only in m4 (round-1 C3 x input) and m5 (round-1 E1 y input).
Per instance (cv, counter, flags) we count:
  ZA   : dY7 = dY15 = 0  (E0/E2 inputs equal: the 'zero channel' of the A half; the filed path pins this)
  A    : out0,2,5,7 equal;      Afold = A and not ZA   (A half equal through XOR-fold cancellation)
  ZB   : E1 and E3 outputs equal (B 'zero channel');   B : out1,3,4,6 equal;  Bfold = B and not ZB
  full : all 8 output words equal (a real toy collision of the 2-round compression)
TEST 1b question: do these rates depend on the instance constants (chunk counter, flags, chaining value)?
TEST 2 question: how much of A and B comes through the XOR-fold channel (Rumba-style cancellation)?
Usage: python t2_sibling.py w log2N [seed]
"""
import sys, time
import numpy as np
from xtoy import Toy


def instances(w, rng):
    m = (1 << w) - 1
    out = [("filed: IV t=0 flags=11", None, 0, 11),
           ("chunk t=1 flags=3", None, 1, 3)]
    for i in range(3):
        out.append((f"chunk t=rand{i} flags=3", None, int(rng.integers(2, 1 << (2 * w))), 3))
    for i in range(3):
        cv = [int(x) for x in rng.integers(0, m + 1, 8)]
        out.append((f"2-block cv=rand{i} t=rand flags=2", cv, int(rng.integers(1, 1 << (2 * w))), 2))
    return out


def run(w, log2n, seed=11, batch_log=18, alt=False):
    T = Toy(w, alt=alt)
    mask = T.mask
    rng = np.random.default_rng(seed)
    b1 = 55 & int(mask)
    b2 = b1 ^ 8
    res = []
    for name, cv, t, flags in instances(w, rng):
        cnt = dict(N=0, ZA=0, A=0, Afold=0, ZB=0, B=0, Bfold=0, full=0, full_ZA=0, Xbad=0,
                   dY3z=0, dY11z=0, dY7z=0, dY15z=0)
        t0 = time.time()
        nb = 1 << max(0, log2n - batch_log)
        n = 1 << min(log2n, batch_log)
        for _ in range(nb):
            M = [rng.integers(0, int(mask) + 1, n, dtype=np.uint64) for _ in range(16)]
            v1 = T.init_state(n, cv=cv, counter=t, blen=b1, flags=flags)
            v2 = T.init_state(n, cv=cv, counter=t, blen=b2, flags=flags)
            cv2, cv6 = v1[2], v1[6]
            a1 = (cv2 + cv6 + M[4]) & mask
            a1p = a1 ^ np.uint64(b1 ^ b2)
            Mp = list(M)
            Mp[4] = (a1p - cv2 - cv6) & mask
            Mp[5] = (M[5] + a1 - a1p) & mask
            f1, X1, Y1 = T.rounds(M, v1, keep=True)
            f2, X2, Y2 = T.rounds(Mp, v2, keep=True)
            xb = np.zeros(n, dtype=bool)
            for i in range(16):
                xb |= (X1[i] != X2[i])
            o1, o2 = Toy.out(f1), Toy.out(f2)
            eq = [o1[i] == o2[i] for i in range(8)]
            A = eq[0] & eq[2] & eq[5] & eq[7]
            B = eq[1] & eq[3] & eq[4] & eq[6]
            ZA = (Y1[7] == Y2[7]) & (Y1[15] == Y2[15])
            ZB = np.ones(n, dtype=bool)
            for i in (1, 6, 11, 12, 3, 4, 9, 14):
                ZB &= (f1[i] == f2[i])
            cnt['N'] += n
            cnt['Xbad'] += int(xb.sum())
            cnt['ZA'] += int(ZA.sum()); cnt['A'] += int(A.sum()); cnt['Afold'] += int((A & ~ZA).sum())
            cnt['ZB'] += int(ZB.sum()); cnt['B'] += int(B.sum()); cnt['Bfold'] += int((B & ~ZB).sum())
            cnt['full'] += int((A & B).sum()); cnt['full_ZA'] += int((A & B & ZA).sum())
            for k, i in (('dY3z', 3), ('dY11z', 11), ('dY7z', 7), ('dY15z', 15)):
                cnt[k] += int((Y1[i] == Y2[i]).sum())
        cnt['sec'] = round(time.time() - t0, 1)
        res.append((name, t, flags, cnt))
        lg = lambda k: (f"{np.log2(cnt[k] / cnt['N']):.2f}" if cnt[k] else "-inf")
        print(f"w={w} {name:34s} N=2^{log2n} Xbad={cnt['Xbad']} | log2 p: ZA {lg('ZA')} A {lg('A')} "
              f"Afold {lg('Afold')} [{cnt['Afold']}] | ZB {lg('ZB')} B {lg('B')} Bfold {lg('Bfold')} [{cnt['Bfold']}] | "
              f"full {lg('full')} [{cnt['full']}] fullZA [{cnt['full_ZA']}] | dY3=0 {lg('dY3z')} dY11=0 {lg('dY11z')} "
              f"dY7=0 {lg('dY7z')} dY15=0 {lg('dY15z')} | {cnt['sec']}s", flush=True)
    return res


if __name__ == "__main__":
    w = int(sys.argv[1]); log2n = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 11
    alt = len(sys.argv) > 4 and sys.argv[4] == "alt"
    print(f"# toy w={w} rots={Toy(w, alt=alt).rots} random baselines: one word 2^-{w}, half (4 words) 2^-{4*w}, "
          f"digest 2^-{8*w}", flush=True)
    run(w, log2n, seed, alt=alt)
