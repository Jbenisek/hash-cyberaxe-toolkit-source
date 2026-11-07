import random, json, time, sys
import numpy as np
from b3e0 import *
out = {}
t0 = time.time()
out['validation'] = validate()
rng = random.Random(20261012)

def r1_pair(rng):
    X = [rng.getrandbits(32) for _ in range(16)]
    X[3], X[7], X[11], X[15] = X3, X7, X11, X15
    w = [rng.getrandbits(32) for _ in range(16)]
    w[4], w[13], w[14], w[15] = W4, W13, 0, 0
    wp = list(w); wp[4] = W4P; wp[5] = (w[5] + W4 - W4P) & M
    m1 = [w[i] for i in P]; m1p = [wp[i] for i in P]
    return X, w, wp, m1, m1p

def r1_trace(X, m1):
    tr = {}
    v = list(X)
    for j, (a, b, c, d) in enumerate(CALLS):
        x, y = m1[2 * j], m1[2 * j + 1]
        r = G(v[a], v[b], v[c], v[d], x, y)
        tr[j] = (v[a], v[b], v[c], v[d], x, y, r)
        v[a], v[b], v[c], v[d] = r['a2'], r['b2'], r['c2'], r['d2']
    return v, tr

# ---------- E1: clean reachable round-1 bases, Lemma H check, E0 absorption family ----------
N = 20000
bad_Y = bad_E0 = bad_fold = 0
fam_ok = fam_n = fam_B = fam_C = rel_dD = 0
for _ in range(N):
    X, w, wp, m1, m1p = r1_pair(rng)
    Z, tr = r1_trace(X, m1); Zp, trp = r1_trace(X, m1p)
    Yd = set()
    for j in range(4):
        a, b, c, d = CALLS[j]
        r = tr[j][6]; rp = trp[j][6]
        for pos, key in ((a, 'a2'), (b, 'b2'), (c, 'c2'), (d, 'd2')):
            if r[key] != rp[key]: Yd.add(pos)
    if Yd - {3, 11}: bad_Y += 1
    if tr[4][:6] != trp[4][:6]: bad_E0 += 1
    if not all(((Z[i] ^ Z[i + 8]) == (Zp[i] ^ Zp[i + 8])) for i in (0, 2, 5, 7)): bad_fold += 1
    A, B, C, D, x, y, r = tr[4]
    for _k in range(5):
        xp, yp = rng.getrandbits(32), rng.getrandbits(32)
        iv = Ginv(r['a2'], r['b2'], r['c2'], r['d2'], xp, yp)
        a1p = (r['a2'] - iv['b1'] - yp) & M
        Dp = iv['rd'] ^ a1p
        Ap = (a1p - iv['B'] - xp) & M
        rr = G(Ap, iv['B'], iv['C'], Dp, xp, yp)
        fam_n += 1
        fam_ok += (rr['a2'], rr['b2'], rr['c2'], rr['d2']) == (r['a2'], r['b2'], r['c2'], r['d2'])
        fam_B += iv['B'] == B; fam_C += iv['C'] == C
        rel_dD += (D ^ Dp) == (r['a1'] ^ a1p)
okrel = 0; nrel = 20000
for _ in range(nrel):
    X, w, wp, m1, m1p = r1_pair(rng)
    Z, tr = r1_trace(X, m1)
    A, B, C, D, x, y, r = tr[4]
    a1p = rng.getrandbits(32); xp = rng.getrandbits(32)
    Ap = (a1p - B - xp) & M
    Dp = D ^ r['a1'] ^ a1p
    yp = (y + r['a1'] - a1p) & M
    rr = G(Ap, B, C, Dp, xp, yp)
    okrel += (rr['a2'], rr['b2'], rr['c2'], rr['d2']) == (r['a2'], r['b2'], r['c2'], r['d2'])
out['E1_clean_bases'] = dict(n=N, Y_diff_outside_3_11=bad_Y, E0_inputs_differ=bad_E0, fold_0_2_5_7_unequal=bad_fold)
out['E1_family'] = dict(preimage_trials=fam_n, outputs_equal=fam_ok, B_prime_eq_B=fam_B, C_prime_eq_C=fam_C, dD_eq_da1=rel_dD,
                        constructive_trials=nrel, constructive_outputs_equal=okrel,
                        size_per_base='2^64 (x,y free; A,D determined; B,C forced equal)')

