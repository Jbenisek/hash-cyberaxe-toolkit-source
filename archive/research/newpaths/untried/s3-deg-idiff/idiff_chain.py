"""Step 3: how many rounds can the internal difference be kept DETERMINISTIC (constant) inside a symmetric field by
linear conditions alone, and what is left?  For a space t + span(B) (t p-periodic):
  round r: test whether delta_r = S_r xor rot_p(S_r) is affine on t + span(B) (64 random second differences);
           if affine: rank of its linear part = number of linear conditions; restrict B to the kernel (delta_r is then
           the constant delta_r(t) on the new coset); record weights; continue with round r+1.
           if not affine: the deterministic chain stops; record where.
Then sample NSAMP random points of the final coset and of the starting space and record the weight of delta_r per round
(rounds 1-5 full 1600-bit state, round 6 the 256-bit digest), against the random-state mean.
Usage: python idiff_chain.py SEED NT NSAMP SPACES(comma)   (spaces as in idiff_degree.py, no W40)"""
import sys, json, random
import numpy as np
import symlib as S

seed, NT, NSAMP = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
spaces = sys.argv[4].split(',')
rng = random.Random(seed)
FO = json.load(open('fields_out.json'))


def space(tag):
    kind, p = (tag[:2], int(tag[2:])) if tag.startswith('Vn') else (tag[0], int(tag[1:]))
    sym = S.sym_basis(p)
    if kind == 'U':
        return p, S.lane16_for(p), sym, sym
    key = f'p{p}_' + ('native_l16' if kind == 'Vn' else 'periodic_l16')
    return p, (S.NATIVE if kind == 'Vn' else S.lane16_for(p)), [int(h, 16) for h in FO['bases'][key]], sym


def run(pts, l16):
    return {r: A for r, A in S.states(S.unpack_src(pts), l16, 6)}


def dbits(A, p, digest=False):
    L = A[:4] if digest else A
    D = [a ^ S.rotl(a, p) for a in L]
    if digest:
        return np.stack([np.unpackbits(b.view(np.uint8).reshape(-1, 8), axis=1, bitorder='little') for b in D],
                        axis=1).reshape(len(D[0]), 256)
    return S.bits_of(D)


def colpar_weight(bits1600):
    lanes = bits1600.reshape(25, 64)
    cp = lanes[0:5] ^ lanes[5:10] ^ lanes[10:15] ^ lanes[15:20] ^ lanes[20:25]
    return int(cp.sum())


def kernel_combos(vecs):
    piv = {}; ker = []
    for i, v in enumerate(vecs):
        c = 1 << i
        while v:
            b = v.bit_length() - 1
            if b in piv:
                v ^= piv[b][0]; c ^= piv[b][1]
            else:
                piv[b] = (v, c); break
        if not v:
            ker.append(c)
    return ker


def chain(p, l16, basis, sym):
    t = S.combine(rng.getrandbits(len(sym)), sym)
    B = list(basis); rows = []
    for r in range(1, 7):
        n = len(B)
        quads = []
        for _ in range(64):
            a = S.combine(rng.getrandbits(n), B) if n else 0
            b = S.combine(rng.getrandbits(n), B) if n else 0
            quads += [t ^ a ^ b, t ^ a, t ^ b, t]
        st = run([t] + [t ^ b for b in B] + quads, l16)[r]
        db = dbits(st, p)
        q = db[1 + n:].reshape(64, 4, 1600)
        nonaff = int(np.count_nonzero((q[:, 0] ^ q[:, 1] ^ q[:, 2] ^ q[:, 3]).any(axis=1)))
        row = {'r': r, 'dim_in': n, 'w_delta_t': int(db[0].sum()), 'w_colpar_delta_t': colpar_weight(db[0]),
               'nonaffine_2nd_diffs_of_64': nonaff}
        if nonaff:
            rows.append(row); break
        lin = db[1:1 + n] ^ db[0]
        vecs = [int.from_bytes(np.packbits(lin[i], bitorder='little').tobytes(), 'little') for i in range(n)]
        K = kernel_combos(vecs)
        row.update({'conditions': n - len(K), 'dim_out': len(K)})
        rows.append(row)
        B = [S.combine(c, B) for c in K]
    return t, B, rows


def sample(p, l16, t, B, sym, n):
    pts = []
    for _ in range(n):
        if B is None:
            pts.append(S.combine(rng.getrandbits(len(sym)), sym))
        else:
            pts.append(t ^ (S.combine(rng.getrandbits(len(B)), B) if B else 0))
    st = run(pts, l16)
    rec = {}
    for r in range(1, 7):
        d = dbits(st[r], p, digest=(r == 6))
        w = d.sum(axis=1)
        p1 = d.mean(axis=0)                                   # per-bit Pr[delta bit = 1]
        rec[r] = {'w_mean': round(float(w.mean()), 1), 'w_min': int(w.min()),
                  'distinct_delta': int(len({row.tobytes() for row in np.packbits(d, axis=1)})),
                  'bits_const0': int((p1 == 0).sum()), 'bits_const1': int((p1 == 1).sum()),
                  'bits_P0_ge_0.6_nonconst': int(((p1 <= 0.4) & (p1 > 0)).sum()),
                  'max_P0_nonconst': round(float(1 - p1[p1 > 0].min()), 4) if (p1 > 0).any() else None}
    return rec


for tag in spaces:
    p, l16, basis, sym = space(tag)
    best = None
    for _ in range(NT):
        t, B, rows = chain(p, l16, basis, sym)
        key = (len(rows), rows[-1].get('dim_out', rows[-1]['dim_in']))
        if best is None or key > best[0]:
            best = (key, t, B, rows)
        print(json.dumps({'space': tag, 'p': p, 'dim': len(basis), 'chain': rows}), flush=True)
    _, t, B, rows = best
    print(json.dumps({'space': tag, 'best_chain_final_dim': len(B),
                      'sample_on_final_coset': sample(p, l16, t, B, sym, NSAMP),
                      'sample_on_start_field_coset': sample(p, l16, t, basis, sym, NSAMP),
                      'sample_on_whole_symmetric_U': sample(p, l16, t, None, sym, NSAMP),
                      'random_state_mean_w': {'r1-5 (1600 bits)': 800, 'r6 (256-bit digest)': 128}}), flush=True)
