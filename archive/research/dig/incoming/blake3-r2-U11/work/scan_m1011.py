import random, json, time
import numpy as np
from b3lib import *
rng = random.Random(1011)
out = {}
sub = lambda *q: (q[0] - sum(q[1:])) & M
add = lambda *q: sum(q) & M
def ctx(a):
    d = build(*a); A = d['A']
    sa, _ = compress_full(A, 55)
    return d, sa
t0 = time.time()
# ---- structure: where are w10, w11 used (schedule) -------------------
s1 = [P[i] for i in range(16)]            # round-1 slot i holds w[P[i]]
uses = {}
for w in (10, 11):
    uses[w] = dict(round0_slot=w, round1_slot=s1.index(w))
out['uses'] = uses   # w10: R0 D1 first word, R1 slot3 = C1 second word; w11: R0 D1 second, R1 slot9 = E0 second

# ---- Q1 --------------------------------------------------------------
N = 20000
bc = {10: [0]*32, 11: [0]*32}; diffnz = 0; x11ok = 0; d1fwd = 0
for _ in range(N):
    a = [rnd(rng) for _ in range(8)]
    d, sa = ctx(a); A, B = d['A'], d['B']
    if A[10] != B[10] or A[11] != B[11]: diffnz += 1
    for w in (10, 11):
        for b in range(32): bc[w][b] += (A[w] >> b) & 1
    S, X = sa['S'], sa['X']
    if X[11] == X11: x11ok += 1
    v = [0]*16; v[1], v[6], v[11], v[12] = S[1], S[6], S[11], S[12]
    G(v, 1, 6, 11, 12, A[10], A[11])
    if (v[1], v[6], v[11], v[12]) == (X[1], X[6], X[11], X[12]): d1fwd += 1
out['Q1'] = dict(N=N, A_vs_B_diff_nonzero=diffnz, X11_equals_pin=x11ok, D1_forward_reproduces_X1_X6_X11_X12=d1fwd,
    max_bit_bias_w10=max(abs(c/N-.5) for c in bc[10]), max_bit_bias_w11=max(abs(c/N-.5) for c in bc[11]),
    bitcount_range_w10=[min(bc[10]), max(bc[10])], bitcount_range_w11=[min(bc[11]), max(bc[11])])

# ---- Q2 --------------------------------------------------------------
NN = 1500
Q2 = {}
for w in (10, 11):
    r = dict(contexts=NN, same_bitflip_trials=0, same_flip_consts_kept=0, same_flip_X11_kept=0, same_flip_Y4_kept=0,
             same_flip_lemmaH_kept=0, same_flip_S_equal=0, Bonly_trials=0, Bonly_lemmaH_kept=0, Bonly_X_equal=0,
             ctrl_lemmaH=0, xchg_lanes={})
    for _ in range(NN):
        a = [rnd(rng) for _ in range(8)]
        d, sa = ctx(a); A, B = d['A'], d['B']
        sb0, ob0 = compress_full(B, 63); sa0, oa0 = compress_full(A, 55)
        if all(oa0[i] == ob0[i] for i in (0, 2, 5, 7)): r['ctrl_lemmaH'] += 1
        for bit in rng.sample(range(32), 4):
            dl = 1 << bit
            A2 = A[:]; B2 = B[:]; A2[w] ^= dl; B2[w] ^= dl
            sa2, oa2 = compress_full(A2, 55); sb2, ob2 = compress_full(B2, 63)
            X = sa2['X']; r['same_bitflip_trials'] += 1
            if (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15): r['same_flip_consts_kept'] += 1
            if X[11] == X11: r['same_flip_X11_kept'] += 1
            if sa2['Y'][4] == a[7]: r['same_flip_Y4_kept'] += 1
            if all(oa2[i] == ob2[i] for i in (0, 2, 5, 7)): r['same_flip_lemmaH_kept'] += 1
            if sa2['S'] == sb2['S']: r['same_flip_S_equal'] += 1
            for i in range(16):
                if X[i] != sa0['X'][i]: r['xchg_lanes'][i] = r['xchg_lanes'].get(i, 0) + 1
            B3 = B[:]; B3[w] ^= dl
            sb3, ob3 = compress_full(B3, 63); r['Bonly_trials'] += 1
            if all(oa0[i] == ob3[i] for i in (0, 2, 5, 7)): r['Bonly_lemmaH_kept'] += 1
            if sb3['X'] == sa0['X']: r['Bonly_X_equal'] += 1
    Q2[f'w{w}'] = r
