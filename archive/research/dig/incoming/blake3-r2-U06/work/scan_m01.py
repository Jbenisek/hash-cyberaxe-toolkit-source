import random, json
import numpy as np
from b3lib import *
rng = random.Random(777)
out = {}
sub = lambda *q: (q[0] - sum(q[1:])) & M
add = lambda *q: sum(q) & M

# ---- Q1: difference and condition count on w0,w1
N = 20000
bc0 = [0]*32; bc1 = [0]*32; difffail = 0
for _ in range(N):
    a = [rnd(rng) for _ in range(8)]
    d = build(*a); A, B = d['A'], d['B']
    if A[0] != B[0] or A[1] != B[1]: difffail += 1
    for b in range(32):
        bc0[b] += (A[0] >> b) & 1; bc1[b] += (A[1] >> b) & 1
out['Q1'] = dict(N=N, xor_diff_nonzero=difffail,
                 max_bit_bias_w0=max(abs(c/N-0.5) for c in bc0), max_bit_bias_w1=max(abs(c/N-0.5) for c in bc1),
                 minmax_w0=[min(bc0), max(bc0)], minmax_w1=[min(bc1), max(bc1)])

# ---- Q2: necessity
NN = 3000
res = {}
for name, idx in (('w0', 0), ('w1', 1)):
    eqH = 0; nd = []; both_keep = 0
    for _ in range(NN):
        a = [rnd(rng) for _ in range(8)]
        d = build(*a); A, B = d['A'], d['B']
        sa, oa = compress_full(A, 55)
        for dl in (1 << rng.randrange(32), rnd(rng) | 1):
            B2 = B[:]; B2[idx] ^= dl
            sb, ob = compress_full(B2, 63)
            if all(oa[i] == ob[i] for i in (0, 2, 5, 7)): eqH += 1
            nd.append(sum(1 for i in range(8) if oa[i] != ob[i]))
        A2 = A[:]; A2[idx] ^= (rnd(rng) | 1)
        sa2, _ = compress_full(A2, 55); X = sa2['X']
        if (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15): both_keep += 1
    res[name] = dict(trials_diff_in_B_only=2*NN, lemmaH_events_kept=eqH, mean_digest_words_differing=sum(nd)/len(nd),
                     min_digest_words_differing=min(nd), value_changed_keep_admissible=both_keep, value_changed_trials=NN)
out['Q2'] = res

# ---- Q3 exact dof
def k0_fwd(w0, w1, t=0, thi=0, n=55, flags=11):
    v = IV[:8] + IV[:4] + [t, thi, n, flags]
    G(v, 0, 4, 8, 12, w0, w1); return v[4], v[8], v[0], v[12]
def k0_inv(S4, S8):
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ IV[4]; K0d1 = (K0c1 - IV[0]) & M; K0a1 = rol(K0d1, 16)
    S12 = (S8 - K0c1) & M; S0 = rol(S12, 8) ^ K0d1
    return (K0a1 - IV[0] - IV[4]) & M, (S0 - K0a1 - K0b1) & M
rt1 = 0; rt2 = 0; M1 = 200000
for _ in range(M1):
    w0, w1 = rnd(rng), rnd(rng)
    S4, S8, S0, S12 = k0_fwd(w0, w1)
    if k0_inv(S4, S8) == (w0, w1): rt1 += 1
    S4, S8 = rnd(rng), rnd(rng)
    a, b = k0_inv(S4, S8); r = k0_fwd(a, b)
    if (r[0], r[1]) == (S4, S8): rt2 += 1
out['Q3_k0_roundtrip'] = dict(trials=M1, fwd_inv_ok=rt1, inv_fwd_ok=rt2)

