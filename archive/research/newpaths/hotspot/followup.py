#!/usr/bin/env python3
"""followup.py (hotspot; research only) - checks of the hot spots found by analyze_hot.py.
1. GF(2) affine relations that hold for EVERY logged event (c1 free bits for E1 events; Y9 / w8 / e1 bits for E3).
2. Fixed regions (named here, from the discovery half of out/h_sub.bin): gain = P(region | event) / P(region | null) on
   the held-out half (thread id odd) and on the whole-class file, for every event.
3. Exact (DP) per-Y9 probability that Delta f1 is in the eps* list, and the gain curve of keeping the best Y9 values;
   the same for the R = 0 targets Delta f1 = tau ^ ror(tau, 1).
  python -B followup.py out/h_sub.bin out/h_all.bin
"""
import sys
import numpy as np
from ref import F, load, ror, rol, CM, E3L
from analyze_hot import events, K_NULL

EPS = 0x6e21be55
ETA = 0x830303CF
TAUS = [0x175020a0, 0x175060a0, 0x185020a0, 0x185060a0, 0x275020a0, 0x275060a0, 0x285020a0, 0x285060a0, 0x385020a0,
        0x385060a0, 0x675020a0, 0x675060a0, 0x685020a0, 0x685060a0]
FREE_C1 = [b for b in range(32) if not (CM >> b) & 1]


def bit(R, w, b):
    return ((R[:, F[w]] >> np.uint32(b)) & np.uint32(1)).astype(np.uint8)


def affine_relations(V, labels):
    """all (a, c) with a . x = c for every row x of V (rows of 0/1); returns list of (bits in a, c)"""
    if len(V) == 0:
        return []
    x0 = V[0].copy()
    D = (V ^ x0)
    k = V.shape[1]
    basis = {}                         # pivot -> row (python int)
    for row in D:
        r = int(''.join('1' if b else '0' for b in row[::-1]), 2) if row.any() else 0
        while r:
            p = r.bit_length() - 1
            if p in basis:
                r ^= basis[p]
            else:
                basis[p] = r
                break
    # null space of the row space: solve for a with a . row = 0 for every basis row
    piv = sorted(basis)
    rows = [basis[p] for p in piv]
    # reduce to RREF
    for i, p in enumerate(piv):
        for j in range(len(rows)):
            if j != i and (rows[j] >> p) & 1:
                rows[j] ^= rows[i]
    free = [c for c in range(k) if c not in piv]
    rels = []
    for f in free:
        a = 1 << f
        for i, p in enumerate(piv):
            if (rows[i] >> f) & 1:
                a |= 1 << p
        bits_ = [labels[c] for c in range(k) if (a >> c) & 1]
        cval = int(sum(int(x0[c]) for c in range(k) if (a >> c) & 1) % 2)
        rels.append((bits_, cval))
    return rels


def dp_y9(y9, targets):
    """exact number of h1 (out of 2^32) with Delta g1 in targets, for each y9 (vector)"""
    y9 = y9.astype(np.uint64)
    N = len(y9)
    tot = np.zeros(N)
    for T in targets:
        cnt = np.zeros((N, 4)); cnt[:, 0] = 1.0
        for i in range(32):
            x = ((y9 >> np.uint64(i)) & np.uint64(1)).astype(np.int64)
            e, t = (ETA >> i) & 1, (T >> i) & 1
            new = np.zeros_like(cnt)
            for c in (0, 1):
                for cb in (0, 1):
                    src = cnt[:, 2 * c + cb]
                    if (e ^ c ^ cb) != t:
                        continue
                    for y in (0, 1):
                        yb = y ^ e
                        nc = (x & y) | (x & c) | (y & c)
                        ncb = (x & yb) | (x & cb) | (yb & cb)
                        d = 2 * nc + ncb
                        for dv in range(4):
                            m = d == dv
                            new[m, dv] += src[m]
            cnt = new
        tot += cnt.sum(1)
    return tot / 2.0 ** 32