# ---------- E1c: message-only difference at E0 (state identical) ----------
cnt_random = {k: 0 for k in range(5)}
cnt_target = {t: {k: 0 for k in range(5)} for t in ('a2', 'd2', 'c2', 'b2')}
mo_n = 0
for _ in range(3000):
    X, w, wp, m1, m1p = r1_pair(rng)
    Z, tr = r1_trace(X, m1)
    A, B, C, D, x, y, r = tr[4]
    for _k in range(20):
        xp = rng.getrandbits(32)
        if xp == x: continue
        yp = rng.getrandbits(32); rr = G(A, B, C, D, xp, yp)
        k = sum(rr[o] == r[o] for o in ('a2', 'b2', 'c2', 'd2')); cnt_random[k] += 1
        a1p = (A + B + xp) & M; d1p = ror(D ^ a1p, 16); c1p = (C + d1p) & M; b1p = ror(B ^ c1p, 12)
        for t in ('a2', 'd2', 'c2', 'b2'):
            if t == 'a2': a2n = r['a2']
            elif t == 'd2': a2n = d1p ^ rol(r['d2'], 8)
            elif t == 'c2': a2n = d1p ^ rol((r['c2'] - c1p) & M, 8)
            else:
                c2n = b1p ^ rol(r['b2'], 7); a2n = d1p ^ rol((c2n - c1p) & M, 8)
            ypp = (a2n - a1p - b1p) & M
            rr = G(A, B, C, D, xp, ypp)
            assert rr[t] == r[t]
            k = sum(rr[o] == r[o] for o in ('a2', 'b2', 'c2', 'd2')); cnt_target[t][k] += 1
        mo_n += 1
out['E1c_message_only_E0'] = dict(trials=mo_n, random_y_equal_outputs_hist=cnt_random, targeted_y_equal_outputs_hist=cnt_target)

# ---------- E2: activation closure (full 2-round pair, generic words) ----------
def full_pair(w, wp, tlo, tlop, n, np_, flags=11):
    tr, trp = {}, {}
    v, o = compress(IV, w, tlo, 0, n, flags, 2, tr)
    vp, op = compress(IV, wp, tlop, 0, np_, flags, 2, trp)
    act = [NAMES[i] for i in range(16) if tr[i] != trp[i]]
    return act, v, vp, o, op
def base_pair(rng):
    w = [rng.getrandbits(32) for _ in range(16)]
    w[14] = w[15] = 0
    w[13] &= 0x00ffffff
    wp = list(w)
    wp[4] = (((K + w[4]) ^ 8) - K) & M; wp[5] = (w[5] + w[4] - wp[4]) & M
    return w, wp
scen = {}
def run_scen(name, fn, trials):
    cnt = {}; xs = []; ys = []; folds = 0; Rs = []; early = 0
    for _ in range(trials):
        w, wp, tlo, tlop, n, np_ = fn(rng)
        act, v, vp, o, op = full_pair(w, wp, tlo, tlop, n, np_)
        for a in act: cnt[a] = cnt.get(a, 0) + 1
        v1, _ = compress(IV, w, tlo, 0, n, 11, 1); v1p, _ = compress(IV, wp, tlop, 0, np_, 11, 1)
        xs.append(sum(a != b for a, b in zip(v1, v1p)))
        ys.append(len(act))
        folds += all(o[i] == op[i] for i in (0, 2, 5, 7))
        Rs.append(sum(o[i] != op[i] for i in (1, 3, 4, 6)))
        early += sum(1 for a in act if a in NAMES[:11])
    scen[name] = dict(trials=trials, active_freq={k: round(v / trials, 3) for k, v in sorted(cnt.items(), key=lambda kv: NAMES.index(kv[0]))},
                      mean_active_calls=round(sum(ys) / trials, 2), mean_active_in_K_D_C0_C2=round(early / trials, 2),
                      mean_X_words_differ=round(sum(xs) / trials, 2),
                      fold_0_2_5_7_equal_freq=folds / trials, mean_R_words_differ_of4=round(sum(Rs) / trials, 2))
def mk_base(extra=None):
    def f(rng):
        w, wp = base_pair(rng)
        if extra: extra(rng, w, wp)
        return w, wp, 0, 0, 55, 63
    return f
run_scen('baseline_len55_63_w4w5_only(unpinned X: Y7,Y15 not pinned here)', mk_base(), 400)
for k in (0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12):
    def ex(rng, w, wp, k=k): wp[k] = (wp[k] ^ (1 << rng.randrange(32))) & M
    run_scen('baseline+dw%d_onebit' % k, mk_base(ex), 200)
def ex_pair(rng, w, wp):
    d = rng.getrandbits(32) | 1
    wp[1] = (w[1] + d) & M; wp[11] = (w[11] - d) & M
