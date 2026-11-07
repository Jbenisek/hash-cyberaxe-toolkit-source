"""U3 real-field experiments: partial rounds R4 (R5). Single process, exact big-int."""

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

import sys, random, time
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
from poseidon_ref import *
random.seed(20261012)
M = MDS
def rnd(): return random.randrange(P)
def inv(a): return pow(a, P - 2, P)
def mv(A, v): return [sum(A[i][j] * v[j] for j in range(3)) % P for i in range(3)]
def vadd(a, b): return [(x + y) % P for x, y in zip(a, b)]
def vsub(a, b): return [(x - y) % P for x, y in zip(a, b)]
def hx(x): return hex(x)
def upto_R3(nk, rho):
    s = [nk, rho, CAPACITY]
    for i in range(4): s = round_full(s, i)
    return s
def out(*a): print(*a); sys.stdout.flush()

out("== Q1 X5 exact on 1000 inputs ==")
bad = 0; bad2 = 0; bad3 = 0
for _ in range(1000):
    nk, rho = rnd(), rnd()
    s = upto_R3(nk, rho)
    w = pow((s[0] + RC[4][0]) % P, 5, P)
    pred = mv(M, [w, (s[1] + RC[4][1]) % P, (s[2] + RC[4][2]) % P])
    if round_partial(s, 4) != pred: bad += 1
    # carried version: drop lane1,2 constants of R4 and add M(0,c41,c42) after
    s2 = [(s[0] + RC[4][0]) % P, s[1], s[2]]
    s2[0] = pow(s2[0], 5, P)
    y = vadd(mv(M, s2), mv(M, [0, RC[4][1], RC[4][2]]))
    if y != round_partial(s, 4): bad2 += 1
out("X5 direct: mismatches", bad, "/1000 ; carried-constant single round mismatches", bad2, "/1000")

# effective constants (Q6) + full-pipeline check with carry for r=1,2 on 1000 inputs
def eff_consts(r):
    """lane1,2 constants of each partial round are removed and carried forward (through M and the following lane-0 S-box is
    unaffected only for lanes 1,2). Carry is added to next round's constant vector."""
    carry = [0, 0, 0]
    eff = {}
    for idx in range(4, 4 + r):
        c = vadd(RC[idx], carry)       # effective constant vector at this round (carry from previous round included)
        eff[idx] = c
        carry = mv(M, [0, c[1], c[2]])  # lanes 1,2 constants pass M (lane 0 constant stays with the S-box)
        eff[idx] = [c[0], 0, 0]
    nxt = vadd(RC[60], carry)
    return eff, nxt, carry
for r in (1, 2):
    eff, c60, carry = eff_consts(r)
    bad = 0
    for _ in range(1000):
        nk, rho = rnd(), rnd()
        s = upto_R3(nk, rho)
        for idx in range(4, 4 + r):
            s = [(s[0] + eff[idx][0]) % P, s[1], s[2]]
            s[0] = pow(s[0], 5, P); s = mv(M, s)
        s = vadd(s, [0, 0, 0])
        s = [(s[i] + c60[i]) % P for i in range(3)]
        s = [pow(x, 5, P) for x in s]; s = mv(M, s)
        for idx in (61, 62, 63): s = round_full(s, idx)
        if s[0] != hash_reduced(nk, rho, r): bad += 1
    out("carried constants full pipeline r=%d: mismatches %d/1000" % (r, bad))

