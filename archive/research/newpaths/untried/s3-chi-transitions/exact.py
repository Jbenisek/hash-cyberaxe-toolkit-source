"""Exact check of candidate triangles from stage2 (three seed words + one kernel-preserving chi1 variant each).
Pattern level (z3): chi1 transitions fixed by the variants (consistency of shared neighbour constants checked);
chi2: one COMMON set of row constants for all three directions (free Bools for every bit of every active chi2 row);
output forms g[i] = f[i] + (c[i+1]+1) f[i+2] + c[i+2] f[i+1] + [f[i+1]=f[i+2]!=0] f[i+2] (forms in GF(2)^3);
chi3 forms h = P(g) (affine in the constants); per-row test: every adjacent pair has h=0, h'=0 or h=h'.
Native level: conditions as in linstruct3/ls3.py (chi1 neighbour constants = linear conditions; chi2 constants
linearised by helper conditions), forced values honoured, patterns recomputed from the imposed values, chi3 rule
re-checked, every condition row must vanish on every direction.
Usage: python exact.py MAXSECS"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, time, json, random
import numpy as np
import z3
from common import *
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/linstruct3'))
import ls3

NBp, NBm, NBm2 = ls.NBp, ls.NBm, ls.NBm2
PEQ = [np.nonzero(ls3.Pmat[q])[0] for q in range(1600)]      # chi3-input bits fed by chi2-output bit q


def word_setup(bits):   # identical to stage1.word_setup (same generator order)
    v = bits_to_lanes(bits); A1 = P(v)
    base = np.zeros((1, 25), dtype=U64); gens = []
    tb = ls.tobits(A1)[0]
    for y in range(5):
        for z in range(64):
            d = 0
            for x in range(5):
                if tb[64 * (x + 5 * y) + z]: d |= 1 << x
            if not d: continue
            b, gs = Uspace(d)
            for x in range(5):
                if (b >> x) & 1: base[0, x + 5 * y] |= U64(1) << U64(z)
            for g in gs:
                G = np.zeros((1, 25), dtype=U64)
                for x in range(5):
                    if (g >> x) & 1: G[0, x + 5 * y] |= U64(1) << U64(z)
                gens.append(G)
    return A1, base, gens


def chi1_choice(bits, tau):
    """Active chi1-input bits, chosen chi1 output pattern, and the neighbour-constant preferences it implies."""
    A1, base, gens = word_setup(bits)
    B1 = base.copy()
    for i, g in enumerate(gens):
        if (tau >> i) & 1: B1 ^= g
    a1 = ls.tobits(A1)[0]; b1 = ls.tobits(B1)[0]
    pref = {}
    for p in np.nonzero(a1)[0]:
        p = int(p)
        pref[int(NBp[p])] = int(b1[NBm[p]])          # adds x-1  <=> a_{x+1} = 1
        pref[int(NBm[p])] = 1 - int(b1[NBm2[p]])     # adds x-2  <=> a_{x-1} = 0
    return a1, b1, pref


def pattern_z3(dirs_a2, timeout_ms=20000):
    """dirs_a2: list of three (1600,) bool chi2-input patterns. Returns (status, {pos: const}) ."""
    nd = len(dirs_a2)
    f = np.zeros(1600, dtype=np.int64)
    for k, a in enumerate(dirs_a2): f |= a.astype(np.int64) << k
    act = np.nonzero(f)[0]
    rows = sorted({(int(ls.Y[p]), int(ls.Z[p])) for p in act})
    pos_var = {}
    for (y, z) in rows:
        for x in range(5): pos_var[64 * (x + 5 * y) + z] = len(pos_var)
    # affine forms per chi2-output position: list of nd (mask, const)
    g = {}
    for q in pos_var:
        q1, q2 = int(NBp[q]), int(NBp[NBp[q]])
        fi, f1, f2 = int(f[q]), int(f[q1]), int(f[q2])
        eq = 1 if (f1 == f2 and f1 != 0) else 0
        frm = []
        for k in range(nd):
            b0, b1, b2 = (fi >> k) & 1, (f1 >> k) & 1, (f2 >> k) & 1
            const = b0 ^ b2 ^ (eq & b2)
            mask = (b2 << pos_var[q1]) ^ (b1 << pos_var[q2])
            frm.append((mask, const))
        g[q] = frm
    h = {}
    for q, frm in g.items():
        if all(m == 0 and c == 0 for (m, c) in frm): continue
        for j in PEQ[q]:
            j = int(j); cur = h.get(j, [(0, 0)] * nd)
            h[j] = [(cur[k][0] ^ frm[k][0], cur[k][1] ^ frm[k][1]) for k in range(nd)]
    V = [z3.Bool('c%d' % i) for i in range(len(pos_var))]
    def zexp(mc):
        m, c = mc
        terms = [V[i] for i in range(m.bit_length()) if (m >> i) & 1]
        if not terms: return z3.BoolVal(bool(c))
        e = terms[0]
        for t in terms[1:]: e = z3.Xor(e, t)
        return z3.Not(e) if c else e
    s = z3.Solver(); s.set('timeout', timeout_ms)
    ncons = 0
    for j, hj in h.items():
        j2 = int(NBp[j])
        if j2 not in h: continue
        hk = h[j2]
        if all(m == 0 for (m, c) in hj) and all(m == 0 for (m, c) in hk):
            u = [c for (m, c) in hj]; w = [c for (m, c) in hk]
            if any(u) and any(w) and u != w: return 'unsat-const', None
            continue
        U = [zexp(t) for t in hj]; Wv = [zexp(t) for t in hk]
        s.add(z3.Or(z3.Not(z3.Or(*U)), z3.Not(z3.Or(*Wv)), z3.And(*[U[k] == Wv[k] for k in range(nd)])))
        ncons += 1
    r = s.check()
    if r != z3.sat: return str(r), None
    mdl = s.model()
    return 'sat', {q: int(z3.is_true(mdl.eval(V[i], model_completion=True))) for q, i in pos_var.items()}


def chi1out_affine2(st, k):
    """ls3.chi1out_affine with one extension: if a_{k+1} is active, fix a_{k+2} (helper) instead."""
    k1, k2 = int(NBp[k]), int(NBp[NBp[k]])
    r, c = ls.ROW[k], int(ls.PADC[k])
    if k1 in st.c1:
        if st.c1[k1] == 0: r ^= ls.ROW[k2]; c ^= int(ls.PADC[k2])
        return r, c
    if k2 in st.c1:
        if st.c1[k2] == 1: r ^= ls.ROW[k1]; c ^= int(ls.PADC[k1]) ^ 1
        return r, c
    if not st.G1[k1]:
        ls3.add1(st, k1, 1); return chi1out_affine2(st, k)
    if not st.G1[k2]:
        ls3.add1(st, k2, 0); return chi1out_affine2(st, k)
    return None


def add2b(st, q, pref):
    if q in st.c2: return st.c2[q]
    R, C = 0, 0
    for k in ls3.KQ[q]:
        o = chi1out_affine2(st, int(k))
        if o is None: return None
        R ^= o[0]; C ^= o[1]
    val = st.el.add(R, pref ^ C) ^ C
    st.c2[q] = val; st.rows.append((R, val ^ C)); return val


def native(bits_list, pref1_list, pref2):
    """Build the condition system for all directions at once; return (ok, info, st, Vints)."""
    st = ls3.St()
    A1s = []
    for bits in bits_list:
        v = np.zeros(1600, bool); v[list(bits)] = True
        A1s.append(ls.Pb(v)[0]); st.V.append(v)
    G1 = np.zeros(1600, bool)
    for a in A1s: G1 |= a
    st.G1 = G1
    mism1 = 0
    for pr in pref1_list:
        for q, val in sorted(pr.items()):
            if G1[q]: return False, 'chi1 neighbour is active', st, None
            got = ls3.add1(st, q, val)
            mism1 += got != val
    # actual chi1 outputs
    A2s = []
    for a in A1s:
        h = a.copy()
        for p in np.nonzero(a)[0]:
            if st.c1[int(NBm[p])] == 0: h[NBm2[p]] ^= True
            if st.c1[int(NBp[p])] == 1: h[NBm[p]] ^= True
        A2s.append(ls.Pb(h)[0])
    G2 = np.zeros(1600, bool)
    for a in A2s: G2 |= a
    # chi2 conditions: the two row neighbours of every active chi2-input bit (the constants the transitions use)
    mism2 = 0
    for p in np.nonzero(G2)[0]:
        for q in (int(NBm[p]), int(NBp[p])):
            if G2[q] or q in st.c2: continue
            want = pref2.get(q, 0)
            got = add2b(st, q, want)
            if got is None: return False, 'chi2 linearisation impossible', st, None
            mism2 += got != want
    # actual chi2 outputs per direction with the joint rule (forms), then chi3 test
    f = np.zeros(1600, dtype=np.int64)
    for k, a in enumerate(A2s): f |= a.astype(np.int64) << k
    nd = len(A2s)
    gout = np.zeros(1600, dtype=np.int64)
    for p in range(1600):
        f1, f2 = int(f[NBp[p]]), int(f[NBp[NBp[p]]])
        if not (f[p] or f1 or f2): continue
        if f1 and f2 and f1 != f2: return False, 'chi2 row test', st, None
        c1 = st.c2.get(int(NBp[p]), 0); c2v = st.c2.get(int(NBp[NBp[p]]), 0)
        if f1 and f2 and f1 == f2: return False, 'adjacent equal-form chi2 pair (not modelled natively)', st, None
        val = int(f[p]) ^ ((c1 ^ 1) * f2) ^ (c2v * f1)
        gout[p] = val
    E3 = []
    for k in range(nd):
        e = ((gout >> k) & 1).astype(bool)
        E3.append(ls.Pb(e)[0])
    Em = np.array(E3); nz = Em.any(axis=0)
    if (nz & nz[NBp] & (Em != Em[:, NBp]).any(axis=0)).any():
        return False, 'chi3 rule fails natively (mism1=%d mism2=%d)' % (mism1, mism2), st, None
    Vi = [ls.vec_int(v) for v in st.V]
    for (R, _) in st.rows:
        for vi in Vi:
            if bin(R & vi).count('1') & 1: return False, 'condition row not invariant on a direction', st, None
    gr = ls.Elim()
    for x in Vi: gr.add(x, 0)
    if len(gr.piv) != nd: return False, 'directions dependent', st, None
    st.E3 = E3; st.A2s = A2s
    return True, {'mism1': mism1, 'mism2': mism2, 'chi3_bits_union': int(nz.sum()),
                  'chi3_bits_each': [int(e.sum()) for e in E3]}, st, Vi


if __name__ == '__main__':
    maxsecs = float(sys.argv[1]) if len(sys.argv) > 1 else 240
    t0 = time.time()
    S = json.load(open(HERE + 'stage1_stats.json')); words = [tuple(w) for w in S['words']]
    d = np.load(HERE + 'stage1_kp.npz'); tau = d['tau']
    T = json.load(open(HERE + 'stage2.json'))['vtri']
    rng = random.Random(5); rng.shuffle(T)
    res = {'tested': 0, 'chi1_const_clash': 0, 'z3': {}, 'native': {}, 'found': []}
    for (a, b, c, ia, ib, ic) in T:
        if time.time() - t0 > maxsecs: break
        res['tested'] += 1
        ch = [chi1_choice(words[w], int(tau[i])) for w, i in ((a, ia), (b, ib), (c, ic))]
        merged = {}; clash = False
        for (_, _, pr) in ch:
            for q, v in pr.items():
                if merged.get(q, v) != v: clash = True
                merged[q] = v
        if clash: res['chi1_const_clash'] += 1; continue
        A2s = [ls.Pb(b1)[0] for (_, b1, _) in ch]
        stt, sol = pattern_z3(A2s)
        res['z3'][stt] = res['z3'].get(stt, 0) + 1
        if stt != 'sat': continue
        ok, info, st, Vi = native([words[a], words[b], words[c]], [pr for (_, _, pr) in ch], sol)
        key = 'ok' if ok else info
        res['native'][key] = res['native'].get(key, 0) + 1
        if ok:
            res['found'].append({'words': [a, b, c], 'variants': [ia, ib, ic], 'info': info,
                                 'cond_rank': len(ls3.rref_rows(st.rows))})
            json.dump({'words': [list(words[w]) for w in (a, b, c)], 'pref1': [{str(k): v for k, v in pr.items()} for (_, _, pr) in ch],
                       'pref2': {str(k): v for k, v in sol.items()}, 'rows': [[hex(R), v] for (R, v) in st.rows]},
                      open(HERE + 'found_rank3_%d.json' % len(res['found']), 'w'))
            if len(res['found']) >= 3: break
        if res['tested'] % 50 == 0:
            print(json.dumps({k: res[k] for k in ('tested', 'chi1_const_clash', 'z3', 'native')}), round(time.time() - t0, 1), flush=True)
    res['secs'] = round(time.time() - t0, 1)
    print(json.dumps(res), flush=True)
    json.dump(res, open(HERE + 'exact_result.json', 'w'))
