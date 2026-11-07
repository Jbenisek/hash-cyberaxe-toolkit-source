'''Fresh, independent re-check of the "joint" lens claims (perspectives/joint/RESULT.md).
Own evaluator: pairs are built from (outer words, member k, cube index j) with the front-line lines (pkgCG
experiments/frontline.py, sha256 prefix 5936cfad: member, rebuild, step_ct), and BOTH blocks are compressed with the
organizer's hash-smash/verifier/blake3.py (_compress / _g, rounds=2, counter t, flags 3). R = digest words (1,3,4,6)
of A XOR B. Seeds are new (not those of perspectives/data).
usage: python fresh.py rows <n> <seed>      independent rows: rank, relations E-a/E-b, spiral identities, controls
       python fresh.py groups <n> <seed> <mode>   mode=rand: random (ow,k) groups; mode=pass: only groups whose
                                                  front-line pre-check T != 0 (they reach the joint solver)
'''

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

import sys, random, struct, time
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCG/pkg/blake3-r2/experiments'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import frontline as F
import blake3 as B

M = 0xFFFFFFFF
ETA, EPS = 0x830303CF, 0x6E21BE55
QFREE = [i for i in range(32) if not (0x0E09818B >> i & 1)]
assert len(QFREE) == 21


def ror(x, n): return ((x >> n) | (x << (32 - n))) & M if n % 32 else x
def par(x): return bin(x).count('1') & 1
def pdep(j): return sum((j >> n & 1) << i for n, i in enumerate(QFREE))


def comp_trace(words, t, n):
    'organizer _g, rounds=2; returns (cv words 0..7, state before round-2 diagonals, round-2 message words)'
    v = list(B.IV) + list(B.IV[:4]) + [t & M, t >> 32, n, 3]
    m = list(words); ystate = None; mr = None
    for r in range(2):
        for i, (a, b, c, d) in enumerate(((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                                          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))):
            if r == 1 and i == 4: ystate, mr = list(v), list(m)
            B._g(v, a, b, c, d, m[2 * i], m[2 * i + 1])
        m = [m[p] for p in B.PERMUTATION]
    return [v[i] ^ v[i + 8] for i in range(8)], ystate, mr


def halfg(a, b, c, d, x, y):
    a1 = (a + b + x) & M; d1 = ror(d ^ a1, 16); c1 = (c + d1) & M; b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return (a1, b1, c1, d1), (a2, b2, c2, d2)


def group_v(ow, k):
    e1, y = F.member(k)
    return F.rebuild(ow, y, e1), e1


def pair(v, j, full=False):
    c1 = 0x02008000 | pdep(j)
    u = F.step_ct(v, c1)
    if u['t'] == 0: return None
    wa = struct.unpack('<16I', u['A'].ljust(64, b'\0')); wb = struct.unpack('<16I', u['B'].ljust(64, b'\0'))
    t = u['t']
    if not full:
        da = B._compress(B.IV, wa, t, 55, 3, 2)[:8]; db = B._compress(B.IV, wb, t, 63, 3, 2)[:8]
        assert all(da[i] == db[i] for i in (0, 2, 5, 7))
        return tuple(da[i] ^ db[i] for i in (1, 3, 4, 6))
    da, ya, ma = comp_trace(wa, t, 55); db, yb, mb = comp_trace(wb, t, 63)
    assert da == list(B._compress(B.IV, wa, t, 55, 3, 2)[:8]) and db == list(B._compress(B.IV, wb, t, 63, 3, 2)[:8])
    assert all(da[i] == db[i] for i in (0, 2, 5, 7))
    R = tuple(da[i] ^ db[i] for i in (1, 3, 4, 6))
    # E1 = G(v1,v6,v11,v12; m10,m11), E3 = G(v3,v4,v9,v14; m14,m15) of round 2 (diagonal calls 5 and 7)
    E1 = [halfg(y[1], y[6], y[11], y[12], m[10], m[11]) for y, m in ((ya, ma), (yb, mb))]
    E3 = [halfg(y[3], y[4], y[9], y[14], m[14], m[15]) for y, m in ((ya, ma), (yb, mb))]
    d1 = [[E1[0][h][q] ^ E1[1][h][q] for q in range(4)] for h in (0, 1)]   # da db dc dd, first/second half
    d3 = [[E3[0][h][q] ^ E3[1][h][q] for q in range(4)] for h in (0, 1)]   # de df dg dh
    return R, d1, d3, c1


def affine_basis(vecs):
    'GF(2) basis (dict pivot->vec) of the differences vecs[i]^vecs[0]; returns (basis, origin)'
    o = vecs[0]; basis = {}
    for x in vecs[1:]:
        r = x ^ o
        while r:
            p = r.bit_length() - 1
            if p in basis: r ^= basis[p]
            else: basis[p] = r; break
    return basis, o


def in_span(basis, x):
    while x:
        p = x.bit_length() - 1
        if p not in basis: return False
        x ^= basis[p]
    return True


def pack(R): return R[0] | R[1] << 32 | R[2] << 64 | R[3] << 96


