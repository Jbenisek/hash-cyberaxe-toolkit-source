#!/usr/bin/env python3
"""e3cond.py (counter_next/stack; research only)

The E3 side of a counter-arrangement trial, written as three exact XOR-difference conditions on one inner word.

Per outer step the counter arrangement fixes y = Y4, Q = Y9, W = w8 (Sol answer Y section 7: E3 coordinates (y,Q,W,h));
only h1 moves.  With E = Y3 + y + w8 and E' = Y3' + y + w8 = E + DY3 (exact), and E1 outcome (beta, tau, eps):
  R = 0  <=>  dE3.c = tau (word 1), dE3.a = eps (word 3), dE3.b = ROR(tau,8) (word 4), dE3.d = ROR(beta^eps,7) (word 6)
and with h1' = h1 ^ eta (class), f1 = ROR(y ^ g1, 12), e2 = E + f1, h2 = ROR(h1 ^ e2, 8), g2 = g1 + h2:
  (1) (Q + h1) ^ (Q + (h1 ^ eta)) = G   with G = ROL(tau ^ ROR(tau,1), 12)          [from words 1 and 4]
  (2) (E + f1) ^ (E' + (f1 ^ ROR(G,12))) = eps                                       [word 3]
  (3) (g1 + h2) ^ (g1' + h2') = tau,  h2 ^ h2' = ROR(eta ^ eps, 8)                   [word 1]
  word 6 needs n = eps ^ ROL(beta ^ eps, 1) ^ eta = 0 (Lemma N; E1 only).
Part A checks these identities on random real E3 executions (both messages).  Part B counts, exactly by carry DP over
one 32-bit word, the solutions of (1) for sampled Q and of (2) for sampled E, for the seven beta* outcomes, and the share
of outer steps for which (1) and (2) have no solution for any of the seven (such an outer step cannot contain a
collision of a beta* outcome: an EXACT necessary-condition filter on outer words).
"""
import random, sys, math
M = 0xFFFFFFFF
def ror(x, r): return ((x >> r) | (x << (32 - r))) & M
def rol(x, r): return ror(x, (32 - r) % 32)

Y3, Y3B, ETA = 0x8127C181, 0x7EDF3E7E, 0x830303CF
DY3 = (Y3B - Y3) & M
SUB_M, SUB_V = 0x07EF8303, 0x030C0303          # sub-class: (Y3 + y) & SUB_M == SUB_V
CLS_M = 0x03CF8303
BETA = 0x18B0E098
EPS = 0x6E21BE55
TAUS = [0x175020A0, 0x185020A0, 0x275020A0, 0x285020A0, 0x385020A0, 0x675020A0, 0x685020A0]
WEIGHT = [96, 256, 16, 384, 256, 1, 24]        # Sol answer Y 9.5: L_j N_j / 2^16 / 2^81 numerators (sum 1033)


def g_of(tau): return rol(tau ^ ror(tau, 1), 12)


def e3(a, y, q, d, w8):
    """G(a, b=y, c=q, d, mx=0, my=w8) as E3: returns (e1, h1, g1, f1, e2, h2, g2, f2)."""
    e1 = (a + y) & M
    h1 = ror(d ^ e1, 16)
    g1 = (q + h1) & M
    f1 = ror(y ^ g1, 12)
    e2 = (e1 + f1 + w8) & M
    h2 = ror(h1 ^ e2, 8)
    g2 = (g1 + h2) & M
    f2 = ror(f1 ^ g2, 7)
    return e1, h1, g1, f1, e2, h2, g2, f2


def member(rng, mask=SUB_M, val=SUB_V):
    e1 = (val | (rng.getrandbits(32) & ~mask)) & M
    return (e1 - Y3) & M