def regions(R):
    c11 = bit(R, 'c1', 11) ^ bit(R, 'c1', 12)
    c20 = bit(R, 'c1', 20) ^ bit(R, 'c1', 22)
    y9 = R[:, F['Y9']]
    m4 = (y9 & np.uint32(3)) == 0
    return {
        'c1[11]^c1[12]=1': c11 == 1,
        'c1[20]^c1[22]=1': c20 == 1,
        'both c1 parities': (c11 == 1) & (c20 == 1),
        'Y9 = 0 mod 4': m4,
        'Y9 = 4 mod 8': (y9 & np.uint32(7)) == 4,
        'Y9 = 4 mod 8 & w8[22]=0': ((y9 & np.uint32(7)) == 4) & (bit(R, 'w8', 22) == 0),
        'c1 parities & Y9 = 0 mod 4': (c11 == 1) & (c20 == 1) & m4,
        'Y12[16]^KY[16]=1': (bit(R, 'Y12', 16) ^ bit(R, 'KY', 16)) == 1,
        'Y12[16]^KY[16]=1 & KY low16 < 2^12': ((bit(R, 'Y12', 16) ^ bit(R, 'KY', 16)) == 1) & ((R[:, F['KY']] & np.uint32(0xF000)) == 0),
        'Y9 support (Y9=0 mod 4, Y9[16]^Y9[17]=1, Y9[24]=Y9[25])': m4 & ((bit(R, 'Y9', 16) ^ bit(R, 'Y9', 17)) == 1) & ((bit(R, 'Y9', 24) ^ bit(R, 'Y9', 25)) == 0),
        'c1 parities & Y9 support': (c11 == 1) & (c20 == 1) & m4 & ((bit(R, 'Y9', 16) ^ bit(R, 'Y9', 17)) == 1) & ((bit(R, 'Y9', 24) ^ bit(R, 'Y9', 25)) == 0),
    }