def rows(n, seed):
    rnd = random.Random(seed); out = []; t0 = time.time()
    ea = eb = 0; idf = [0] * 4; skipped = 0; dc1set = set(); dh1bad = 0
    vecs = []; uni = []
    hist_dc2_lo = 0
    while len(out) < n:
        ow = tuple(rnd.getrandbits(32) for _ in range(7)); k = rnd.getrandbits(19); j = rnd.getrandbits(21)
        v, e1 = group_v(ow, k)
        r = pair(v, j, full=True)
        if r is None: skipped += 1; continue
        R, d1, d3, c1 = r
        R1, R3, R4, R6 = R
        out.append(R); vecs.append(pack(R)); uni.append(rnd.getrandbits(128))
        ea += par(R3) ^ par(R6)
        eb += par(R3 >> 8) ^ (R4 >> 25 & 1) ^ par((R6 >> 1) & 0xFFFFFF)
        da1, db1, dc1, dd1 = d1[0]; da2, db2, dc2, dd2 = d1[1]
        de1, df1, dg1, dh1 = d3[0]; de2, df2, dg2, dh2 = d3[1]
        dc1set.add(dc1); dh1bad += dh1 != ETA
        # K1 = (da2, dc2, dd2, db2), K3 = (dg2, de2, df2, dh2): check R = K1 ^ K3
        assert R == (da2 ^ dg2, dc2 ^ de2, dd2 ^ df2, db2 ^ dh2)
        idf[0] += (R6 ^ ror(R3, 8) ^ ror(ETA, 8)) != (ror(dc1, 19) ^ ror(dc2 ^ ror(dc2, 1), 7))
        idf[1] += (R6 ^ ror(R3, 7)) != (ror(dc1, 19) ^ ror(ETA, 8) ^ ror(de2 ^ ror(de2, 1), 7))
        idf[2] += (R4 ^ ror(R1, 8)) != (ror(dg1, 19) ^ ror(dg2 ^ ror(dg2, 1), 7))
        idf[3] += (R4 ^ ror(R1, 7)) != (ror(da2 ^ ror(da2, 1), 7) ^ ror(dg1, 19))
        hist_dc2_lo += (dc2 & 0xFFFF) == (EPS & 0xFFFF)
    b, o = affine_basis(vecs); bu, ou = affine_basis(uni)
    h = len(vecs) // 2
    b1, o1 = affine_basis(vecs[:h]); b2, o2 = affine_basis(vecs[h:])
    print('rows', len(out), 'skipped(t=0)', skipped, 'seed %#x' % seed, 'time %.1fs' % (time.time() - t0))
    print('affine rank R: all %d  half1 %d  half2 %d ; uniform control %d' % (len(b), len(b1), len(b2), len(bu)))
    print('0 in affine hull of R:', in_span(b, o))
    print('E-a failures', ea, ' E-b failures', eb)
    print('distinct dc1 values', len(dc1set), ['%08x' % x for x in list(dc1set)[:3]], ' dh1!=eta', dh1bad)
    print('spiral identity failures U1,Q7,U3,Z7:', idf)
    print('Pr[dc2 low16 = eps low16] = %d/%d (uniform 2^-16 -> %.2f expected)' % (hist_dc2_lo, len(out), len(out) / 65536))


def frontline_T(v, e1):
    x = F.T1(v['Y9']) & F.T2(v['omega'])
    T = x & F.VMASK[F.nu_of(v['Y9'], e1, v['C2_c1'], v['C2_b1'])] if x else 0
    return x, T


def groups(n, seed, mode, npts=2048):
    rnd = random.Random(seed); t0 = time.time(); scanned = 0; res = []
    while len(res) < n:
        ow = tuple(rnd.getrandbits(32) for _ in range(7)); k = rnd.getrandbits(19)
        v, e1 = group_v(ow, k); scanned += 1
        x, T = frontline_T(v, e1)
        if mode == 'pass' and not T: continue
        js = [rnd.getrandbits(21) for _ in range(npts)]
        vecs = []
        for j in js:
            R = pair(v, j)
            if R is not None: vecs.append(pack(R))
        b, o = affine_basis(vecs)
        rank_half, _ = affine_basis(vecs[:len(vecs) // 2])
        feas = in_span(b, o)
        extra = ''
        if not feas or len(rank_half) != len(b):        # saturation check: 4x more points
            more = [pack(r) for r in (pair(v, rnd.getrandbits(21)) for _ in range(3 * npts)) if r is not None]
            b2, o2 = affine_basis(vecs + more); feas2 = in_span(b2, o2)
            extra = ' sat-check rank %d feas %d' % (len(b2), feas2)
            feas = feas2; b = b2
        res.append((len(b), feas, x, T))
        print('group %3d scanned %7d x=%02x T=%02x rank %3d (half %3d) zero_in_hull %d%s' %
              (len(res), scanned, x, T, len(b), len(rank_half), feas, extra), flush=True)
    nf = sum(r[1] for r in res)
    print('mode %s seed %#x groups %d scanned %d : zero in hull %d/%d = %.3f ; mean rank %.1f ; time %.0fs' %
          (mode, seed, len(res), scanned, nf, len(res), nf / len(res), sum(r[0] for r in res) / len(res), time.time() - t0))
    if mode == 'rand':
        for lab, sel in (('x!=0', lambda r: r[2]), ('x==0', lambda r: not r[2])):
            s = [r for r in res if sel(r)]
            if s: print('  %s: %d groups, zero in hull %d' % (lab, len(s), sum(r[1] for r in s)))


if __name__ == '__main__':
    if sys.argv[1] == 'rows': rows(int(sys.argv[2]), int(sys.argv[3], 0))
    else: groups(int(sys.argv[2]), int(sys.argv[3], 0), sys.argv[4])
