"""SHA3-256 r6, combo "low degree x connector": can the 2-round-affine field W40 carry a FIXED pair
difference through rounds 1-2 (and the chi3 conditions be paid in field dimensions), so that FES can enumerate
pairs of a differential trail cheaply?

For a coset t + W40 and a pair difference Delta (in the 320-bit source, embedded like W40: lanes 0-4 and 10-14,
lane 16 = 0x86<<56; or a general message-lane difference), the pair-difference function
    delta_r(w) = S_r(t + w) xor S_r(t + Delta + w),   w in W40
is affine in w for r <= 2 (both cosets are 2-round affine), and for r = 3 on the sub-field where delta_2 is
constant (derivative of a quadratic map).  Per stage we report:
  r=1,2: dim of the sub-field W'_r on which delta_r is constant (= 40 - rank of its linear part)
  r=2  : weight of delta_2 and its column-parity weight at theta3 (odd columns -> theta3 spread)
  r=3  : rank of delta_3's linear part on W'_2 (= linear chi3 conditions), dim W'_3
  r=4..6: sampled weight of delta_r on W'_3 (or W'_2) and the max per-bit bias.
Imports research/sha3r6/lowdegree/cube_degree.py (W40, organizer round function via SOLCLOUD_12 keccak).
Labels: every printed number is COMPUTED.  Usage: python sha3_ldconn.py SEED NCOSETS
"""

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

import sys, json, random, time
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree'))
import cube_degree as cd

U = np.uint64
MASK = (1 << 64) - 1
W = cd.W  # 40 x 320-bit ints


def states(srcs, extra=None, nr=6):
    """srcs: list of 320-bit ints (source). extra: optional dict lane->list of uint64 XOR differences per point.
    Returns list over rounds 1..nr of 25-lane arrays (each np.uint64 array of len n)."""
    n = len(srcs)
    u = [np.array([(s >> (64 * k)) & MASK for s in srcs], dtype=U) for k in range(5)]
    A = cd.lanes(u)
    A = [a.copy() for a in A]
    if extra:
        for lane, vals in extra.items():
            A[lane] = A[lane] ^ np.array(vals, dtype=U)
    out = []
    for i in range(nr):
        A = cd.rnd(A, i)
        out.append([a.copy() for a in A])
    return out


def bits1600(A, j):
    """state (list of 25 arrays) at point j -> python int with 1600 bits (lane k at bits 64k..)"""
    v = 0
    for k in range(25):
        v |= int(A[k][j]) << (64 * k)
    return v


def gf2_rank_kernel(vecs, nbits):
    """vecs: list of python ints (rows). Returns (rank, kernel basis as list of combination masks over rows)."""
    rows = list(vecs)
    m = len(rows)
    comb = [1 << i for i in range(m)]
    piv = {}
    kernel = []
    for i in range(m):
        v, c = rows[i], comb[i]
        while v:
            b = v.bit_length() - 1
            if b in piv:
                pv, pc = piv[b]
                v ^= pv; c ^= pc
            else:
                piv[b] = (v, c)
                break
        if v == 0:
            kernel.append(c)
    return len(piv), kernel


def colpar_weight(v):
    """column parity weight of a 1600-bit state (lane x+5y at bits 64(x+5y)..)"""
    lanes = [(v >> (64 * k)) & MASK for k in range(25)]
    w = 0
    for x in range(5):
        c = 0
        for y in range(5):
            c ^= lanes[x + 5 * y]
        w += bin(c).count('1')
    return w


def theta(v):
    lanes = [(v >> (64 * k)) & MASK for k in range(25)]
    C = [0] * 5
    for x in range(5):
        for y in range(5):
            C[x] ^= lanes[x + 5 * y]
    rot1 = lambda a: ((a << 1) | (a >> 63)) & MASK
    D = [C[(x - 1) % 5] ^ rot1(C[(x + 1) % 5]) for x in range(5)]
    out = 0
    for x in range(5):
        for y in range(5):
            out |= (lanes[x + 5 * y] ^ D[x]) << (64 * (x + 5 * y))
    return out


def popc(v):
    return bin(v).count('1')


