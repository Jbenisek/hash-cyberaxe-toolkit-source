import random, json, re
import b3lib as bl
from b3lib import *
rng = random.Random(1213)
out = {}
HD = lambda x: bin(x).count('1')
def eq4(oa, ob): return sum(1 for i in (0,2,5,7) if oa[i]==ob[i])
def ok(A, B):
    sa, oa = compress_full(A, 55); sb, ob = compress_full(B, 63)
    return sa, oa, sb, ob
def ctx(): return [rnd(rng) for _ in range(8)]

# ---- Q1 (m12, m13): difference and condition
N = 20000; d12 = d13 = 0; top0 = 0; w13ok = 0
bc12 = [0]*32
for _ in range(N):
    d = build(*ctx()); A, B = d['A'], d['B']
    d12 += A[12] != B[12]; d13 += A[13] != B[13]
    w13ok += A[13] == W13; top0 += (A[13] >> 24) == 0
    for b in range(32): bc12[b] += (A[12] >> b) & 1
out['Q1'] = dict(N=N, m12_differs_A_B=d12, m13_differs_A_B=d13, m13_equals_W13=w13ok, m13_top_byte_zero=top0,
                 m12_max_bit_bias=max(abs(c/N-0.5) for c in bc12))
# D2 / E1 / C3 state equality between A and B (difference-freeness of the calls that read m12, m13)
eqD2 = eqE1a = eqE1d = n = 0; c3diff = 0
for _ in range(3000):
    d = build(*ctx()); A, B = d['A'], d['B']
    sa, oa, sb, ob = ok(A, B)
    n += 1
    eqD2 += (sa['X'][2], sa['X'][7], sa['X'][8], sa['X'][13]) == (sb['X'][2], sb['X'][7], sb['X'][8], sb['X'][13])
    Y = sa['Y']; Yb = sb['Y']
    a1 = (Y[1]+Y[6]+A[12]) & M; a1b = (Yb[1]+Yb[6]+B[12]) & M
    eqE1a += a1 == a1b
    eqE1d += rol(Y[12], 0) == Yb[12]
    c3diff += (Y[3] != Yb[3]) and (Y[11] != Yb[11]) and Y[7] == Yb[7] and Y[15] == Yb[15]
out['Q1_calls'] = dict(n=n, D2_outputs_equal=eqD2, E1_a1_equal=eqE1a, E1_Y12_equal=eqE1d, C3_pattern_Y3_Y11_differ_Y7_Y15_equal=c3diff)

# ---- Q2 relaxations
NN = 3000
r = {}
# m12: change w12 in both messages by same random value (no re-solve)
keep = eqs = 0; tot = 0; eqB = 0
for _ in range(NN):
    d = build(*ctx()); A, B = d['A'], d['B']
    v = rnd(rng) | 1
    A2 = A[:]; B2 = B[:]; A2[12] = (A[12]+v) & M; B2[12] = (B[12]+v) & M
    sa, oa, sb, ob = ok(A2, B2)
    X = sa['X']; keep += (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15)
    eqs += eq4(oa, ob); tot += 4
    eqB += all(oa[i]==ob[i] for i in (0,2,5,7))
r['m12_shift_both_no_resolve'] = dict(trials=NN, constants_X3_X7_X11_X15_kept=keep, digest_words_0257_equal_total=eqs, of=tot, all_four_equal=eqB)
# m13: change w13 in both by same random value (no re-solve)
keep = eqs = eqB = 0
for _ in range(NN):
    d = build(*ctx()); A, B = d['A'], d['B']
    v = rnd(rng) | 1
    A2 = A[:]; B2 = B[:]; A2[13] = (A[13]+v) & M; B2[13] = (B[13]+v) & M
    sa, oa, sb, ob = ok(A2, B2)
    X = sa['X']; keep += (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15)
    eqs += eq4(oa, ob); eqB += all(oa[i]==ob[i] for i in (0,2,5,7))