def ctx_consts(a6):
    C0c1, C0d1, D3d1, S15, S9, w5 = a6
    K2a1 = add(IV[2], IV[6], W4); K2d1 = ror(55 ^ K2a1, 16)
    S2 = add(K2a1, ror(IV[6] ^ add(IV[2], K2d1), 12), w5)
    S14 = ror(K2d1 ^ S2, 8)
    D3a1 = rol(D3d1, 16) ^ S14; D3c1 = add(S9, D3d1); D3b1 = sub(X3, D3a1); S4 = rol(D3b1, 12) ^ D3c1
    S3 = sub(D3a1, S4)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = add(IV[3], K3d1); K3b1 = ror(IV[7] ^ K3c1, 12)
    S11 = add(K3c1, S15); S7 = ror(K3b1 ^ S11, 7)
    X8 = sub(C0c1, C0d1); D2b1 = rol(X7, 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7; X13 = sub(X8, D2c1)
    return S4, D2c1, X13
a = [rnd(rng) for _ in range(8)]
S4c, D2c1, X13 = ctx_consts(a[:6])
R = rol(X13, 8)
m = np.uint64(M)
def rolv(x, r): return ((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & m
def w01_of_X2(X2):
    D2d1 = np.uint64(R) ^ X2
    S8 = (np.uint64(D2c1) - D2d1) & m
    K0b1 = rolv(np.uint64(S4c), 7) ^ S8
    K0c1 = rolv(K0b1, 12) ^ np.uint64(IV[4])
    K0d1 = (K0c1 - np.uint64(IV[0])) & m
    K0a1 = rolv(K0d1, 16)
    S12 = (S8 - K0c1) & m
    S0 = rolv(S12, 8) ^ K0d1
    w0 = (K0a1 - np.uint64(IV[0]) - np.uint64(IV[4])) & m
    w1 = (S0 - K0a1 - K0b1) & m
    return w0, w1
for _ in range(2000):
    x = rnd(rng); dd = build(a[0], a[1], a[2], a[3], a[4], a[5], x, a[7])
    w0, w1 = w01_of_X2(np.array([x], dtype=np.uint64))
    assert (int(w0[0]), int(w1[0])) == (dd['A'][0], dd['A'][1])
LOG = 24
x = np.arange(1 << LOG, dtype=np.uint64)
w0, w1 = w01_of_X2(x)
x2 = np.array(rng.sample(range(1 << 32), 1 << LOG), dtype=np.uint64)
w0r, w1r = w01_of_X2(x2)
out['Q3_X2_sweep'] = dict(n_consecutive=1 << LOG, distinct_w0=int(np.unique(w0).size), distinct_w1=int(np.unique(w1).size),
                          distinct_pair=int(np.unique((w0 << np.uint64(32)) | w1).size),
                          n_random_distinct_X2=int(np.unique(x2).size), distinct_w0_rand=int(np.unique(w0r).size),
                          distinct_w1_rand=int(np.unique(w1r).size))

def solve_for_w01(w0t, w1t):
    S4t, S8t, _, _ = k0_fwd(w0t, w1t)
    C0c1, C0d1, D3d1, S15, w5, y = [rnd(rng) for _ in range(6)]
    K2a1 = add(IV[2], IV[6], W4); K2d1 = ror(55 ^ K2a1, 16)
    S2 = add(K2a1, ror(IV[6] ^ add(IV[2], K2d1), 12), w5); S14 = ror(K2d1 ^ S2, 8)
    D3a1 = rol(D3d1, 16) ^ S14; D3b1 = sub(X3, D3a1)
    D3c1 = rol(D3b1, 12) ^ S4t
    S9 = (D3c1 - D3d1) & M
    S3 = sub(D3a1, S4t)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = add(IV[3], K3d1); K3b1 = ror(IV[7] ^ K3c1, 12)
    S11 = add(K3c1, S15); S7 = ror(K3b1 ^ S11, 7)
    X8 = sub(C0c1, C0d1); D2b1 = rol(X7, 7) ^ X8; D2c1_ = rol(D2b1, 12) ^ S7; X13_ = sub(X8, D2c1_)
    D2d1 = sub(D2c1_, S8t)
    X2 = rol(X13_, 8) ^ D2d1
    return (C0c1, C0d1, D3d1, S15, S9, w5, X2, y)
hit = 0; T = 20000
for _ in range(T):
    w0t, w1t = rnd(rng), rnd(rng)
    d = build(*solve_for_w01(w0t, w1t))
    sa, oa = compress_full(d['A'], 55); sb, ob = compress_full(d['B'], 63)
    X = sa['X']
    if d['A'][0] == w0t and d['A'][1] == w1t and (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15) \
       and all(oa[i] == ob[i] for i in (0, 2, 5, 7)): hit += 1
out['Q3_surjective_targets'] = dict(trials=T, hit=hit)

# counter instance
ct = 0; Tc = 100000; tset = set(); w0set = set()
S4, S8 = rnd(rng), rnd(rng)
K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ IV[4]; K0d1 = (K0c1 - IV[0]) & M
S12 = (S8 - K0c1) & M; S0 = rol(S12, 8) ^ K0d1
for _ in range(Tc):
    w0 = rnd(rng); w0set.add(w0)
    K0a1 = (IV[0] + IV[4] + w0) & M
    t = rol(K0d1, 16) ^ K0a1; w1 = (S0 - K0a1 - K0b1) & M
    r = k0_fwd(w0, w1, t, 0, 64, 3)
    if (r[0], r[1], r[2], r[3]) == (S4, S8, S0, S12): ct += 1
    tset.add(t)
out['Q3_counter'] = dict(trials=Tc, ok=ct, distinct_w0=len(w0set), distinct_t=len(tset))

# ---- Q4 alternatives: counters differing between A and B absorbed by w0 difference
alt = dict(trials=0, K0_states_equal=0, lemmaH_kept=0); wd = []
for _ in range(2000):
    a_ = [rnd(rng) for _ in range(8)]
    d = build(*a_); A, B = d['A'], d['B']
    dl = rnd(rng) | 1
    B2 = B[:]; B2[0] = (B[0] + dl) & M
    a1A = (IV[0] + IV[4] + A[0]) & M; a1B = (IV[0] + IV[4] + B2[0]) & M
    tA = rnd(rng); tB = tA ^ a1A ^ a1B
    B2[1] = (B[1] + a1A - a1B) & M
    sa, oa = compress_full(A, 55, tA, 0, 3); sb, ob = compress_full(B2, 63, tB, 0, 3)
    alt['trials'] += 1
    # only K0 outputs (S0,S4,S8,S12) can match; other lanes see v12=t
    if [sa['S'][i] for i in (0, 4, 8, 12)] == [sb['S'][i] for i in (0, 4, 8, 12)]: alt['K0_states_equal'] += 1
    if all(oa[i] == ob[i] for i in (0, 2, 5, 7)): alt['lemmaH_kept'] += 1
    wd.append(sum(1 for i in range(8) if oa[i] != ob[i]))
alt['mean_words_differ'] = sum(wd)/len(wd); alt['min_words_differ'] = min(wd)
out['Q4_counter_diff_alt'] = alt
json.dump(out, open('scan_m01.out.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