def analyse(t, dsrc, dextra, basis, rng, nsamp=256):
    """t: 320-bit coset rep; dsrc: 320-bit source difference; dextra: dict lane->uint64 difference outside source.
    basis: list of 320-bit directions (field). Returns per-stage dict."""
    res = {}
    n = len(basis)
    # points: 0, w_i (i<n); for both sides
    pts = [t] + [t ^ w for w in basis]
    ptsD = [p ^ dsrc for p in pts]
    ex = None
    if dextra:
        ex = {lane: [val] * len(ptsD) for lane, val in dextra.items()}
    S = states(pts, None, 3)
    SD = states(ptsD, ex, 3)
    cur = list(range(n))  # current field basis as combos over 'basis' indices: start with unit vectors
    field = [1 << i for i in range(n)]  # masks over basis
    for r in (1, 2):
        A, B = S[r - 1], SD[r - 1]
        d0 = bits1600(A, 0) ^ bits1600(B, 0)
        L = [(bits1600(A, i + 1) ^ bits1600(B, i + 1)) ^ d0 for i in range(n)]
        # restrict to current field: vectors for field elements = XOR of L over mask
        Lf = []
        for m in field:
            v = 0; mm = m; idx = 0
            while mm:
                if mm & 1: v ^= L[idx]
                mm >>= 1; idx += 1
            Lf.append(v)
        rk, ker = gf2_rank_kernel(Lf, 1600)
        newfield = []
        for c in ker:
            m = 0; cc = c; idx = 0
            while cc:
                if cc & 1: m ^= field[idx]
                cc >>= 1; idx += 1
            newfield.append(m)
        field = newfield
        res['r%d_rank' % r] = rk
        res['r%d_dim' % r] = len(field)
        res['r%d_delta_weight_at0' % r] = popc(d0)
        if r == 2:
            res['r2_delta_colparity_weight'] = colpar_weight(d0)
            res['r2_theta3_out_weight'] = popc(theta(d0))
        if not field:
            break
    if len(field) == 0:
        res['r3_rank'] = None; res['r3_dim'] = 0
        return res
    # verify delta_2 constant on the sub-field (random combos)
    dirs2 = []
    for m in field:
        v = 0; mm = m; idx = 0
        while mm:
            if mm & 1: v ^= basis[idx]
            mm >>= 1; idx += 1
        dirs2.append(v)
    chk = []
    for _ in range(16):
        c = rng.getrandbits(len(dirs2)) if dirs2 else 0
        v = 0
        for j, dv in enumerate(dirs2):
            if c >> j & 1: v ^= dv
        chk.append(v)
    P = [t ^ v for v in chk]
    S2 = states(P, None, 2)[1]
    S2D = states([p ^ dsrc for p in P], ({lane: [val] * len(P) for lane, val in dextra.items()} if dextra else None), 2)[1]
    dset = set(bits1600(S2, j) ^ bits1600(S2D, j) for j in range(len(P)))
    res['r2_constant_check_distinct'] = len(dset)
    # r = 3 on field W'_2: linear part of delta_3
    pts3 = [t] + [t ^ v for v in dirs2]
    A3 = states(pts3, None, 3)[2]
    B3 = states([p ^ dsrc for p in pts3], ({lane: [val] * len(pts3) for lane, val in dextra.items()} if dextra else None), 3)[2]
    d30 = bits1600(A3, 0) ^ bits1600(B3, 0)
    L3 = [(bits1600(A3, i + 1) ^ bits1600(B3, i + 1)) ^ d30 for i in range(len(dirs2))]
    rk3, ker3 = gf2_rank_kernel(L3, 1600)
    res['r3_rank'] = rk3
    res['r3_dim'] = len(ker3)
    res['r3_delta_weight_at0'] = popc(d30)
    # samples on W'_3 if nonzero else W'_2 for rounds 4..6
    dirs3 = []
    for c in ker3:
        v = 0
        for j, dv in enumerate(dirs2):
            if c >> j & 1: v ^= dv
        dirs3.append(v)
    use = dirs3 if dirs3 else dirs2
    res['sample_field'] = 'W3' if dirs3 else 'W2'
    P = []
    for _ in range(nsamp):
        c = rng.getrandbits(len(use)) if use else 0
        v = 0
        for j, dv in enumerate(use):
            if c >> j & 1: v ^= dv
        P.append(t ^ v)
    SA = states(P, None, 6)
    SB = states([p ^ dsrc for p in P], ({lane: [val] * len(P) for lane, val in dextra.items()} if dextra else None), 6)
    for r in (3, 4, 5, 6):
        A, B = SA[r - 1], SB[r - 1]
        lanes = 25 if r < 6 else 4
        ws = []
        ones = np.zeros(64 * lanes)
        for j in range(len(P)):
            v = 0
            for k in range(lanes):
                v |= (int(A[k][j]) ^ int(B[k][j])) << (64 * k)
            ws.append(popc(v))
            # per-bit counts
            for k in range(lanes):
                x = int(A[k][j]) ^ int(B[k][j])
                if x:
                    for bpos in range(64):
                        if x >> bpos & 1: ones[64 * k + bpos] += 1
        p1 = ones / len(P)
        res['r%d_mean_weight' % r] = round(float(np.mean(ws)), 1)
        res['r%d_const0_bits' % r] = int(np.sum(p1 == 0))
        res['r%d_max_bias' % r] = round(float(np.max(np.abs(p1 - 0.5))), 3)
    return res