out("\n== Q6 effective carried constants ==")
for r in (1, 2):
    eff, c60, carry = eff_consts(r)
    out("r=%d" % r)
    for idx in range(4, 4 + r):
        out("  R%d lane-0 const original %s ; effective %s ; lanes1,2 original (%s, %s) -> 0 (carried)" % (idx, hx(RC[idx][0]), hx(eff[idx][0]), hx(RC[idx][1]), hx(RC[idx][2])))
    out("  R60 original lane0..2: %s %s %s" % tuple(hx(x) for x in RC[60]))
    out("  R60 effective lane0..2: %s %s %s" % tuple(hx(x) for x in c60))
    out("  carry into R60 (= c60eff - c60): %s %s %s" % tuple(hx(x) for x in carry))
    for k, x in enumerate(c60):
        out("   R60 eff lane %d: bits %d, quad-residue %s, in{0,+-1,+-i}? %s" % (k, x.bit_length(), pow(x, (P - 1) // 2, P) == 1, x in (0, 1, P - 1)))
# Specific: which carried constant hits lane 0 of R5 and R60
c41, c42 = RC[4][1], RC[4][2]
d5 = (M[0][1] * c41 + M[0][2] * c42) % P
out("R5 lane0 extra from carry = M01*c41+M02*c42 = %s ; R5 lane1,2 extra = %s %s" % (hx(d5), hx((M[1][1]*c41+M[1][2]*c42)%P), hx((M[2][1]*c41+M[2][2]*c42)%P)))
out("R5 effective lane0 const = c50 + that = %s (bits %d)" % (hx((RC[5][0] + d5) % P), ((RC[5][0] + d5) % P).bit_length()))

out("\n== Q2/Q4 difference spaces ==")
M01, M02 = M[0][1], M[0][2]
trail = [0, M02, (-M01) % P]
out("trail vector r=2: (0, M02, -M01) =", [hx(x) for x in trail])
# r=1: random equal-lane-0 pairs, hand-built
bad = 0
for _ in range(200):
    s = [rnd(), rnd(), rnd()]; d1, d2 = rnd(), rnd()
    s2 = vadd(s, [0, d1, d2])
    a = round_partial(s, 4); b = round_partial(s2, 4)
    if vsub(b, a) != mv(M, [0, d1, d2]): bad += 1
out("r=1: 200 hand-built pairs with d0=0 pushed through R4: output diff == M(0,d1,d2) mismatches", bad)
# r=2 trail
bad = 0; bad_w = 0
for _ in range(200):
    s = [rnd(), rnd(), rnd()]; t = rnd()
    d = [(t * x) % P for x in trail]
    s2 = vadd(s, d)
    a4 = round_partial(s, 4); b4 = round_partial(s2, 4)
    dd = vsub(b4, a4)
    ok1 = dd == mv(M, d) and dd[0] == 0
    a5 = round_partial(a4, 5); b5 = round_partial(b4, 5)
    e = vsub(b5, a5)
    ok2 = e == mv(M, [0, dd[1], dd[2]])
    wa = pow((a4[0] + RC[5][0]) % P, 5, P); wb = pow((b4[0] + RC[5][0]) % P, 5, P)
    if not (ok1 and ok2 and wa == wb): bad += 1
out("r=2: 200 pairs along trail through R4,R5: failures", bad, "(lane-0 diff after R4 = 0, R5 w equal, diff after R5 = M(0,e1,e2))")
# negative controls
cnt = 0
for _ in range(200):
    s = [rnd(), rnd(), rnd()]; d1, d2 = rnd(), rnd()
    s2 = vadd(s, [0, d1, d2])
    a4 = round_partial(s, 4); b4 = round_partial(s2, 4)
    if (a4[0] - b4[0]) % P == 0: cnt += 1
out("r=2 negative control: generic d0=0 (not on trail line): lane0 equal after R4 in", cnt, "/200")
cnt = 0
for _ in range(200):
    s = [rnd(), rnd(), rnd()]; s2 = vadd(s, [rnd(), rnd(), rnd()])
    a4 = round_partial(s, 4); b4 = round_partial(s2, 4)
    if (a4[0] - b4[0]) % P == 0: cnt += 1
out("negative control: random d: lane0 equal after R4 in", cnt, "/200")
# diff vectors
d = trail
e1 = mv(M, d); e2 = mv(M, e1)
out("r=2 trail: d=(0,M02,-M01); M d =", [hx(x) for x in e1], " (lane0 should be 0:", e1[0] == 0, ")")
out("  M^2 d (diff after R5 for unit t) =", [hx(x) for x in e2], " lane0 nonzero:", e2[0] != 0)
# closure: image of {d0=0} under M, and where that meets {lane0 = 0}
# r=3 observability
def det3(A):
    return (A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1]) - A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0]) + A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0])) % P