def count_add_xor(x0, x1, dz, out):
    """#v in Z_2^32 with (x0 + v) ^ (x1 + (v ^ dz)) == out (exact, carry DP)."""
    st = {(0, 0): 1}
    for i in range(32):
        a, b, dd, o = x0 >> i & 1, x1 >> i & 1, dz >> i & 1, out >> i & 1
        nst = {}
        for (c, cb), n in st.items():
            for v in (0, 1):
                vb = v ^ dd
                s, sb = a ^ v ^ c, b ^ vb ^ cb
                if s ^ sb != o:
                    continue
                k = ((a & v) | (a & c) | (v & c), (b & vb) | (b & cb) | (vb & cb))
                nst[k] = nst.get(k, 0) + n
        st = nst
        if not st:
            return 0
    return sum(st.values())


def count_cond1(q, g):
    """#h1 with (q + h1) ^ (q + (h1 ^ eta)) == g."""
    return count_add_xor(q, q, ETA, g)


def count_cond2(E, df1):
    """#f1 with (E + f1) ^ ((E + DY3) + (f1 ^ df1)) == eps."""
    return count_add_xor(E, (E + DY3) & M, df1, EPS)


def lm_valid(a, b, g):
    """Lipmaa-Moriai: XOR-differential (a, b -> g) of addition possible?  returns (valid, weight)."""
    def eq(x, y, z): return (~x ^ y) & (~x ^ z) & M
    if eq(a << 1 & M, b << 1 & M, g << 1 & M) & (a ^ b ^ g ^ (b << 1 & M)) & M:
        return False, None
    return True, bin(~eq(a, b, g) & 0x7FFFFFFF).count('1')