def source_bit(b):
    return 1 << b


def copy_cp_map():
    """linear map: source difference (320 bits) -> chi1-input difference (after theta1=id on kernel, rho, pi),
    then its column parity (320 bits). Returns list of 320 python ints (images of unit vectors), each 320-bit CP."""
    imgs = []
    for b in range(320):
        lane = b // 64; z = b % 64
        st = 0
        for base in (0, 10):
            st |= 1 << (64 * (base + lane) + z)
        # rho, pi (theta1 acts as identity: column parity of the copy pair is zero)
        out = 0
        for k in range(25):
            word = (st >> (64 * k)) & MASK
            if not word: continue
            x, y = k % 5, k // 5
            r = cd.RHO[k] % 64
            word = ((word << r) | (word >> (64 - r))) & MASK if r else word
            nx, ny = y, (2 * x + 3 * y) % 5
            out |= word << (64 * (nx + 5 * ny))
        # column parity of out (identity chi1)
        cp = 0
        lanes = [(out >> (64 * k)) & MASK for k in range(25)]
        for x in range(5):
            c = 0
            for y in range(5):
                c ^= lanes[x + 5 * y]
            cp |= c << (64 * x)
        imgs.append((out, cp))
    return imgs


LB_BEST_COMBO = {}


def lee_brickell(rows, nbits, rng, iters=1500, key=None):
    """approximate minimum weight of a nonzero codeword in span(rows) (rows: python ints over nbits).
    Random column permutation + systematic form; check single rows and pairs of rows.  The weight returned is the
    lightest word FOUND (an upper bound on the true minimum).  The combination mask (over rows) of the best word is
    stored in LB_BEST_COMBO[key]."""
    best = None
    for _ in range(iters):
        perm = list(range(nbits)); rng.shuffle(perm)
        R = []
        for r in rows:
            v = 0
            for newpos, oldpos in enumerate(perm):
                if r >> oldpos & 1: v |= 1 << newpos
            R.append(v)
        piv = []  # (row, combo)
        for i, v in enumerate(R):
            c = 1 << i
            for p, pc in piv:
                lb = p & -p
                if v & lb: v ^= p; c ^= pc
            if v:
                lb = v & -v
                piv = [(p ^ v, pc ^ c) if p & lb else (p, pc) for p, pc in piv]
                piv.append((v, c))
        for i, (a, ac) in enumerate(piv):
            w = popc(a)
            if best is None or w < best:
                best = w; LB_BEST_COMBO[key] = ac
            for b, bc in piv[i + 1:]:
                w2 = popc(a ^ b)
                if w2 < best:
                    best = w2; LB_BEST_COMBO[key] = ac ^ bc
    return best