def matmul(A, B): return [[sum(A[i][k]*B[k][j] for k in range(3)) % P for j in range(3)] for i in range(3)]
M2 = matmul(M, M); M3 = matmul(M2, M); M4 = matmul(M3, M)
rows = [M[0], M2[0], M3[0], M4[0]]
# rank of rows [e0; e0M; ...; e0M^{k-1}]
def rank(rowsl):
    A = [list(r) for r in rowsl]; rk = 0
    for c in range(3):
        piv = None
        for i in range(rk, len(A)):
            if A[i][c] % P: piv = i; break
        if piv is None: continue
        A[rk], A[piv] = A[piv], A[rk]
        iv = inv(A[rk][c]); A[rk] = [x * iv % P for x in A[rk]]
        for i in range(len(A)):
            if i != rk and A[i][c]:
                f = A[i][c]; A[i] = [(x - f * y) % P for x, y in zip(A[i], A[rk])]
        rk += 1
    return rk
E0 = [1, 0, 0]
def e0Mk(k):
    v = E0
    for _ in range(k):
        v = [sum(v[i] * M[i][j] for i in range(3)) % P for j in range(3)]
    return v
for r in range(1, 6):
    rws = [e0Mk(k) for k in range(r)]
    out("r=%d: rank of [e0; e0 M; ...; e0 M^(r-1)] = %d -> surviving trail direction dimension %d" % (r, rank(rws), 3 - rank(rws)))
out("det[e0;e0M;e0M^2] =", hx(det3([e0Mk(0), e0Mk(1), e0Mk(2)])))

out("\n== Q3 degrees of lane 0 after R3 / R4 / R5 on lines (finite differences) ==")
from math import comb
def line_deg_check(fn, D, label):
    # f(t) for t=0..D+2 ; Delta^k f(0) = sum (-1)^(k-j) C(k,j) f(j)
    vals = [fn(t) for t in range(D + 3)]
    def delta(k):
        s = 0; c = 1
        for j in range(k + 1):
            s += (-1) ** (k - j) * c * vals[j]
            c = c * (k - j) // (j + 1)  # exact integer binomial update
        return s % P
    dD, dD1, dD2 = delta(D), delta(D + 1), delta(D + 2)
    dm1 = delta(D - 1)
    out("  %s: Delta^%d != 0: %s ; Delta^%d == 0: %s ; Delta^%d == 0: %s  => degree exactly %d" % (label, D, dD != 0, D + 1, dD1 == 0, D + 2, dD2 == 0, D))
for trial in range(2):
    nk0, rho0, u, v = rnd(), rnd(), rnd(), rnd()
    def lane0_R3(t): return upto_R3((nk0 + u * t) % P, (rho0 + v * t) % P)[0]
    def lane0_R4(t):
        return round_partial(upto_R3((nk0 + u * t) % P, (rho0 + v * t) % P), 4)[0]
    def lane12_R3(t): return upto_R3((nk0 + u * t) % P, (rho0 + v * t) % P)[1]
    out("line", trial)
    line_deg_check(lane0_R3, 625, "lane0 after R3")
    line_deg_check(lane12_R3, 625, "lane1 after R3")
    line_deg_check(lane0_R4, 3125, "lane0 after R4")
    def s_in_R4(t): return upto_R3((nk0 + u * t) % P, (rho0 + v * t) % P)[0]
    if trial == 0:
        def lane0_R5(t):
            s = upto_R3((nk0 + u * t) % P, (rho0 + v * t) % P)
            return round_partial(round_partial(s, 4), 5)[0]
        line_deg_check(lane0_R5, 15625, "lane0 after R5")
# in (A,B) coordinates: degree 125 for lane 0 after R3
nk0, rho0, u, v = rnd(), rnd(), rnd(), rnd()
a0 = (nk0 + RC[0][0]) % P; b0 = (rho0 + RC[0][1]) % P
def lane0_R3_AB(t):
    A = (a0 + u * t) % P; B = (b0 + v * t) % P   # here (A,B) -> nk=A^(1/5)-c ... use direct: line in (A,B) plane
    s = mv(M, [A, B, pow((CAPACITY + RC[0][2]) % P, 5, P)])
    for i in range(1, 4): s = round_full(s, i)
    return s[0]
line_deg_check(lane0_R3_AB, 125, "lane0 after R3, line in (A,B) coords")
# Jacobian of lane0 after R3 wrt (nk,rho): rank / smoothness of level curve at random points (nonzero gradient)
def grad_R3(nk, rho):
    h = 1  # exact derivative via polynomial identity: use difference quotient is not exact; use dual numbers
    # dual numbers via explicit forward-mode AD
    return None
out("done real")