if __name__ == '__main__':
    paths = sys.argv[1:] or ['out/h_sub.bin', 'out/h_all.bin']
    for path in paths:
        R = load(path)
        EV = events(R)
        null = (R[:, 0] & K_NULL) != 0
        half = (R[:, F['tid']] & 1).astype(bool)
        print(f'===== {path}: records {len(R)}')
        print('-- 1. affine GF(2) relations holding for every logged event (all data of this file)')
        groups = {
            'c1 free bits': [('c1', b) for b in FREE_C1],
            'Y9 bits': [('Y9', b) for b in range(32)],
            'w8 bits': [('w8', b) for b in range(32)],
            'Y9 + w8 + e1 bits': [('Y9', b) for b in range(32)] + [('w8', b) for b in range(32)] + [('e1', b) for b in range(32)],
            'c1 free + Y12 + KY + w5 bits': [('c1', b) for b in FREE_C1] + [(w, b) for w in ('Y12', 'KY', 'w5') for b in range(32)],
        }
        for ename, gnames in (('listed E1 outcome', ('c1 free bits', 'c1 free + Y12 + KY + w5 bits')),
                              ('E1 outcome & rule A', ('c1 free bits',)),
                              ('listed partial E3', ('Y9 bits', 'w8 bits')),
                              ('partial E3 eps(beta*)', ('Y9 bits', 'w8 bits', 'Y9 + w8 + e1 bits')),
                              ('partial E3 & rule A', ('Y9 bits',)),
                              ('eta condition (sample)', ('c1 free bits',)),
                              ('listed tau (sample)', ('c1 free + Y12 + KY + w5 bits',))):
            m = EV[ename]
            for g in gnames:
                labels = [f'{w}[{b}]' for w, b in groups[g]]
                V = np.stack([bit(R[m], w, b) for w, b in groups[g]], axis=1) if m.sum() else np.zeros((0, len(labels)), np.uint8)
                # drop bits that are constant in the null sample (fixed by the class)
                Vn = np.stack([bit(R[null], w, b) for w, b in groups[g]], axis=1)
                var = (Vn.min(0) != Vn.max(0))
                Vv = V[:, var]
                lab = [l for l, v in zip(labels, var) if v]
                rels = affine_relations(Vv, lab)
                rtxt = '; '.join(f'{"^".join(a)} = {c}' for a, c in rels[:12]) if rels else 'none'
                print(f'   {ename} (n={int(m.sum())}) over {g} ({len(lab)} varying bits): {len(rels)} relations: {rtxt}'
                      + (' ...' if len(rels) > 12 else ''))
        print('-- 2. fixed regions: gain = P(region|event)/P(region|null); held-out half of this file (and all data)')
        RG = regions(R)
        for rname, rm in RG.items():
            f_h = rm[null & half].mean(); f_a = rm[null].mean()
            print(f'   region {rname}: fraction kept {f_a:.4f} (2^{np.log2(f_a):.2f})')
            for ename, m in EV.items():
                n_h, n_a = int((m & half).sum()), int(m.sum())
                if n_a < 5:
                    continue
                k_h, k_a = int((m & half & rm).sum()), int((m & rm).sum())
                g_h = (k_h / n_h) / f_h if n_h else float('nan')
                g_a = (k_a / n_a) / f_a
                # cluster-robust z (outer steps) of the region share among the events, all data
                ol = R[m, F['olaunch']].astype(np.int64)
                key = ((ol >> 8) << 24) | (R[m, F['tid']].astype(np.int64) << 5) | (ol & 0xFF)
                _, inv = np.unique(key, return_inverse=True)
                res_c = np.bincount(inv, weights=rm[m].astype(float) - f_a)
                zr = (k_a - n_a * f_a) / np.sqrt(max((res_c ** 2).sum(), 1e-9))
                print(f'      {ename:26s} held-out {k_h:6d}/{n_h:6d} gain x{g_h:5.2f} | all {k_a:6d}/{n_a:6d} gain x{g_a:5.2f}'
                      f' (2^{np.log2(max(g_a, 1e-9)):+.2f}, robust z {zr:+.1f})')
    print('-- 3. exact per-Y9 probability of Delta f1 in the eps* list (DP over h1), 2^15 random Y9 values')
    psis, _ = E3L[EPS]
    r0targets = sorted({t ^ ror(t, 1) for t in TAUS})
    print(f'   R = 0 targets tau ^ ror(tau,1): {len(r0targets)} values; all in the eps* psi list: {set(r0targets) <= set(psis)}')
    rng = np.random.default_rng(7)
    y9 = rng.integers(0, 2 ** 32, size=2 ** 15, dtype=np.uint64)
    for lab, tg in (('eps* psi list', sorted(psis)), ('R = 0 targets', r0targets)):
        p = dp_y9(y9, [rol(x, 12) for x in tg])
        mean = p.mean()
        srt = np.sort(p)[::-1]
        curve = ' '.join(f'1/{int(1 / q)}:x{srt[:max(1, int(q * len(srt)))].mean() / mean:.2f}' for q in (1 / 4, 1 / 8, 1 / 16, 1 / 64, 1 / 256, 1 / 1024))
        zero = (p == 0).mean()
        print(f'   {lab}: mean over Y9 2^{np.log2(mean):.3f}; Y9 with probability 0: {zero:.3f}; keep best q -> gain {curve}')
        m4 = (y9 & np.uint64(3)) == 0
        m8 = (y9 & np.uint64(7)) == 4
        print(f'      Y9 = 0 mod 4: gain x{p[m4].mean() / mean:.3f} (q 1/4); Y9 = 4 mod 8: gain x{p[m8].mean() / mean:.3f} (q 1/8)')
        sup = m4 & ((((y9 >> np.uint64(16)) ^ (y9 >> np.uint64(17))) & np.uint64(1)) == 1) & \
            ((((y9 >> np.uint64(24)) ^ (y9 >> np.uint64(25))) & np.uint64(1)) == 0)
        print(f'      4-condition support: fraction {sup.mean():.4f}; mass inside {p[sup].sum() / p.sum():.6f}; Y9 outside with p > 0:'
              f' {int(((p > 0) & ~sup).sum())}; max p 2^{np.log2(p.max()):.2f}; quantiles of p inside (50/90/99/99.9%):'
              f' {" ".join(f"2^{np.log2(max(np.quantile(p[sup], q), 1e-30)):.1f}" for q in (0.5, 0.9, 0.99, 0.999))}')
    # sampling check of the DP: 6 random Y9 values (3 in the support), 2^24 random h1 each
    print('   DP against sampling (2^24 random h1 per Y9):')
    tg = np.array([rol(x, 12) for x in r0targets], dtype=np.uint64)
    picks = list(y9[:3]) + [int(v) for v in y9[sup][np.argsort(-dp_y9(y9[sup], [int(t) for t in tg]))[:3]]]
    for v in picks:
        v = int(v)
        h1 = rng.integers(0, 2 ** 32, size=2 ** 24, dtype=np.uint64)
        g = (np.uint64(v) + h1) & np.uint64(0xFFFFFFFF)
        gb = (np.uint64(v) + (h1 ^ np.uint64(ETA))) & np.uint64(0xFFFFFFFF)
        hit = np.isin(g ^ gb, tg).mean()
        print(f'      Y9 {v:08x}: DP {dp_y9(np.array([v], dtype=np.uint64), [int(t) for t in tg])[0]:.3e}  sampled {hit:.3e}')