def field_delta2_minweights(t, rng, iters=300):
    """for Delta in W40: delta_2 = L_t(Delta). Returns approx min column-parity weight and min theta3-output
    weight of delta_2 over nonzero Delta in W40 (Lee-Brickell, single rows + pairs)."""
    pts = [t] + [t ^ w for w in W]
    S2 = states(pts, None, 2)[1]
    base = bits1600(S2, 0)
    L = [bits1600(S2, i + 1) ^ base for i in range(40)]
    def cpvec(v):
        lanes = [(v >> (64 * k)) & MASK for k in range(25)]
        out = 0
        for x in range(5):
            c = 0
            for y in range(5): c ^= lanes[x + 5 * y]
            out |= c << (64 * x)
        return out
    cps = [cpvec(v) for v in L]
    ths = [theta(v) for v in L]
    return (lee_brickell(cps, 320, rng, iters, key=('cp', t)), lee_brickell(ths, 1600, rng, max(20, iters // 15), key=('th', t)),
            min(popc(c) for c in cps), min(popc(v) for v in L))


def main():
    seed = int(sys.argv[1]); ncos = int(sys.argv[2])
    rng = random.Random(seed)
    t0 = time.time()
    for i in range(min(ncos, 3)):
        t = rng.getrandbits(320)
        cpmin, thmin, cpbasis, wbasis = field_delta2_minweights(t, rng)
        print(json.dumps({'field_delta2_lightest_found_colparity_weight': cpmin, 'field_delta2_lightest_found_theta3out_weight': thmin,
                          'basis_min_colparity': cpbasis, 'basis_min_delta2_weight': wbasis,
                          'sec': round(time.time() - t0, 1)}), flush=True)
        # run the per-round pipeline on the lightest Delta found (both criteria), on this coset
        for crit in ('cp', 'th'):
            combo = LB_BEST_COMBO.get((crit, t))
            if not combo: continue
            d = 0
            for j in range(40):
                if combo >> j & 1: d ^= W[j]
            r = analyse(t, d, None, W, rng, nsamp=128)
            r['family'] = 'inW_lightest_' + crit
            r['delta_src_weight'] = popc(d)
            r['sec'] = round(time.time() - t0, 1)
            print(json.dumps(r), flush=True)
    print(json.dumps({'W_rank': cd.rank(W), 'selfcheck_sponge': cd.selfcheck(rng)}), flush=True)
    # theta2-kernel sub-space of source differences (identity chi1 transition)
    imgs = copy_cp_map()
    rk, ker = gf2_rank_kernel([cp for (_, cp) in imgs], 320)
    kvecs = []
    for c in ker:
        v = 0
        for j in range(320):
            if c >> j & 1: v ^= 1 << j
        kvecs.append(v)
    print(json.dumps({'source_diff_space': 320, 'theta2_kernel_dim_identity_chi1': len(kvecs),
                      'min_weight_basis_vec': min((popc(v) for v in kvecs), default=None)}), flush=True)
    families = []
    for i in range(ncos):
        t = rng.getrandbits(320)
        # (a) Delta in W (random element)
        c = rng.getrandbits(40) or 1
        dW = 0
        for j in range(40):
            if c >> j & 1: dW ^= W[j]
        families.append(('inW', t, dW, None))
        # (b) single source bits
        for _ in range(2):
            families.append(('srcbit', t, source_bit(rng.randrange(320)), None))
        # (c) theta2-kernel source differences (if any)
        if kvecs:
            cc = rng.getrandbits(len(kvecs)) or 1
            v = 0
            for j, kv in enumerate(kvecs):
                if cc >> j & 1: v ^= kv
            families.append(('th2ker', t, v, None))
            families.append(('th2ker_basis', t, kvecs[rng.randrange(len(kvecs))], None))
        # (d) random dense source difference
        families.append(('random', t, rng.getrandbits(320), None))
        # (e) one bit outside the source lanes (lane 5..9 / 15, message bits), source diff 0
        lane = rng.choice([5, 6, 7, 8, 9, 15])
        families.append(('outside1bit', t, 0, {lane: 1 << rng.randrange(64)}))
    for name, t, d, ex in families:
        r = analyse(t, d, ex, W, rng, nsamp=128)
        r['family'] = name
        r['delta_src_weight'] = popc(d)
        r['sec'] = round(time.time() - t0, 1)
        print(json.dumps(r), flush=True)


if __name__ == '__main__':
    main()