# relax-one exact: pairs (w10,w11) with X11 = pin, given context: w11 is unique for every w10
chk = dict(ctxs=0, w10_trials=0, unique_w11_hits=0, other_w11_trials=0, other_w11_hits=0)
for _ in range(20):
    a = [rnd(rng) for _ in range(8)]
    d, sa = ctx(a); S = sa['S']
    for _ in range(2000):
        w10 = rnd(rng)
        v = [0]*16; v[1], v[6], v[11], v[12] = S[1], S[6], S[11], S[12]
        a1 = add(S[1], S[6], w10); d1 = ror(S[12] ^ a1, 16); c1 = add(S[11], d1)
        b1 = ror(S[6] ^ c1, 12)
        d2 = sub(X11, c1); a2 = rol(d2, 8) ^ d1; w11 = sub(a2, a1, b1)
        vv = v[:]; G(vv, 1, 6, 11, 12, w10, w11)
        chk['w10_trials'] += 1
        if vv[11] == X11: chk['unique_w11_hits'] += 1
        w11b = rnd(rng)
        if w11b != w11:
            vv = v[:]; G(vv, 1, 6, 11, 12, w10, w11b)
            chk['other_w11_trials'] += 1
            if vv[11] == X11: chk['other_w11_hits'] += 1
    chk['ctxs'] += 1
Q2['pin_X11_solve'] = chk
out['Q2'] = Q2