run_scen('baseline+E0_absorbing_msg_pair(dw1=+d,dw11=-d)', mk_base(ex_pair), 200)
def ex_w1(rng, w, wp): wp[1] = (w[1] + (rng.getrandbits(32) | 1)) & M
run_scen('baseline+dw1_only', mk_base(ex_w1), 200)
def ex_w11(rng, w, wp): wp[11] = (w[11] + (rng.getrandbits(32) | 1)) & M
run_scen('baseline+dw11_only', mk_base(ex_w11), 200)
def mk_k0(rng):
    w, wp = base_pair(rng)
    d = rng.getrandbits(32) | 1
    wp[1] = (w[1] + d) & M; wp[11] = (w[11] - d) & M
    wp[0] = (w[0] - d) & M
    a1 = (IV[0] + IV[4] + w[0]) & M; a1p = (IV[0] + IV[4] + wp[0]) & M
    return w, wp, 0, a1 ^ a1p, 55, 63
run_scen('baseline+E0_msg_pair+K0_counter_absorb(dw0=-d,dt=a1^a1p)', mk_k0, 200)
kk = 0
for _ in range(200):
    w, wp, tlo, tlop, n, np_ = mk_k0(rng)
    r = G(IV[0], IV[4], IV[0], tlo, w[0], w[1]); rp = G(IV[0], IV[4], IV[0], tlop, wp[0], wp[1])
    kk += (r['a2'], r['b2'], r['c2'], r['d2']) == (rp['a2'], rp['b2'], rp['c2'], rp['d2'])
scen['K0_counter_absorb_check'] = dict(trials=200, K0_outputs_equal=kk)
out['E2_activation_closure'] = scen

# ---------- E3: cross cancellation E0 vs E2 (event-level alternative), numpy ----------
def ror_(v, n): return (v >> np.uint32(n)) | (v << np.uint32(32 - n))
def vG(A, B, C, D, x, y):
    a1 = A + B + x; d1 = ror_(D ^ a1, 16); c1 = C + d1; b1 = ror_(B ^ c1, 12)
    a2 = a1 + b1 + y; d2 = ror_(d1 ^ a2, 8); c2 = c1 + d2; b2 = ror_(b1 ^ c2, 7)
    return a2, b2, c2, d2
def u32(v): return np.uint32(v)
NN = 1 << 22
matches = {}
nrng = np.random.default_rng(7)
for tt in range(3):
    X, w, wp, m1, m1p = r1_pair(rng)
    Z, tr = r1_trace(X, m1)
    A, B, C, D, x, y, r = tr[4]
    A2, B2, C2, D2, x2, y2, r2 = tr[6]
    xs0 = nrng.integers(0, 1 << 32, NN, dtype=np.uint32)
    ys0 = nrng.integers(0, 1 << 32, NN, dtype=np.uint32)
    xs2 = nrng.integers(0, 1 << 32, NN, dtype=np.uint32)
    with np.errstate(over='ignore'):
        e0 = vG(u32(A), u32(B), u32(C), u32(D), xs0, ys0)
        e2 = vG(u32(A2), u32(B2), u32(C2), u32(D2), xs2, u32(y2))
    d0 = [e0[i] ^ u32([r['a2'], r['b2'], r['c2'], r['d2']][i]) for i in range(4)]
    d2_ = [e2[i] ^ u32([r2['a2'], r2['b2'], r2['c2'], r2['d2']][i]) for i in range(4)]
    pairs = {'Z0~Z8': (d0[0], d2_[2]), 'Z5~Z13': (d0[1], d2_[3]), 'Z10~Z2': (d0[2], d2_[0]), 'Z15~Z7': (d0[3], d2_[1])}
    for nm, (u, v) in pairs.items():
        ku, cu = np.unique(u, return_counts=True); kv, cv = np.unique(v, return_counts=True)
        com, iu, iv_ = np.intersect1d(ku, kv, return_indices=True)
        matches.setdefault(nm, []).append(int((cu[iu].astype(np.int64) * cv[iv_].astype(np.int64)).sum()))
    key0 = (d0[0].astype(np.uint64) << np.uint64(32)) | d0[1].astype(np.uint64)
    key2 = (d2_[2].astype(np.uint64) << np.uint64(32)) | d2_[3].astype(np.uint64)
    ku, cu = np.unique(key0, return_counts=True); kv, cv = np.unique(key2, return_counts=True)
    com, iu, iv_ = np.intersect1d(ku, kv, return_indices=True)
    matches.setdefault('Z0~Z8 and Z5~Z13', []).append(int((cu[iu].astype(np.int64) * cv[iv_].astype(np.int64)).sum()))
out['E3_cross_cancel'] = dict(N_E0=NN, N_E2=NN, expected_per_single_word_pair=NN * NN / 2 ** 32, expected_two_word=NN * NN / 2 ** 64,
                              observed_3_bases=matches,
                              note="E0 varies (w1,w11) with state fixed (2^64 space); E2 varies w9 only (w14=0 pinned, state fixed); 4 cross-equalities are 128 bits vs 2^96 freedom, expected 2^-32 per base")
out['elapsed_s'] = round(time.time() - t0, 1)
json.dump(out, open('results.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
