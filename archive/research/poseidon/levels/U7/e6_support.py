# E6: polynomial normal form (support / degree) of compositions of the round map R(x) = M * S(x + c), state x = (x0,x1,x2) three FREE variables, over the real F_p.
# "ANF" here = the multivariate polynomial over F_p (the binary ANF is meaningless over a prime field).
import itertools, time
from common import *
t0 = time.time()
def padd(a, b, q=P):
    r = dict(a)
    for k, v in b.items():
        r[k] = (r.get(k, 0)+v) % q
        if r[k] == 0: del r[k]
    return r
def pscale(a, c):
    return {k: v*c % P for k, v in a.items()} if c % P else {}
def pmul(a, b):
    r = {}
    for k1, v1 in a.items():
        for k2, v2 in b.items():
            k = (k1[0]+k2[0], k1[1]+k2[1], k1[2]+k2[2])
            r[k] = (r.get(k, 0)+v1*v2) % P
    return {k: v for k, v in r.items() if v}
def pconst(c): return {(0, 0, 0): c % P} if c % P else {}
def ppow5(a):
    a2 = pmul(a, a); a4 = pmul(a2, a2); return pmul(a4, a)
def var(j):
    e = [0, 0, 0]; e[j] = 1; return {tuple(e): 1}
def apply_round(state, idx, full, use_const=True):
    ins = [padd(state[j], pconst(PR.RC[idx][j] if use_const else 0)) for j in range(3)]
    outs = [ppow5(ins[j]) if (full or j == 0) else ins[j] for j in range(3)]
    new = []
    for i in range(3):
        acc = {}
        for j in range(3): acc = padd(acc, pscale(outs[j], PR.MDS[i][j]))
        new.append(acc)
    return new
def profile(state):
    sizes = [len(s) for s in state]
    deg = [max(sum(k) for k in s) for s in state]
    res = set();
    for s in state:
        for k in s: res.add(tuple(e % 5 for e in k))
    return sizes, deg, len(res)
def full_triangle(d): return (d+1)*(d+2)*(d+3)//6
x = [var(0), var(1), var(2)]
print("Notation: x = free state (x0,x1,x2); F = full round, P = partial round (S on lane 0 only); 'c' = with the real round constants of the named original rounds, 'n' = no constants")
print("columns: monomials per lane | degree per lane | number of distinct exponent-residue classes mod 5 over all monomials (1 means every exponent vector is = 0 mod 5)")
def run(seq, use_const, label):
    st = [s for s in x]
    for idx, full in seq: st = apply_round(st, idx, full, use_const)
    sz, dg, nres = profile(st)
    print("%-34s %-5s sizes %-20s deg %-22s residue-classes(mod 5): %-4d full-triangle(deg %d) = %d  [%.1fs]" % (label, "const" if use_const else "none", sz, dg, nres, max(dg), full_triangle(max(dg)), time.time()-t0), flush=True)
    return st
for uc in (False, True):
    run([(1, True)], uc, "F")
    run([(4, False)], uc, "P (original R4)")
    run([(1, True), (2, True)], uc, "F,F")
    run([(4, False), (5, False)], uc, "P,P (R4,R5)")
    run([(3, True), (4, False)], uc, "F,P (R3,R4)")
    run([(4, False), (60, True)], uc, "P,F (R4,R60)")
    run([(4, False), (5, False), (60, True)], uc, "P,P,F (R4,R5,R60)")
run([(1, True), (2, True), (3, True)], False, "F,F,F")
# no-constant closed forms
print("\nno-constant check: F^k lane is a polynomial in X=x^5 of degree 5^(k-1): predicted monomials C(5^(k-1)+2,2): k=1: 3 (deg 5 -> 3 monomials x_j^5), k=2: 21, k=3: 351")
# S o M (the S-box AFTER the mix): coordinate (Mx)_j^5
print("\n=== S o M: lane j = (M_j . x)^5 (what the next round's S-box sees, no constants) ===")
for j in range(3):
    lin = {}
    for k in range(3): lin = padd(lin, pscale(var(k), PR.MDS[j][k]))
    p5 = ppow5(lin)
    print("lane", j, "monomials", len(p5), "(homogeneous degree 5 in 3 vars has C(7,2)=21)", "all coefficients nonzero:", len(p5) == 21)
# exponents of homogeneous form = binomial*M powers; all binomials C(5;a,b,c) nonzero mod p (5<p) -> dense.
print("\nCoefficient of x0^a x1^b x2^c in (m0 x0+m1 x1+m2 x2)^5 is the multinomial 5!/(a!b!c!) * m0^a m1^b m2^c: nonzero for all 21 (PROVED, 5 < p, M entries nonzero).")
print("elapsed %.1fs" % (time.time()-t0))