# ---- Q3 --------------------------------------------------------------
m = np.uint64(M)
def rolv(x, r): return ((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & m
def rorv(x, r): return ((x >> np.uint64(r)) | (x << np.uint64(32 - r))) & m
def u(x): return np.uint64(x)
def make_ctx(a):
    d, sa = ctx(a); S, X = sa['S'], sa['X']
    return dict(C0c1=a[0], C0d1=a[1], C0b1=ror(X[4] ^ a[0], 12), w6=d['A'][6], S1=S[1], S6=S[6], S11=S[11], S12=S[12])
def pair_of_y(c, y):
    Y8 = rolv(y, 7) ^ u(c['C0b1']); Y12 = (Y8 - u(c['C0c1'])) & m
    Y0 = rolv(Y12, 8) ^ u(c['C0d1']); C0a1 = (Y0 - u(c['C0b1']) - u(c['w6'])) & m
    X12 = rolv(u(c['C0d1']), 16) ^ C0a1
    D1c1 = (u(X11) - X12) & m; D1d1 = (D1c1 - u(c['S11'])) & m
    D1a1 = rolv(D1d1, 16) ^ u(c['S12'])
    w10 = (D1a1 - u(c['S1']) - u(c['S6'])) & m
    D1b1 = rorv(u(c['S6']) ^ D1c1, 12)
    X1 = rolv(X12, 8) ^ D1d1
    w11 = (X1 - D1a1 - D1b1) & m
    return w10, w11
def y_of_w10(c, w10):
    D1a1 = (w10 + u(c['S1']) + u(c['S6'])) & m
    D1d1 = rorv(D1a1 ^ u(c['S12']), 16); D1c1 = (D1d1 + u(c['S11'])) & m
    X12 = (u(X11) - D1c1) & m
    C0a1 = X12 ^ rolv(u(c['C0d1']), 16)
    Y0 = (C0a1 + u(c['C0b1']) + u(c['w6'])) & m
    Y12 = rorv(Y0 ^ u(c['C0d1']), 8); Y8 = (Y12 + u(c['C0c1'])) & m
    return rorv(Y8 ^ u(c['C0b1']), 7)
a = [rnd(rng) for _ in range(8)]
c = make_ctx(a)
ys = [rnd(rng) for _ in range(2000)]
bad = 0
for yv in ys:
    dd = build(*a[:7], yv)
    w10, w11 = pair_of_y(c, np.array([yv], dtype=np.uint64))
    if (int(w10[0]), int(w11[0])) != (dd['A'][10], dd['A'][11]): bad += 1
assert bad == 0, bad
LOG = 25
y1 = np.arange(1 << LOG, dtype=np.uint64)
y2 = np.array(rng.sample(range(1 << 32), 1 << LOG), dtype=np.uint64)
res = {}
for nm, yy in (('consecutive', y1), ('random', y2)):
    w10, w11 = pair_of_y(c, yy)
    res[nm] = dict(n=int(yy.size), distinct_y=int(np.unique(yy).size), distinct_w10=int(np.unique(w10).size),
                   distinct_w11=int(np.unique(w11).size), distinct_pair=int(np.unique((w10 << np.uint64(32)) | w11).size),
                   inverse_w10_to_y_roundtrip=int((y_of_w10(c, w10) == yy).sum()))
res['validated_vs_build'] = 2000
out['Q3_y_sweep'] = res
dep = {}
names = ['C0c1', 'C0d1', 'D3d1', 'S15', 'S9', 'w5', 'X2', 'y']
for k, nm in enumerate(names):
    ch10 = ch11 = 0; T = 1500
    for _ in range(T):
        a = [rnd(rng) for _ in range(8)]; a2 = a[:]; a2[k] = rnd(rng)
        d1_ = build(*a)['A']; d2_ = build(*a2)['A']
        ch10 += d1_[10] != d2_[10]; ch11 += d1_[11] != d2_[11]
    dep[nm] = dict(trials=T, w10_changed=ch10, w11_changed=ch11)
out['Q3_dependence'] = dep
T = 150000; ps = set(); s10 = set(); s11 = set()
for _ in range(T):
    A = build(*[rnd(rng) for _ in range(8)])['A']; s10.add(A[10]); s11.add(A[11]); ps.add((A[10], A[11]))
out['Q3_global'] = dict(builds=T, distinct_w10=len(s10), distinct_w11=len(s11), distinct_pairs=len(ps))

# ---- Q4 --------------------------------------------------------------
def D1_out(S1, S6, S11, S12, w10, w11):
    v = [0]*16; v[1], v[6], v[11], v[12] = S1, S6, S11, S12
    G(v, 1, 6, 11, 12, w10, w11); return (v[1], v[6], v[11], v[12])
T = 100000
ab = dict(trials=T, S1S12_diff_absorbed=0, S1_only_absorbed=0, S12_only_absorbed=0, S6_recovered_from_outputs_equals_A=0,
          S11_recovered_from_outputs_equals_A=0)
for _ in range(T):
    S1, S6, S11, S12, w10, w11 = [rnd(rng) for _ in range(6)]
    o = D1_out(S1, S6, S11, S12, w10, w11)
    S1b, S12b = rnd(rng), rnd(rng)
    a2, b2, c2, d2 = o
    b1 = rol(b2, 7) ^ c2; c1 = sub(c2, d2); d1 = rol(d2, 8) ^ a2
    if (rol(b1, 12) ^ c1) == S6: ab['S6_recovered_from_outputs_equals_A'] += 1
    if sub(c1, d1) == S11: ab['S11_recovered_from_outputs_equals_A'] += 1
    a1b = rol(d1, 16) ^ S12b
    w10b = sub(a1b, S1b, S6); w11b = sub(a2, a1b, b1)
    if D1_out(S1b, S6, S11, S12b, w10b, w11b) == o: ab['S1S12_diff_absorbed'] += 1
    a1c = rol(d1, 16) ^ S12
    if D1_out(S1b, S6, S11, S12, sub(a1c, S1b, S6), sub(a2, a1c, b1)) == o: ab['S1_only_absorbed'] += 1
    a1d = rol(d1, 16) ^ S12b
    if D1_out(S1, S6, S11, S12b, sub(a1d, S1, S6), sub(a2, a1d, b1)) == o: ab['S12_only_absorbed'] += 1
out['Q4_D1_absorb'] = ab
T = 200000; f = 0
for _ in range(T):
    w0, w1, t, thi = rnd(rng), rnd(rng), rnd(rng), rnd(rng)
    v = IV[:8] + IV[:4] + [t, thi, rnd(rng), rnd(rng)]
    G(v, 0, 4, 8, 12, w0, w1)
    S4, S8, S12 = v[4], v[8], v[12]
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ IV[4]
    if sub(S8, K0c1) == S12: f += 1
out['Q4_K0_S12_function_of_S4_S8'] = dict(trials=T, S12_equals_S8_minus_K0c1=f)
out['seconds'] = time.time() - t0
json.dump(out, open('scan_m1011.out.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
