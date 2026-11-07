"""s3-deg-idiff scout: shared code for z-periodic (symmetric) sub-fields of the SHA3-256 r6 message families.

Embedding = research/sha3r6/lowdegree/cube_degree.py: 320-bit source u0..u4 in lanes 0-4 AND 10-14 (column parities
constant -> round 0 affine on all of U320), lane 16 constant, all other lanes 0, zero capacity; message = first 135
bytes of lanes 0..16, so byte 135 = 0x86 is the organizer's own 0x06|0x80 padding byte.
Lane 16: native 0x86<<56, or its p-periodic extension (0x86 at the top byte of every p-bit block; bytes 128..134 are
ordinary message bytes) so that the whole 1600-bit input is p-periodic in z.
Round function: organizer's round (cube_degree.rnd, vectorised); end-to-end check against
hash-smash/verifier/keccak.py sha3_256(rounds=6)."""

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

import sys, importlib.util, random
import numpy as np

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree'))
import cube_degree as cd                     # W40 (cd.W), vectorised round cd.rnd, cd.rot, cd.RHO, cd.RC

_spec = importlib.util.spec_from_file_location('orgkec', _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/keccak.py'))
okec = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(okec)

U = np.uint64
MASK = (1 << 64) - 1
NATIVE = 0x86 << 56


def lane16_for(p):
    """p-periodic lane 16 whose top byte is the padding byte 0x86 (p in 8,16,32); None/64 -> native."""
    if p in (None, 64):
        return NATIVE
    assert p in (8, 16, 32), 'p<=4: 0x86 is not 4-periodic, no symmetric single-block input exists'
    v = 0
    for k in range(64 // p):
        v |= 0x86 << (p * k + p - 8)
    return v


def lanes(u, l16):
    n = len(u[0]); z = np.zeros(n, U)
    A = [z] * 25
    for k in range(5):
        A[k] = u[k]; A[10 + k] = u[k]
    A[16] = np.full(n, U(l16))
    return A


def unpack_src(ts):
    """list of 320-bit ints -> 5 lane arrays"""
    return [np.array([(t >> (64 * k)) & MASK for t in ts], dtype=U) for k in range(5)]


def prechi(A, i):
    """theta/rho/pi of round i (no chi, no iota); returns the 25 chi-input lanes B[x+5y]"""
    C = [A[x] ^ A[x + 5] ^ A[x + 10] ^ A[x + 15] ^ A[x + 20] for x in range(5)]
    D = [C[(x - 1) % 5] ^ cd.rot(C[(x + 1) % 5], 1) for x in range(5)]
    B = [None] * 25
    for y in range(5):
        for x in range(5):
            B[y + 5 * ((2 * x + 3 * y) % 5)] = cd.rot(A[x + 5 * y] ^ D[x], cd.RHO[x + 5 * y])
    return B


def states(u, l16, upto=6):
    """yield (r, A) for r = 1..upto: full 25-lane state after round r (1-indexed: after organizer round r-1)"""
    A = lanes(u, l16)
    for i in range(upto):
        A = cd.rnd(A, i)
        yield i + 1, A


def rotl(v, r):
    return cd.rot(v, r)


def msg_bytes(t, l16):
    L = [0] * 25
    for k in range(5):
        L[k] = (t >> (64 * k)) & MASK; L[10 + k] = L[k]
    L[16] = l16
    return b''.join(l.to_bytes(8, 'little') for l in L[:17])[:135]


def selfcheck(l16, rng, npts=8):
    """vectorised round function on this embedding == organizer sha3_256(rounds=6) on random sources"""
    ts = [rng.getrandbits(320) for _ in range(npts)]
    A = None
    for r, A in states(unpack_src(ts), l16, 6):
        pass
    ok = True
    for j, t in enumerate(ts):
        dig = b''.join(int(A[k][j]).to_bytes(8, 'little') for k in range(4))
        ok &= okec.sha3_256(msg_bytes(t, l16), rounds=6) == dig
    return ok


def bits_of(B):
    """25 lane arrays (n,) -> uint8 bit matrix [n, 1600], position = 64*lane + z"""
    return np.stack([np.unpackbits(b.view(np.uint8).reshape(-1, 8), axis=1, bitorder='little') for b in B],
                    axis=1).reshape(len(B[0]), 1600)


def affine_map(l16, stage):
    """Affine map U320 -> 1600 bits. stage='r1': state after round 1; 'chi1in': chi input of round 2 (theta/rho/pi
    of organizer round 1 applied to the round-1 output). Returns (const_int, [form_int per position]) with forms over
    the 320 source bits (bit i of the form <-> source bit i). Valid only because round 0 is affine on U320."""
    pts = [0] + [1 << i for i in range(320)]
    A = cd.rnd(lanes(unpack_src(pts), l16), 0)
    if stage == 'chi1in':
        A = prechi(A, 1)
    bm = bits_of(A)                                   # [321, 1600]
    lin = bm[1:] ^ bm[0]                              # [320, 1600]
    packed = np.packbits(lin.T, axis=1, bitorder='little')   # [1600, 40]
    forms = [int.from_bytes(packed[pos].tobytes(), 'little') for pos in range(1600)]
    c = int.from_bytes(np.packbits(bm[0], bitorder='little').tobytes(), 'little')
    return c, forms


def round0_affine_check(l16, rng, ntrip=400):
    """second differences of the state after round 1 over random a,b in U320 at random base points: must be 0"""
    bad = 0
    ts = []
    for _ in range(ntrip):
        t, a, b = rng.getrandbits(320), rng.getrandbits(320), rng.getrandbits(320)
        ts += [t, t ^ a, t ^ b, t ^ a ^ b]
    A = cd.rnd(lanes(unpack_src(ts), l16), 0)
    for L in A:
        v = L.reshape(-1, 4)
        bad += int(np.count_nonzero(v[:, 0] ^ v[:, 1] ^ v[:, 2] ^ v[:, 3]))
    return bad


def sym_basis(p):
    """basis of the p-periodic part of U320: e_{x,j} = all bits 64x + j + kp; index 5? -> x*p + j"""
    B = []
    for x in range(5):
        for j in range(p):
            v = 0
            for k in range(64 // p):
                v |= 1 << (64 * x + j + k * p)
            B.append(v)
    return B


def restrict(f, basis):
    r = 0
    for i, b in enumerate(basis):
        if (f & b).bit_count() & 1:
            r |= 1 << i
    return r


def chi_pairs(forms_r):
    """non-trivial adjacent pairs (f,g) of chi input forms: product f*g is affine on the subspace iff f=0, g=0 or f=g"""
    P = set()
    for y in range(5):
        for z in range(64):
            for x in range(5):
                f = forms_r[64 * ((x + 1) % 5 + 5 * y) + z]
                g = forms_r[64 * ((x + 2) % 5 + 5 * y) + z]
                if f and g and f != g:
                    P.add((min(f, g), max(f, g)))
    return P


# ---------------- GF(2) linear algebra on python ints ----------------
def rank(vs):
    piv = {}; rk = 0
    for v in vs:
        while v:
            b = v.bit_length() - 1
            if b in piv:
                v ^= piv[b]
            else:
                piv[b] = v; rk += 1; break
    return rk


def span_basis(vs):
    piv = {}
    for v in vs:
        while v:
            b = v.bit_length() - 1
            if b in piv:
                v ^= piv[b]
            else:
                piv[b] = v; break
    return list(piv.values())


def annihilator(Q, N):
    """basis of {v in GF(2)^N : <q,v> = 0 for all q in Q}"""
    # row-reduce Q to RREF
    piv = {}
    for q in Q:
        for b, w in piv.items():
            if q >> b & 1:
                q ^= w
        if q:
            b = q.bit_length() - 1
            for c in list(piv):
                if piv[c] >> b & 1:
                    piv[c] ^= q
            piv[b] = q
    free = [i for i in range(N) if i not in piv]
    out = []
    for f in free:
        v = 1 << f
        for b, w in piv.items():
            if w >> f & 1:
                v |= 1 << b
        out.append(v)
    return out


def intersect(Abasis, Bbasis, N):
    """basis of span(A) cap span(B) in GF(2)^N via annihilators"""
    QA = annihilator(Abasis, N); QB = annihilator(Bbasis, N)
    return annihilator(QA + QB, N)


def combine(coef, basis):
    v = 0
    i = 0
    while coef:
        if coef & 1:
            v ^= basis[i]
        coef >>= 1; i += 1
    return v


def rot_src(t, r):
    """rotate each of the 5 source lanes of a 320-bit source by r"""
    out = 0
    for k in range(5):
        L = (t >> (64 * k)) & MASK
        L = ((L << r) | (L >> (64 - r))) & MASK if r % 64 else L
        out |= L << (64 * k)
    return out


# ---------------- greedy minimum "hitting subspace" ----------------
def hitting_greedy(pairs, rng, slack=0):
    """Find a small subspace Q (list of ints) of the dual such that every pair (f,g) has f, g or f^g in span(Q).
    Then V = annihilator(Q) is a subspace on which every chi product f*g is affine (per-row test).
    Greedy maximum coverage, random tie-break among candidates within `slack` of the best count.
    Pair values are kept as canonical representatives modulo span(Q) (pivot = leading bit)."""
    live = list(pairs)
    Q = []
    while True:
        cnt = {}
        nxt = []
        for rf, rg in live:
            if rf == 0 or rg == 0 or rf == rg:
                continue
            nxt.append((rf, rg))
            for c in (rf, rg, rf ^ rg):
                cnt[c] = cnt.get(c, 0) + 1
        live = nxt
        if not live:
            break
        best = max(cnt.values())
        cands = [c for c, k in cnt.items() if k >= best - slack]
        w = rng.choice(cands)
        b = w.bit_length() - 1
        live = [((rf ^ w) if rf >> b & 1 else rf, (rg ^ w) if rg >> b & 1 else rg) for rf, rg in live]
        Q.append(w)
    return Q


def check_pairs_on(pairs, Vcoef):
    """count pairs whose restriction to span(Vcoef) is not dependent (should be 0)"""
    bad = 0
    for f, g in pairs:
        rf = sum(((f & v).bit_count() & 1) << i for i, v in enumerate(Vcoef))
        rg = sum(((g & v).bit_count() & 1) << i for i, v in enumerate(Vcoef))
        if rf and rg and rf != rg:
            bad += 1
    return bad
