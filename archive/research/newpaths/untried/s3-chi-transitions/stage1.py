"""Stage 1: every chi1 transition of every seed word; relaxed chi2; chi3-input K/N sets.
Seeds: the 1,749 linstruct3 cycle words (theta1 kernel, stopped chi1 output in theta2 kernel; 6 or 8 bits).
Per word v: A1 = P(v) (chi1 input, exact). chi1 output B1(tau) = base + sum tau_i g_i over the product of the row
affine spaces U(delta_row) = ALL compatible output differences (= every choice of neighbour constants).
A2(tau) = P(B1(tau)). chi2 relaxed (common.chi_relax_KN): K = chi3-input bits active for every chi2 choice,
N = bits never active. 'kp' = chi1 output in the theta2 CP kernel (no theta2 spread).
6-bit words: all 4^6 chi1 choices enumerated. 8-bit words: kp choices (solved exactly) + 4,096 random non-kp choices.
Writes stage1_kp.npz (all kp variants: word id, tau, A2, K, N) and stage1_stats.json."""
import time, json, random
import numpy as np
from common import *

t0 = time.time()
W = load_cycles()
print('words', len(W), 'weights', {w: sum(1 for x in W if len(x) == w) for w in (6, 8)}, flush=True)
rng = random.Random(7)


def word_setup(bits):
    v = bits_to_lanes(bits)
    assert not colpar(v).any(), 'theta1 kernel'
    A1 = P(v)
    base = np.zeros((1, 25), dtype=U64); gens = []
    nrows = 0; multirows = 0
    tb = ls.tobits(A1)[0]
    for y in range(5):
        for z in range(64):
            d = 0
            for x in range(5):
                if tb[64 * (x + 5 * y) + z]: d |= 1 << x
            if not d: continue
            nrows += 1; multirows += bin(d).count('1') > 1
            b, gs = Uspace(d)
            for x in range(5):
                if (b >> x) & 1: base[0, x + 5 * y] |= U64(1) << U64(z)
            for g in gs:
                G = np.zeros((1, 25), dtype=U64)
                for x in range(5):
                    if (g >> x) & 1: G[0, x + 5 * y] |= U64(1) << U64(z)
                gens.append(G)
    return v, A1, base, gens, nrows, multirows


def span_table(P0, PG):
    arr = P0.copy()
    for g in PG:
        arr = np.concatenate([arr, arr ^ g], axis=0)
    return arr


def kp_affine(base, gens):
    """tau solving colpar(base + sum tau_i g_i) = 0: particular solution + kernel basis (as int bitmasks)."""
    k = len(gens)
    cb = colpar(base)[0]; cg = [colpar(g)[0] for g in gens]
    toint = lambda c: int.from_bytes(np.ascontiguousarray(c).view(np.uint8).tobytes(), 'little')
    rows = [(toint(cg[i]), 1 << i) for i in range(k)]   # column-parity vector, tau combination
    target = toint(cb)
    piv = {}
    kern = []
    for (c, t) in rows:
        while c:
            p = c.bit_length() - 1
            if p in piv: c ^= piv[p][0]; t ^= piv[p][1]
            else: piv[p] = (c, t); break
        if c == 0: kern.append(t)
    c = target; t = 0
    while c:
        p = c.bit_length() - 1
        if p not in piv: return None, kern
        c ^= piv[p][0]; t ^= piv[p][1]
    return t, kern


stats = []; kp_rows = []
for wi, bits in enumerate(W):
    v, A1, base, gens, nrows, multirows = word_setup(bits)
    k = len(gens)
    P0 = P(base); PG = [P(g) for g in gens]
    # stop variant: chi1 identity (base == A1 when all rows single-bit), chi2 identity
    A2s = P(A1); w3stop = int(popc(P(A2s))[0])
    part, kern = kp_affine(base, gens)
    # kp variants
    taus = []
    if part is not None:
        sp = [0]
        for kv in kern: sp = sp + [s ^ kv for s in sp]
        taus = [part ^ s for s in sp]
    taus = np.array(taus, dtype=np.int64)
    def A2_of(tau_arr):
        out = np.repeat(P0, len(tau_arr), axis=0)
        for i in range(k):
            sel = ((tau_arr >> i) & 1).astype(bool)
            out[sel] ^= PG[i]
        return out
    rec = {'w': wi, 'wt': len(bits), 'k_chi1_gens': k, 'chi1_rows': nrows, 'chi1_multi_rows': multirows,
           'w3_stop': w3stop, 'n_kp': int(len(taus))}
    if len(taus):
        A2k = A2_of(taus); Kk, Nk = chi_relax_KN(A2k)
        pk = popc(Kk)
        rec.update({'kp_minK': int(pk.min()), 'kp_maxK': int(pk.max()), 'kp_minA2': int(popc(A2k).min())})
        kp_rows.append((np.full(len(taus), wi), taus, A2k, Kk, Nk))
    # non-kp statistics
    if k <= 12:
        allt = np.arange(1 << k, dtype=np.int64)
    else:
        allt = np.array([rng.getrandbits(k) for _ in range(4096)], dtype=np.int64)
    A2a = A2_of(allt)
    cpa = np.repeat(colpar(base), len(allt), axis=0)
    for i in range(k):
        sel = ((allt >> i) & 1).astype(bool)
        cpa[sel] ^= colpar(gens[i])[0]
    iskp = ~cpa.any(axis=1)
    Ka, Na = chi_relax_KN(A2a)
    pk = popc(Ka)
    nk = pk[~iskp]
    rec.update({'n_enum': int(len(allt)), 'nonkp_minK': int(nk.min()) if len(nk) else None,
                'nonkp_medK': float(np.median(nk)) if len(nk) else None,
                'nonkp_minA2': int(popc(A2a[~iskp]).min()) if len(nk) else None})
    stats.append(rec)
    if wi % 200 == 0:
        print(wi, rec, round(time.time() - t0, 1), flush=True)

wid = np.concatenate([r[0] for r in kp_rows]); tau = np.concatenate([r[1] for r in kp_rows])
A2 = np.concatenate([r[2] for r in kp_rows]); K = np.concatenate([r[3] for r in kp_rows]); N = np.concatenate([r[4] for r in kp_rows])
np.savez(HERE + 'stage1_kp.npz', wid=wid, tau=tau, A2=A2, K=K, N=N)
json.dump({'words': [list(b) for b in W], 'stats': stats}, open(HERE + 'stage1_stats.json', 'w'))
summ = {
    'words': len(W), 'kp_variants_total': int(len(wid)),
    'w3_stop_min': min(s['w3_stop'] for s in stats),
    'kp_minK_min': min(s.get('kp_minK', 10**9) for s in stats),
    'kp_minK_hist': np.bincount([s['kp_minK'] for s in stats if 'kp_minK' in s]).nonzero()[0][:12].tolist(),
    'nonkp_minK_min': min(s['nonkp_minK'] for s in stats if s['nonkp_minK'] is not None),
    'nonkp_medK_median': float(np.median([s['nonkp_medK'] for s in stats if s['nonkp_medK'] is not None])),
    'n_kp_hist': {int(a): int(b) for a, b in zip(*np.unique([s['n_kp'] for s in stats], return_counts=True))},
    'multi_row_words': sum(1 for s in stats if s['chi1_multi_rows']),
    'secs': round(time.time() - t0, 1)}
print(json.dumps(summ), flush=True)
