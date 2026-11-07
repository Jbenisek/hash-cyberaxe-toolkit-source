#!/usr/bin/env python3
"""real_filter.py [N] [SEED] [CHECK]   (counter_next/stack; research only)

The exact outer-step filter on REAL outer steps of the counter arrangement (not on uniform model words).
outer(): a Python transcription of outer_step() in counter/value/ctr_gen.inc (generated from cone4_E1b1_B10.txt;
basis C0.d1 D2.a1 D2.b1 S11 S4 X9 Y4 w6, Y4 a sub-class member), cross-checked word for word against the team's order
solver verify_ctr.solve_order (copied here) on CHECK random bases, and against the real 2-round compression
(verify_ctr.real_run) for two inner values per outer step: Y9 (= C1 c output) and w8 must not move with the inner word.
Then N random outer steps: share passing the filter for the beta* outcomes (exact model value 2^-9.8132).
"""
import random, sys, re
from math import log2, sqrt
sys.dont_write_bytecode = True
import verify_ctr as V
import e3solve as S
M = 0xFFFFFFFF
rol, ror = V.rol, V.ror
PX3, PX7, PX11, PX15, PW4, PW13 = V.X3, V.X7, V.X11, V.X15, V.W4, V.W13


def outer(C0_d1, D2_a1, D2_b1, S11, S4, X9, Y4, w6):
    X2 = (D2_a1 + D2_b1 + PW13) & M
    X8 = rol(PX7, 7) ^ D2_b1
    C0_c1 = (X8 + C0_d1) & M
    K2_a1 = (0x3c6ef372 + 0x1f83d9ab + PW4) & M
    K2_d1 = ror(0x00000037 ^ K2_a1, 16)
    K2_c1 = (0x3c6ef372 + K2_d1) & M
    K3_a1 = (0xa54ff53a + 0x5be0cd19 + w6) & M
    K2_b1 = ror(0x1f83d9ab ^ K2_c1, 12)
    K3_d1 = ror(0x00000003 ^ K3_a1, 16)
    K3_c1 = (0xa54ff53a + K3_d1) & M
    S15 = (S11 - K3_c1) & M
    S3 = rol(S15, 8) ^ K3_d1
    K3_b1 = ror(0x5be0cd19 ^ K3_c1, 12)
    D3_a1 = (S3 + S4) & M
    S7 = ror(K3_b1 ^ S11, 7)
    D3_b1 = (PX3 - D3_a1) & M
    D2_c1 = rol(D2_b1, 12) ^ S7
    D3_c1 = rol(D3_b1, 12) ^ S4
    X4 = ror(D3_b1 ^ X9, 7)
    X13 = (X8 - D2_c1) & M
    X14 = (X9 - D3_c1) & M
    C0_b1 = ror(X4 ^ C0_c1, 12)
    D2_d1 = rol(X13, 8) ^ X2
    D3_d1 = rol(X14, 8) ^ PX3
    Y8 = rol(Y4, 7) ^ C0_b1
    S13 = rol(D2_d1, 16) ^ D2_a1
    S9 = (D3_c1 - D3_d1) & M
    Y12 = (Y8 - C0_c1) & M
    K1_c1 = (S9 - S13) & M
    Y0 = rol(Y12, 8) ^ C0_d1
    K1_d1 = (K1_c1 - 0xbb67ae85) & M
    C0_a1 = (Y0 - C0_b1 - w6) & M
    K1_a1 = rol(K1_d1, 16)
    w2 = (K1_a1 - 0xbb67ae85 - 0x9b05688c) & M
    X0 = (C0_a1 - X4 - w2) & M
    S14 = rol(D3_d1, 16) ^ D3_a1
    K1_b1 = ror(0x9b05688c ^ K1_c1, 12)
    S10 = (K2_c1 + S14) & M
    D0_d1 = rol(PX15, 8) ^ X0
    S5 = ror(K1_b1 ^ S9, 7)
    D0_c1 = (S10 + D0_d1) & M
    D0_b1 = ror(S5 ^ D0_c1, 12)
    X10 = (D0_c1 + PX15) & M
    X5 = ror(D0_b1 ^ X10, 7)
    S1 = rol(S13, 8) ^ K1_d1
    w3 = (S1 - K1_a1 - K1_b1) & M
    X12 = rol(C0_d1, 16) ^ C0_a1
    D1_c1 = (PX11 - X12) & M
    D1_d1 = (D1_c1 - S11) & M
    S8 = (D2_c1 - D2_d1) & M
    K0_b1 = rol(S4, 7) ^ S8
    S2 = rol(S14, 8) ^ K2_d1
    S6 = ror(K2_b1 ^ S10, 7)
    X1 = rol(X12, 8) ^ D1_d1
    K0_c1 = rol(K0_b1, 12) ^ 0x510e527f
    D1_b1 = ror(S6 ^ D1_c1, 12)
    C1_a1 = (X1 + X5 + w3) & M
    S12 = (S8 - K0_c1) & M
    X6 = ror(D1_b1 ^ PX11, 7)
    C1_d1 = ror(X13 ^ C1_a1, 16)
    D1_a1 = rol(D1_d1, 16) ^ S12
    C1_c1 = (X9 + C1_d1) & M
    w10 = (D1_a1 - S1 - S6) & M
    C1_b1 = ror(X5 ^ C1_c1, 12)
    Y1 = (C1_a1 + C1_b1 + w10) & M
    Y13 = ror(C1_d1 ^ Y1, 8)
    K0_d1 = (K0_c1 - 0x6a09e667) & M
    Y9 = (C1_c1 + Y13) & M
    S0 = rol(S12, 8) ^ K0_d1
    D0_a1 = rol(D0_d1, 16) ^ S15
    w8 = (D0_a1 - S0 - S5) & M
    return Y9, w8


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    chk = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    txt = open('cone4_E1b1_B10.txt').read().splitlines()
    BASIS = re.search(r'basis = ([^|]*)', txt[0]).group(1).split()
    LINES = [(l.split('<-')[0].replace('*', ' ').strip(), l.split('<-')[1].split()) for l in txt[1:]
             if '<-' in l and 'cone of' not in l]
    # cross-checks against the team's solver and the real compression
    bad = 0
    for _ in range(chk):
        y = S.member(rng)
        base = {b: rng.getrandbits(32) for b in BASIS}
        base['Y4'] = y
        it = iter([base[b] for b in BASIS])
        class Stub:
            def randrange(s, n): return next(it)
        orig = V.class_member; V.class_member = lambda k: y
        try:
            v = V.solve_order(LINES, BASIS, Stub())
        finally:
            V.class_member = orig
        q, w8 = outer(*(v[b] for b in ['C0.d1', 'D2.a1', 'D2.b1', 'S11', 'S4', 'X9', 'Y4', 'w6']))
        bad += (q != v['Y9']) + (w8 != v['w8'])
        # real compression of message A for this trial: Y9 from the real run must equal the order's Y9
        words = [v['w%d' % i] for i in range(16)]
        rec, _ = V.real_run(words, v['T0'], V.LEN_A)
        bad += (rec['Y9'] != v['Y9']) + (rec['E3.h1'] != v['E3.h1'])
    print(f'cross-checks: {chk} bases, outer() against solve_order (Y9, w8) and the real compression (Y9, E3.h1): '
          f'mismatches {bad}')
    # constancy of Y9 and w8 over the inner word, real arithmetic: two trials of one outer step
    const_bad = 0
    for _ in range(chk):
        y = S.member(rng)
        base = {b: rng.getrandbits(32) for b in BASIS}
        base['Y4'] = y
        outs = []
        for d1 in (rng.getrandbits(32), rng.getrandbits(32)):
            base['E1.d1'] = d1
            it = iter([base[b] for b in BASIS])
            class Stub2:
                def randrange(s, n): return next(it)
            orig = V.class_member; V.class_member = lambda k: y
            try:
                v = V.solve_order(LINES, BASIS, Stub2())
            finally:
                V.class_member = orig
            rec, _ = V.real_run([v['w%d' % i] for i in range(16)], v['T0'], V.LEN_A)
            outs.append((rec['Y9'], v['w8'], rec['E3.h1'], rec['Y4']))
        const_bad += (outs[0][0] != outs[1][0]) + (outs[0][1] != outs[1][1]) + (outs[0][3] != outs[1][3])
        const_bad += outs[0][2] == outs[1][2]          # h1 should move
    print(f'real arithmetic, {chk} outer steps x 2 inner values: Y9 / w8 / Y4 moved or h1 did not move: {const_bad}')
    # pass rate on real outer steps
    targets = [(S.G(t), S.EPS, t) for t in S.TAUS]
    passed = 0
    for i in range(N):
        y = S.member(rng)
        q, w8 = outer(*(rng.getrandbits(32) for _ in range(6)), y, rng.getrandbits(32))
        E = (S.Y3 + y + w8) & M
        if any(S.solvable1(q, g) and S.solvable2(E, ror(g, 12), e) for g, e, t in targets):
            passed += 1
    p = passed / N
    print(f'real outer steps {N}: passing {passed}, share {p:.6f} = 2^{log2(p):.3f} '
          f'(+-{sqrt(passed) / N / p * 100:.1f}% Poisson); model exact 2^-9.8132 = {2 ** -9.8132:.6f}')


if __name__ == '__main__':
    main()
