"""U1 real-field experiments (Pallas). Single process, exact big-int. Run: python u1_real.py > u1_real_output.txt"""

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

import sys, random, time, itertools
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
from poseidon_ref import P, RC, MDS, mds_apply, round_full, round_partial, hash_reduced, schedule, CAPACITY
T0 = time.time()
hx = lambda n: hex(n % P)
d = pow(5, -1, P - 1)
inv = lambda x: pow(x, P - 2, P)

def matinv(M):
    n = 3; A = [list(M[i]) + [1 if i == j else 0 for j in range(n)] for i in range(n)]
    for c in range(n):
        piv = next(r for r in range(c, n) if A[r][c] % P)
        A[c], A[piv] = A[piv], A[c]
        iv = inv(A[c][c]); A[c] = [x * iv % P for x in A[c]]
        for r in range(n):
            if r != c and A[r][c]:
                f = A[r][c]; A[r] = [(x - f * y) % P for x, y in zip(A[r], A[c])]
    return [row[n:] for row in A]
MI = matinv(MDS)
n_row = MI[2]
col = lambda j: [MDS[i][j] for i in range(3)]
I = next(pow(g, (P - 1) // 4, P) for g in range(2, 50) if pow(pow(g, (P - 1) // 4, P), 2, P) == P - 1)
FIX = {'0': 0, '1': 1, '-1': P - 1, 'i': I, '-i': (-I) % P}
c0 = RC[0]; c1 = RC[1]
print('d =', hex(d), 'bits', d.bit_length(), 'popcount', bin(d).count('1'))
print('i =', hx(I))

def H_from_state(s, r):
    for idx in schedule(r)[1:]:
        s = round_full(s, idx) if (idx < 4 or idx >= 60) else round_partial(s, idx)
    return s[0]
K = pow((CAPACITY + c0[2]) % P, 5, P)
def root5(x): return pow(x, d, P)
def to_AB(nk, rho): return pow((nk + c0[0]) % P, 5, P), pow((rho + c0[1]) % P, 5, P)
def planestate(A, B, K=K):
    return mds_apply([A, B, K])

print('\n=== Q1: X2 on real inputs ===')
rng = random.Random(20261012)
fails = 0; cnt = 0
inputs = [(rng.randrange(P), rng.randrange(P)) for _ in range(1000)]
edge = [0, 1, P - 1, 2, I, (-I) % P, (-c0[0]) % P, (-c0[1]) % P, (1 - c0[0]) % P, (1 - c0[1]) % P, 1 << 65, P - 2]
inputs += [(x, y) for x in edge for y in edge]
nplane = 0; ninv = 0
for (nk, rho) in inputs:
    A, B = to_AB(nk, rho)
    s0 = round_full([nk, rho, CAPACITY], 0)
    if s0 != planestate(A, B): fails += 1
    if sum(n_row[j] * s0[j] for j in range(3)) % P == K: nplane += 1
    if (root5(A) - c0[0]) % P == nk and (root5(B) - c0[1]) % P == rho: ninv += 1
    for r in (1, 2):
        cnt += 1
        if hash_reduced(nk, rho, r) != H_from_state(planestate(A, B), r): fails += 1
print('inputs:', len(inputs), '(1000 random + %d edge pairs)' % (len(edge) ** 2), '; hash checks', cnt, '; failures', fails)
print('round-0 state == M*(A,B,K) and n.s==K on', nplane, 'of', len(inputs), '; fifth-root inverse returned (nk,rho) on', ninv, 'of', len(inputs))
print('OBSERVED (this script, Q1)')

print('\n=== Q2: the plane P0 ===')
print('n = row 2 of M^-1:'); [print('  n%d = %s' % (j, hx(n_row[j]))) for j in range(3)]
print('K = (2^65+c02)^5 =', hx(K), '; 2^65+c02 =', hx((CAPACITY + c0[2]) % P))
print('plane: n0*s0 + n1*s1 + n2*s2 = K   (s = state after R0.M)')
nn = [x * inv(n_row[2]) % P for x in n_row]
print('normalised by n2: n0/n2 =', hx(nn[0]), ' n1/n2 =', hx(nn[1]), ' K/n2 =', hx(K * inv(n_row[2])), '  (s2 = K/n2 - (n0/n2) s0 - (n1/n2) s1)')
for j in range(3): print('column M_.,%d (axis %s):' % (j, ['A->nk', 'B->rho', 'K->capacity'][j]), [hx(x) for x in col(j)])
print('point at (A,B)=(0,0): K*M_.,2 =', [hx(K * x) for x in col(2)])
print('n.M_.,0, n.M_.,1, n.M_.,2 =', [sum(n_row[i] * MDS[i][j] for i in range(3)) % P for j in range(3)], '(expect 0,0,1)')
print('\ncapacity variants (cap enters only via cap+c02, PROVED by the definition):')
caps = [('2^65 (real)', CAPACITY), ('0', 0), ('1', 1), ('-1', P - 1)]
for nm, v in FIX.items(): caps.append(('cap+c02 = %s (S-box fixed point)' % nm, (v - c0[2]) % P))
Kstar = sum(n_row[j] * (-c1[j]) for j in range(3)) % P
capstar = (root5(Kstar) - c0[2]) % P
for nm, cap in caps:
    Kc = pow((cap + c0[2]) % P, 5, P)
    shift = [((Kc - K) * x) % P for x in col(2)]
    st = round_full([5, 7, cap], 0); ok = (sum(n_row[j] * st[j] for j in range(3)) % P == Kc)
    print(' cap=%-34s cap_val=%s K=%s  n.s==K on test pt: %s ; through origin: %s' % (nm, hx(cap) if cap > 1 << 70 else cap, hx(Kc), ok, Kc == 0))
print('capacity for which the plane contains the point s=-c1 (all three R1.S inputs zero): K* = n.(-c1) =', hx(Kstar), ' cap* =', hx(capstar), ' bits', capstar.bit_length(), '(real cap = 2^65, so not reachable; DERIVED)')
print('n.(-c1) - K =', hx(Kstar - K), '(nonzero => real plane does not contain -c1)')
print('what stays the same for all capacities: normal n, both axis directions; only the offset K (a 1-parameter family of PARALLEL planes translated along M_.,2).')

print('\n=== Q4: S-box special inputs at round 0 ===')
for nm, v in FIX.items():
    print(' a=%-3s -> nk=%s | rho=%s | capacity value cap=%s' % (nm, hx(v - c0[0]), hx(v - c0[1]), hx(v - c0[2])))
print(' all values reduced mod p, hence canonical (< p): True')
print(' real lane-2 input 2^65+c02 =', hx(CAPACITY + c0[2]), ' in {0,+-1,+-i}?', (CAPACITY + c0[2]) % P in FIX.values())

print('\n=== Q5 (real part): degree-drop directions, exact degrees on lines ===')
def degree_of(f, nmax):
    vals = [f(t) for t in range(nmax + 3)]
    for k in range(len(vals)):
        if all(v == 0 for v in vals): return -1 if k == 0 else k - 1
        if all(v == vals[0] for v in vals) and vals[0] != 0: return k
        vals = [(vals[j + 1] - vals[j]) % P for j in range(len(vals) - 1)]
    return None
def lane_deg_profile(u, v, a, b, rounds_to):
    out = []
    def state(t, upto):
        s = [(a + u * t) % P, (b + v * t) % P, CAPACITY]
        for idx in range(0, upto + 1):
            s = round_full(s, idx) if idx < 4 else round_partial(s, idx)
        return s
    for upto in range(rounds_to + 1):
        bound = 5 ** (upto + 1)
        pts_ = [state(t, upto) for t in range(bound + 3)]
        degs = []
        for lane in range(3):
            vals = [p_[lane] for p_ in pts_]
            deg = None
            for k in range(len(vals)):
                if all(x == vals[0] for x in vals): deg = k if vals[0] != 0 or k == 0 else -1; break
                vals = [(vals[j + 1] - vals[j]) % P for j in range(len(vals) - 1)]
            degs.append(deg)
        out.append(degs)
    return out
dirs = []
for i in range(3):
    ui = pow((-MDS[i][1] * inv(MDS[i][0])) % P, d, P)
    dirs.append(ui)
    print(' lane %d drop direction u/v = %s ; check M_i0 u^5 + M_i1 = %d' % (i, hx(ui), (MDS[i][0] * pow(ui, 5, P) + MDS[i][1]) % P))
print(' three directions distinct:', len(set(dirs)) == 3)
a0, b0 = rng.randrange(P), rng.randrange(P)
print(' degrees per lane after each M (rows R0..R3), generic direction (u,v)=(1,3):')
for k, row in enumerate(lane_deg_profile(1, 3, a0, b0, 3)): print('   after R%d.M' % k, row)
for i in range(3):
    print(' drop direction of lane %d:' % i)
    for k, row in enumerate(lane_deg_profile(dirs[i], 1, a0, b0, 3)): print('   after R%d.M' % k, row)
for (u, v, nm) in [(1, 0, 'pure nk (1,0)'), (0, 1, 'pure rho (0,1)')]:
    print(' direction', nm, lane_deg_profile(u, v, a0, b0, 1))
print('(degrees are exact: finite differences over F_p, valid because degree < p)')

print('\n=== Q6: cost of x^(1/5) = x^d ===')
def exp_binary(x, e, ctr):
    bits = bin(e)[2:]; r = x
    for b in bits[1:]:
        r = r * r % P; ctr[0] += 1
        if b == '1': r = r * x % P; ctr[1] += 1
    return r
def exp_window(x, e, k, ctr):
    if k == 1: return exp_binary(x, e, ctr)
    x2 = x * x % P; ctr[0] += 1
    tab = {1: x}
    for j in range(3, 1 << k, 2):
        tab[j] = tab[j - 2] * x2 % P; ctr[1] += 1
    bits = bin(e)[2:]; i = 0; r = None
    while i < len(bits):
        if bits[i] == '0':
            r = r * r % P; ctr[0] += 1; i += 1; continue
        j = min(i + k, len(bits))
        while bits[j - 1] == '0': j -= 1
        w = int(bits[i:j], 2)
        if r is None: r = tab[w]
        else:
            for _ in range(j - i): r = r * r % P; ctr[0] += 1
            r = r * tab[w] % P; ctr[1] += 1
        i = j
    return r
xs = [rng.randrange(1, P) for _ in range(100)]
print(' d: %d bits, Hamming weight %d, hex %s' % (d.bit_length(), bin(d).count('1'), hex(d)))
best = None
for k in range(1, 8):
    ctr = [0, 0]
    ok = all(exp_window(x, d, k, [0, 0]) == pow(x, d, P) for x in xs[:10])
    exp_window(2, d, k, ctr)
    print(' sliding window k=%d: squarings %d, multiplications %d, total %d ; matches pow() on 10 inputs: %s' % (k, ctr[0], ctr[1], sum(ctr), ok))
    if best is None or sum(ctr) < best[0]: best = (sum(ctr), k, tuple(ctr))
hi = d >> 128; lo = d & ((1 << 128) - 1)
print(' hi = d>>128 =', hex(hi), '== (2^128-1)//5 ?', hi == (2 ** 128 - 1) // 5, '; lo =', hex(lo))
def exp_struct(x, k, ctr):
    x2 = x * x % P; ctr[0] += 1
    a = x2 * x % P; ctr[1] += 1; m = 1
    while m < 32:
        t = a
        for _ in range(4 * m): t = t * t % P; ctr[0] += 1
        a = t * a % P; ctr[1] += 1; m *= 2
    tab = {1: x}
    for j in range(3, 1 << k, 2):
        tab[j] = tab[j - 2] * x2 % P; ctr[1] += 1
    bits = bin(lo | (1 << 128))[3:]
    i = 0; r = a
    while i < 128:
        if bits[i] == '0':
            r = r * r % P; ctr[0] += 1; i += 1; continue
        j = min(i + k, 128)
        while bits[j - 1] == '0': j -= 1
        w = int(bits[i:j], 2)
        for _ in range(j - i): r = r * r % P; ctr[0] += 1
        r = r * tab[w] % P; ctr[1] += 1
        i = j
    return r
for k in range(1, 7):
    ctr = [0, 0]; v = exp_struct(3, k, ctr)
    print(' structured (nibble-pattern doubling for hi, window k=%d for lo): squarings %d, mults %d, total %d, correct: %s' % (k, ctr[0], ctr[1], sum(ctr), v == pow(3, d, P)))
print(' 100 random x: (x^d)^5 == x:', all(pow(pow(x, d, P), 5, P) == x for x in xs), '; (x^5)^d == x:', all(pow(pow(x, 5, P), d, P) == x for x in xs))
t = time.time(); [pow(x, d, P) for x in xs]; t1 = (time.time() - t) / 100
t = time.time(); [pow(x, 5, P) for x in xs * 100]; t2 = (time.time() - t) / 10000
print(' python timing: pow(x,d,p) %.1f us, pow(x,5,p) %.2f us, ratio %.0f' % (t1 * 1e6, t2 * 1e6, t1 / t2))

print('\n=== Q7: the 25 pairs at S-box fixed points (a,b in {0,1,-1,i,-i}) ===')
names = list(FIX.keys())
def jac_rank(Jm):
    if all(Jm[i][j] == 0 for i in range(3) for j in range(2)): return 0
    for i in range(3):
        for k in range(i + 1, 3):
            if (Jm[i][0] * Jm[k][1] - Jm[i][1] * Jm[k][0]) % P: return 2
    return 1
def tangent_run(nk, rho, r):
    s = [nk, rho, CAPACITY]; J = [[1, 0], [0, 1], [0, 0]]
    ranks = []
    for idx in schedule(r):
        s = [(s[i] + RC[idx][i]) % P for i in range(3)]
        full = idx < 4 or idx >= 60
        for i in (range(3) if full else range(1)):
            f = 5 * pow(s[i], 4, P) % P
            J[i] = [f * J[i][0] % P, f * J[i][1] % P]
            s[i] = pow(s[i], 5, P)
        s = mds_apply(s)
        J = [[sum(MDS[i][k] * J[k][j] for k in range(3)) % P for j in range(2)] for i in range(3)]
        ranks.append(jac_rank(J))
    return s, J, ranks
pts = {}; rows = []
for na in names:
    for nb in names:
        al, be = FIX[na], FIX[nb]
        nk = (al - c0[0]) % P; rho = (be - c0[1]) % P
        s0 = round_full([nk, rho, CAPACITY], 0)
        assert s0 == planestate(al, be)
        pts[(na, nb)] = s0
        h1 = hash_reduced(nk, rho, 1); h2 = hash_reduced(nk, rho, 2)
        _, J1, rk1 = tangent_run(nk, rho, 1); _, J2, rk2 = tangent_run(nk, rho, 2)
        g1 = (J1[0][0] == 0 and J1[0][1] == 0); g2 = (J2[0][0] == 0 and J2[0][1] == 0)
        s1in = [(s0[i] + c1[i]) % P for i in range(3)]
        spec = [i for i in range(3) if s1in[i] in FIX.values() or s0[i] in FIX.values()]
        rows.append((na, nb, [x.bit_length() for x in s0], rk1[:2], rk1[-1], g1, g2, spec, h1, h2, rk2[-1]))
for rw in rows:
    print('  (a,b)=(%2s,%2s) lane bits %s | rank after R0.M,R1.M %s | final rank r1 %d r2 %d | output-gradient zero: r1=%s r2=%s | special lanes %s' % (rw[0], rw[1], rw[2], rw[3], rw[4], rw[10], rw[5], rw[6], rw[7]))
print(' hash outputs distinct: r=1 %s, r=2 %s ; min bit length of any R0.M lane over the 25 states: %d' % (len(set(r_[8] for r_ in rows)) == 25, len(set(r_[9] for r_ in rows)) == 25, min(min(r_[2]) for r_ in rows)))
vals = {}
for key, s in pts.items():
    for i in range(3): vals.setdefault((i, s[i]), []).append(key)
print(' repeated lane values (same lane, same value) among the 25 states:', sum(1 for v in vals.values() if len(v) > 1))
coords = {(na, nb): (FIX[na], FIX[nb]) for na in names for nb in names}
keys = list(coords)
col3 = 0; axis3 = 0
for x, y, z in itertools.combinations(keys, 3):
    (x1, y1), (x2, y2), (x3, y3) = coords[x], coords[y], coords[z]
    if ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) % P == 0:
        col3 += 1
        if x1 == x2 == x3 or y1 == y2 == y3: axis3 += 1
print(' collinear triples among the 25 grid points (grid in (A,B); affine map to P0 preserves collinearity): total %d of 2300, %d axis-parallel, %d other' % (col3, axis3, col3 - axis3))
print(' (state,lane) pairs where the R0.M output lane is itself in {0,+-1,+-i}:', sum(1 for s in pts.values() for x in s if x in FIX.values()))
print(' (state,lane) pairs where the R1.C input lane is in the set:', sum(1 for s in pts.values() for i in range(3) if (s[i] + c1[i]) % P in FIX.values()))

print('\n=== Q8: points of P0 whose R1.C image has zero lanes ===')
for (i, j) in [(0, 1), (0, 2), (1, 2)]:
    a11, a12, r1 = MDS[i][0], MDS[i][1], (-c1[i] - MDS[i][2] * K) % P
    a21, a22, r2 = MDS[j][0], MDS[j][1], (-c1[j] - MDS[j][2] * K) % P
    det = (a11 * a22 - a12 * a21) % P
    A = (r1 * a22 - a12 * r2) * inv(det) % P; B = (a11 * r2 - r1 * a21) * inv(det) % P
    nk = (root5(A) - c0[0]) % P; rho = (root5(B) - c0[1]) % P
    s0 = round_full([nk, rho, CAPACITY], 0)
    s1in = [(s0[t] + c1[t]) % P for t in range(3)]
    third = 3 - i - j
    print(' lanes (%d,%d) zero: A=%s B=%s' % (i, j, hx(A), hx(B)))
    print('   nk=%s\n   rho=%s' % (hx(nk), hx(rho)))
    print('   R1.C input lanes:', [hx(x) for x in s1in], '-> both zero ok:', s1in[i] == 0 and s1in[j] == 0, '; third lane %d zero? %s' % (third, s1in[third] == 0))
    _, Jx, rks = tangent_run(nk, rho, 1)
    _, Jy, rks2 = tangent_run(nk, rho, 2)
    print('   Jacobian (3x2 wrt nk,rho) rank after each round r=1:', rks, ' r=2:', rks2)
    print('   hash r=1 %s ; r=2 %s' % (hx(hash_reduced(nk, rho, 1)), hx(hash_reduced(nk, rho, 2))))
    print('   gradient of output r=1: %s  r=2: %s' % ([hx(x) for x in Jx[0]], [hx(x) for x in Jy[0]]))
print(' unique (A,B) per pair since M has all 2x2 minors nonzero: PROVED')
print(' Bezout view: each zero condition is a quintic curve M_i0 a^5 + M_i1 b^5 = const in (nk,rho); two quintics meet in 25 points over the closure, exactly 1 is F_p-rational: DERIVED')
print(' all three lanes zero needs n.(-c1)=K; n.(-c1)-K =', hx(Kstar - K), '(nonzero): impossible for the real capacity')
print('\ntotal time %.1f s' % (time.time() - T0))
