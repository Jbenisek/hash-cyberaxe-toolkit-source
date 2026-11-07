# U12 real-field experiments (single process, exact big-int). Run: python u12_real.py

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

import sys, random, time, math
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
P, RC, M, CAP = R.P, R.RC, R.MDS, R.CAPACITY
random.seed(12)
D5 = pow(5, -1, P - 1)


def det3(m):
    a, b, c = m[0]; d, e, f = m[1]; g, h, i = m[2]
    return (a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)) % P


def inv3(m):
    a, b, c = m[0]; d, e, f = m[1]; g, h, i = m[2]
    di = pow(det3(m), -1, P)
    adj = [[e * i - f * h, c * h - b * i, b * f - c * e],
           [f * g - d * i, a * i - c * g, c * d - a * f],
           [d * h - e * g, b * g - a * h, a * e - b * d]]
    return [[x * di % P for x in row] for row in adj]


MI = inv3(M)


def mv(m, s): return [sum(m[i][j] * s[j] for j in range(3)) % P for i in range(3)]


full = lambda idx: idx < 4 or idx >= 60
def rnd(s, idx): return R.round_full(s, idx) if full(idx) else R.round_partial(s, idx)
roots = 0


def root(x):
    global roots
    roots += 1
    return pow(x, D5, P)


def rnd_inv(s, idx):
    t = mv(MI, s)
    t = [root(x) for x in t] if full(idx) else [root(t[0]), t[1], t[2]]
    return [(t[i] - RC[idx][i]) % P for i in range(3)]


def run(s, idxs):
    for i in idxs: s = rnd(s, i)
    return s


def rinv(s, idxs):
    for i in reversed(idxs): s = rnd_inv(s, i)
    return s


rr = lambda: random.randrange(P)
out = []


def log(*a):
    m = ' '.join(str(x) for x in a)
    print(m, flush=True)
    out.append(m)


M2 = [[sum(M[i][k] * M[k][j] for k in range(3)) % P for j in range(3)] for i in range(3)]

log('=== 1. r=2 is r=1 with R5 inserted ===')
pre = [0, 1, 2, 3, 4]; tail = [60, 61, 62, 63]
b1 = b2 = b3 = 0
for _ in range(300):
    nk, rho = rr(), rr()
    sA = run([nk, rho, CAP], pre)
    st1 = run(sA, tail)
    st2 = run(rnd(sA, 5), tail)
    if st1[0] != R.hash_reduced(nk, rho, 1): b1 += 1
    if st2[0] != R.hash_reduced(nk, rho, 2): b2 += 1
    c = rinv(st1, tail)           # state after R4 (inverse of the tail)
    if c != sA: b3 += 1
    if run(rnd(c, 5), tail) != st2: b3 += 1
log('OBSERVED 300 random inputs: tail(state after R4) lane0 == hash_reduced r=1: failures', b1,
    '; tail(R5(state after R4)) lane0 == hash_reduced r=2: failures', b2)
log('OBSERVED full 3-lane state: G2 = Psi o R5 o Psi^-1 o G1 (Psi = R60..R63, G1 = r=1 state): failures', b3, 'of 600 checks')
log('OBSERVED schedule(1) =', R.schedule(1), ' schedule(2) =', R.schedule(2),
    ' prefix equal:', R.schedule(1)[:5] == R.schedule(2)[:5], ' suffix equal:', R.schedule(1)[5:] == R.schedule(2)[6:])
nk, rho = rr(), rr()
log('OBSERVED hash r=1 != hash r=2 at a random input:', R.hash_reduced(nk, rho, 1) != R.hash_reduced(nk, rho, 2))

log('\n=== 2. degree tracker (top-form evaluation along nk=a+u t, rho=b+v t, exact) ===')


def tracker(u, v, r):
    L = [(1, u % P), (1, v % P), (0, CAP % P)]   # (deg, leading coeff); deg 0 = full value; None = zero
    steps = []; cancel = []

    def add(l, c):
        d, x = l
        if d is None or d == 0:
            val = ((x if d is not None else 0) + c) % P
            return (0, val) if val else (None, 0)
        return l

    def sb(l):
        d, x = l
        if d is None: return l
        y = pow(x, 5, P)
        if d > 0: return (d * 5, y)
        return (0, y) if y else (None, 0)

    def mds(Ls, name):
        res = []
        for i in range(3):
            terms = [(Ls[j][0], M[i][j] * Ls[j][1] % P) for j in range(3) if Ls[j][0] is not None]
            if not terms: res.append((None, 0)); continue
            dm = max(t[0] for t in terms)
            s = sum(t[1] for t in terms if t[0] == dm) % P
            if s == 0: cancel.append((name, i)); res.append((None, 0))
            else: res.append((dm, s))
        return res

    for idx in R.schedule(r):
        L = [add(L[i], RC[idx][i]) for i in range(3)]
        L = [sb(L[i]) if (full(idx) or i == 0) else L[i] for i in range(3)]
        L = mds(L, idx)
        steps.append((idx, [l[0] for l in L]))
    return steps, cancel