r['m13_shift_both_no_resolve'] = dict(trials=NN, constants_kept=keep, digest_words_0257_equal_total=eqs, of=4*NN, all_four_equal=eqB)
# m13: rebuild (re-solve) with alternative w13 from exhaustive 2^32 sets (w13enum_out.txt)
sets = {'dboth': [], 'donly': [], 'bonly': []}
for l in open('w13enum_out.txt'):
    m = re.match(r'SET w13=([0-9a-f]+) d=(\d) b=(\d) top0=(\d)', l)
    if m:
        w = int(m.group(1), 16); dd, bb = int(m.group(2)), int(m.group(3))
        sets['dboth' if dd and bb else 'donly' if dd else 'bonly'].append(w)
oldW13 = bl.W13
alt = {}
for name, lst in sets.items():
    res = []
    for w in lst:
        bl.W13 = w
        cnt = {i: 0 for i in range(8)}; allok = 0; T = 150; adm = 0
        for _ in range(T):
            d = bl.build(*ctx()); A, B = d['A'], d['B']
            sa, oa, sb, ob = ok(A, B)
            X = sa['X']; adm += (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15)
            for i in range(8): cnt[i] += oa[i] == ob[i]
        res.append(dict(w13='%08x' % w, top_byte_zero=(w >> 24) == 0, admissible_X_consts=adm, trials=T, digest_word_equal_counts=[cnt[i] for i in range(8)]))
    alt[name] = res
bl.W13 = oldW13
r['m13_alt_values_rebuilt'] = alt
out['Q2'] = r

# ---- Q3 dof
# m12 <-> X2 bijection check: w12 - X2 is constant for fixed other parameters
dofres = []
for _ in range(40):
    a = ctx(); offs = set()
    for _ in range(50):
        a[6] = rnd(rng); d = build(*a); offs.add((d['A'][12] - a[6]) & M)
    dofres.append(len(offs))
adm = lh = 0; T = 3000
for _ in range(T):
    d = build(*ctx()); A, B = d['A'], d['B']
    sa, oa, sb, ob = ok(A, B)
    X = sa['X']; adm += (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15)
    lh += all(oa[i]==ob[i] for i in (0,2,5,7))
import numpy as np
a = ctx(); base = build(*a)['A'][12] - a[6]
xs = np.arange(1 << 24, dtype=np.uint64)
w12s = (xs + np.uint64((base) & M)) & np.uint64(M)
out['Q3'] = dict(offset_w12_minus_X2_distinct_values_per_context=sorted(set(dofres)), admissible_blocks=adm, lemmaH_equal=lh, T=T,
                 distinct_w12_over_2p24_consecutive_X2=int(np.unique(w12s).size))
# residual spread: vary X2 only, count distinct residual R over 4096 values and mean weight
a = ctx(); Rs = set(); hw = []
for i in range(4096):
    a[6] = rnd(rng); d = build(*a); A, B = d['A'], d['B']
    sa, oa, sb, ob = ok(A, B)
    R = tuple(oa[j] ^ ob[j] for j in (1,3,4,6)); Rs.add(R); hw.append(sum(HD(x) for x in R))
out['Q3_residual'] = dict(trials=4096, distinct_residual=len(Rs), mean_hw=sum(hw)/len(hw), min_hw=min(hw), zero_residual=sum(1 for x in hw if x == 0))

# ---- Q4 context for the E1 sweep (C program) : a real pair's Y values
d = build(*ctx()); A, B = d['A'], d['B']
sa, oa, sb, ob = ok(A, B)
Y, Yb = sa['Y'], sb['Y']
assert Y[1]==Yb[1] and Y[6]==Yb[6] and Y[12]==Yb[12] and Y[11]!=Yb[11]
out['Q4_ctx'] = dict(Y1=Y[1], Y6=Y[6], Y12=Y[12], Y11A=Y[11], Y11B=Yb[11], w5A=A[5], w5B=B[5])
json.dump(out, open('scan_m1213.out.json', 'w'), indent=1)
print(json.dumps(out, indent=1)[:6000])