def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    nsamp = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    print('constants: DY3 %08x eta %08x beta* %08x eps %08x' % (DY3, ETA, BETA, EPS))
    n = EPS ^ rol(BETA ^ EPS, 1) ^ ETA
    print('Lemma N word for beta*, eps: n = %08x (0 needed)' % n)
    Gs = [g_of(t) for t in TAUS]
    for t, g, w in zip(TAUS, Gs, WEIGHT):
        v1 = lm_valid(ETA, 0, g)
        v2 = lm_valid(rol(ETA, 0) * 0, 0, 0)
        print('tau %08x  G %08x  df1 %08x  weight %4d/1033   LM(eta,0->G) %s' % (t, g, ror(g, 12), w, v1))
    common_m = M
    for g in Gs:
        common_m &= ~(g ^ Gs[0]) & M
    print('G values agree on mask %08x (%d bits), common value %08x' % (common_m, bin(common_m).count('1'), Gs[0] & common_m))

    # ---- Part A: identities on real E3 executions, both messages ----
    bad = 0
    hits1 = 0
    for _ in range(200000):
        y, q, d, w8 = member(rng), rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32)
        A = e3(Y3, y, q, d, w8)
        B = e3(Y3B, y, q, d, w8)
        dh1 = A[1] ^ B[1]; dg1 = A[2] ^ B[2]; df1 = A[3] ^ B[3]; de2 = A[4] ^ B[4]
        dh2 = A[5] ^ B[5]; dg2 = A[6] ^ B[6]; df2 = A[7] ^ B[7]
        E = (Y3 + y + w8) & M
        ok = (dh1 == ETA and df1 == ror(dg1, 12) and dh2 == ror(ETA ^ de2, 8) and df2 == ror(df1 ^ dg2, 7)
              and B[4] == ((E + DY3 + B[3]) & M) and A[4] == ((E + A[3]) & M))
        # implication used for (1): if dg2 = tau and df2 = ROR(tau,8) then dg1 = G(tau)
        if df2 == ror(dg2, 8):
            hits1 += 1
            ok = ok and dg1 == g_of(dg2)
        bad += not ok
    print('Part A: 200000 real E3 pairs (sub-class y), identity failures %d; df2 == ROR(dg2,8) seen %d times' % (bad, hits1))
    # planted check of the counters: a real pair's own differences must be counted >= 1
    for _ in range(300):
        y, q, d, w8 = member(rng), rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32)
        A = e3(Y3, y, q, d, w8); B = e3(Y3B, y, q, d, w8)
        if count_add_xor(q, q, ETA, A[2] ^ B[2]) < 1: bad += 1
        E = (Y3 + y + w8) & M
        if count_add_xor(E, (E + DY3) & M, A[3] ^ B[3], A[4] ^ B[4]) < 1: bad += 1
    # brute-force check of count_add_xor on a 2^20 slice is too slow in python; check exhaustively at 8 bits instead
    def brute8(x0, x1, dz, out):
        return sum(1 for v in range(256) if (((x0 + v) ^ (x1 + (v ^ dz))) & 255) == out)
    def dp8(x0, x1, dz, out):
        st = {(0, 0): 1}
        for i in range(8):
            a, b, dd, o = x0 >> i & 1, x1 >> i & 1, dz >> i & 1, out >> i & 1
            nst = {}
            for (c, cb), nn in st.items():
                for v in (0, 1):
                    vb = v ^ dd; s, sb = a ^ v ^ c, b ^ vb ^ cb
                    if s ^ sb != o: continue
                    k = ((a & v) | (a & c) | (v & c), (b & vb) | (b & cb) | (vb & cb))
                    nst[k] = nst.get(k, 0) + nn
            st = nst
        return sum(st.values())
    for _ in range(2000):
        x0, x1, dz, out = (rng.getrandbits(8) for _ in range(4))
        if brute8(x0, x1, dz, out) != dp8(x0, x1, dz, out): bad += 1
    print('counter checks (planted 600, brute force at 8 bits 2000): failures %d' % bad)

    # ---- Part B: per-outer-step solution counts of (1) and (2) ----
    t1 = [[0] * 7 for _ in range(nsamp)]
    t2 = [[0] * 7 for _ in range(nsamp)]
    for s in range(nsamp):
        q = rng.getrandbits(32)
        y, w8 = member(rng), rng.getrandbits(32)
        E = (Y3 + y + w8) & M
        for j, g in enumerate(Gs):
            t1[s][j] = count_cond1(q, g)
            t2[s][j] = count_cond2(E, ror(g, 12))
    for j in range(7):
        m1 = sum(t1[s][j] for s in range(nsamp)) / nsamp
        m2 = sum(t2[s][j] for s in range(nsamp)) / nsamp
        z1 = sum(1 for s in range(nsamp) if t1[s][j] == 0) / nsamp
        z2 = sum(1 for s in range(nsamp) if t2[s][j] == 0) / nsamp
        print('tau %08x: (1) mean #h1 2^%.3f, P(none) %.4f | (2) mean #f1 2^%.3f, P(none) %.4f'
              % (TAUS[j], math.log2(m1) if m1 else -99, z1, math.log2(m2) if m2 else -99, z2))
    any1 = sum(1 for s in range(nsamp) if any(t1[s])) / nsamp
    any2 = sum(1 for s in range(nsamp) if any(t2[s])) / nsamp
    both = sum(1 for s in range(nsamp) if any(t1[s][j] and t2[s][j] for j in range(7))) / nsamp
    print('outer steps with some j solvable: (1) %.4f  (2) %.4f  (1) and (2) for the same j %.5f  (n = %d)'
          % (any1, any2, both, nsamp))
    # weighted mass of surviving steps (product of counts per j, weight = model share of row j): a proxy only
    pm = [sum(WEIGHT[j] * t1[s][j] * t2[s][j] for j in range(7)) for s in range(nsamp)]
    tot = sum(pm)
    print('proxy mass sum_j w_j*#1*#2: share carried by the surviving steps 1.0 by construction; '
          'top 1%% of steps carries %.3f of it' % (sum(sorted(pm)[-max(1, nsamp // 100):]) / tot if tot else 0))


if __name__ == '__main__':
    main()