res = {}
for r in (1, 2):
    st, c = tracker(1, 2, r); res[r] = st
    log('r=%d cancellations: %s' % (r, c))
    for idx, d in st:
        log('  r=%d after R%-2d: lane degrees %s  = 5^%s' % (r, idx, d, [round(math.log(x, 5), 3) for x in d]))
for r in (1, 2):
    fails = 0; degs = set()
    dirs = [(1, 0), (0, 1)] + [(rr(), rr()) for _ in range(30)]
    for (u, v) in dirs:
        st, c = tracker(u, v, r)
        degs.add(st[-1][1][0])
        if c: fails += 1
    log('OBSERVED r=%d final lane0 degree over 32 directions (incl. both axes): %s; directions with a cancellation: %d; 5^%d = %d'
        % (r, degs, fails, 8 + r, 5 ** (8 + r)))
s1 = res[1]; s2 = res[2]
log('ratio lane-0 degree r=2 / r=1 at tail positions R60,R61,R62,R63:',
    [s2[6 + k][1][0] // s1[5 + k][1][0] for k in range(4)], '; R5 vs R4 (r=2):', s2[5][1][0] // s2[4][1][0],
    '; R4 r=1 vs r=2 identical:', s1[4] == s2[4], '; R0..R4 identical:', s1[:5] == s2[:5])
for i in range(3):
    ratio = (-M[i][1] * pow(M[i][0], -1, P)) % P
    u = pow(ratio, D5, P)
    for r in (1, 2):
        st, c = tracker(u, 1, r)
        log('OBSERVED drop-direction lane %d, r=%d: degrees (lane0) after R0..R4 %s | final %s | cancel %s'
            % (i, r, [x[1][0] for x in st[:5]], st[-1][1][0], c))

log('\n=== 3. trail vectors on the real field ===')
d = [0, M[0][2], (-M[0][1]) % P]
Md = mv(M, d); M2d = mv(M, Md)
log('trail vector d = (0, M02, -M01) = (0, %s, %s)' % (hex(d[1]), hex(d[2])))
log('(M d)_0 =', hex(Md[0]), ' (M^2 d)_0 =', hex(M2d[0]))
row1 = M[0]; row2 = [sum(M[0][k] * M[k][j] for k in range(3)) % P for j in range(3)]
row3 = [sum(M[0][k] * M2[k][j] for k in range(3)) % P for j in range(3)]
log('det[e0M; e0M^2; e0M^3] (rows as coded) =', hex(det3([row1, row2, row3])))
f1 = f2 = ok = 0
for _ in range(200):
    s = [rr(), rr(), rr()]
    sp = [s[0], (s[1] + rr()) % P, (s[2] + rr()) % P]
    a = rnd(s, 4); b = rnd(sp, 4)
    if [(b[i] - a[i]) % P for i in range(3)] != mv(M, [0, (sp[1] - s[1]) % P, (sp[2] - s[2]) % P]): f1 += 1
    t = rr(); s2 = [(s[i] + t * d[i]) % P for i in range(3)]
    a = rnd(s, 4); b = rnd(s2, 4)
    if a[0] != b[0]: f2 += 1
    a5 = rnd(a, 5); b5 = rnd(b, 5)
    if [(b5[i] - a5[i]) % P for i in range(3)] == mv(M2, [t * x % P for x in d]): ok += 1
    last = [(b5[i] - a5[i]) % P for i in range(3)]
log('OBSERVED 200 pairs equal in lane0 entering R4 with random d1,d2: output diff == M(0,d1,d2): failures', f1)
log('OBSERVED 200 pairs along trail line t*d entering R4: lane0 equal after R4.M: failures', f2,
    '; diff after R5.M == M^2 (t d) in', ok, 'of 200; lane0 of that diff is nonzero:', last[0] != 0)
# diff at the R60 entry lies in which spaces
log('OBSERVED r=1 diff entering R60 lies in M*{d0=0} (2-dim); r=2 diff entering R60 lies on the line spanned by M^2 d =', [hex(x) for x in mv(M2, d)])
# three partial rounds: kernel of observability is 0 => rank
log('derivation check: a pair entering R4 with d0=0 stays lane-0-equal after k partial rounds iff (M^j d)_0=0 for j=0..k-1: dims 3-k (k=1: 2, k=2: 1, k=3: det!=0 -> 0)')

log('\n=== 4. ladder arrows ===')
Kc = pow((CAP + RC[0][2]) % P, 5, P)
bad = 0
for _ in range(200):
    nk, rho = rr(), rr()
    if mv(MI, rnd([nk, rho, CAP], 0))[2] != Kc: bad += 1
log('OBSERVED arrow init->P0: (M^-1 s)_2 == K on 200 random inputs, failures', bad)


def fdiff(f, k):
    vals = [f(t) for t in range(k + 1)]
    res = [0, 0, 0]; c = 1
    for i in range(k + 1):
        sign = -1 if (k - i) % 2 else 1
        for l in range(3): res[l] = (res[l] + sign * c * vals[i][l]) % P
        c = c * (k - i) * pow(i + 1, -1, P) % P
    return res


def line_fn(sched, a0, b0, al, be):
    def f(t):
        A = (a0 + al * t) % P; B = (b0 + be * t) % P
        return run([(pow(A, D5, P) - RC[0][0]) % P, (pow(B, D5, P) - RC[0][1]) % P, CAP], sched)
    return f


a0, b0, al, be = rr(), rr(), rr(), rr()
for name, sched, deg in [('R0', [0], 1), ('R0-R1', [0, 1], 5), ('R0-R2', [0, 1, 2], 25), ('R0-R3', [0, 1, 2, 3], 125),
                         ('R0-R4', [0, 1, 2, 3, 4], 625), ('R0-R4,R60 (r=1)', [0, 1, 2, 3, 4, 60], 3125),
                         ('R0-R5 (r=2)', [0, 1, 2, 3, 4, 5], 3125)]:
    f = line_fn(sched, a0, b0, al, be); t0 = time.time()
    hi = fdiff(f, deg + 1); lo = fdiff(f, deg)
    log('OBSERVED (A,B)-line, state after %s: Delta^%d = %s ; Delta^%d nonzero per lane %s -> exact degree in t = %s  (%.1fs)'
        % (name, deg + 1, hi, deg, [x != 0 for x in lo], deg if hi == [0, 0, 0] and all(lo) else 'NOT CONFIRMED', time.time() - t0))
bad = 0
for _ in range(1000):
    s = [rr(), rr(), rr()]
    w = pow((s[0] + RC[4][0]) % P, 5, P)
    if mv(M, [w, (s[1] + RC[4][1]) % P, (s[2] + RC[4][2]) % P]) != R.round_partial(s, 4): bad += 1
log('OBSERVED R4 = M(w, s1+c41, s2+c42), w=(s0+c40)^5, 1000 random states, failures', bad)
bad = 0
for _ in range(1000):
    nk, rho = rr(), rr()
    s = run([nk, rho, CAP], [0, 1, 2, 3, 4, 60, 61, 62])
    T = [pow((s[i] + RC[63][i]) % P, 5, P) for i in range(3)]
    if sum(M[0][j] * T[j] for j in range(3)) % P != R.hash_reduced(nk, rho, 1): bad += 1
log('OBSERVED y = sum_j M0j T_j, T = S(state after R62.M + c63), r=1, 1000 inputs, failures', bad)

log('\n=== 5. inversion cost: 5th roots ===')
t0 = time.time(); [R.hash_reduced(rr(), rr(), 1) for _ in range(50)]; fwd = (time.time() - t0) / 50
xs = [rr() for _ in range(50)]
t0 = time.time(); [pow(x, D5, P) for x in xs]; rt = (time.time() - t0) / 50
log('OBSERVED forward hash r=1 %.0f us; one 5th root pow(x,d,p) %.0f us; d: %d bits, popcount %d -> %d squarings + %d mults (plain square-and-multiply)'
    % (fwd * 1e6, rt * 1e6, D5.bit_length(), bin(D5).count('1'), D5.bit_length() - 1, bin(D5).count('1') - 1))
for r in (1, 2):
    sch = R.schedule(r)
    ok = 0
    for _ in range(20):
        s = [rr(), rr(), rr()]
        if rinv(run(s, sch), sch) == s: ok += 1
    per = {}
    for idx in sch:
        roots = 0; rnd_inv([rr(), rr(), rr()], idx); per[idx] = roots
    tot = sum(per.values()); to_R0M = tot - per[0]
    log('OBSERVED r=%d: full-state inverse returns input %d/20; 5th roots per round %s; total %d; back to the state after R0.M %d; to (A,B) +0, to (nk,rho) +2 = %d'
        % (r, ok, per, tot, to_R0M, to_R0M + 2))
    y = rr(); T0, T1 = rr(), rr()
    T2 = (y - M[0][0] * T0 - M[0][1] * T1) * pow(M[0][2], -1, P) % P
    roots = 0
    t = [root(x) for x in (T0, T1, T2)]
    s = [(t[i] - RC[63][i]) % P for i in range(3)]
    s = rinv(s, sch[:-1])[:3]
    # rinv above went back through R0 too; recompute stopping after R1
    roots_total = roots
    roots = 0
    t = [root(x) for x in (T0, T1, T2)]
    s = [(t[i] - RC[63][i]) % P for i in range(3)]
    s = rinv(s, sch[1:-1])         # now state after R0.M
    resid = (mv(MI, s)[2] - Kc) % P
    chk = run(s, sch[1:])
    log('OBSERVED r=%d: from output y with T0,T1 free: %d 5th roots to reach the state after R0.M; forward check lane0==y: %s; plane residual (M^-1 s)_2-K %s'
        % (r, roots, chk[0] == y, 'nonzero (random T0,T1 is not a preimage)' if resid else 'ZERO'))
open('u12_real_output.txt', 'w').write('\n'.join(out))
