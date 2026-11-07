# E4: symmetry S(ix)=iS(x). Build state pairs related by i at R0 input, track the defect s' - i*s through every step.
import random
from common import *
from toy import *
rnd = random.Random(7)
i_ = I_
print("sqrt(-1) used:", hex(i_), "  i^2+1 mod p =", (i_*i_+1) % P)
def step_trace(nk, rho, r):
    """list of (label, state) after each step C,S,M for all rounds"""
    s = [nk, rho, PR.CAPACITY]; tr = []
    for idx in PR.schedule(r):
        full = idx < 4 or idx >= 60
        s = [(s[j]+PR.RC[idx][j]) % P for j in range(3)]; tr.append(("R%d.C"%idx, s[:]))
        s = [pow(x, 5, P) if (full or j == 0) else x for j, x in enumerate(s)]; tr.append(("R%d.S"%idx, s[:]))
        s = matvec(PR.MDS, s); tr.append(("R%d.M"%idx, s[:]))
    return tr
def pair(nk, rho):
    """partner (nk',rho') with nk'+c00 = i(nk+c00), rho'+c01 = i(rho+c01): lanes 0,1 are i-related at R0.C"""
    c = PR.RC[0]
    return ((i_*(nk+c[0])-c[0]) % P, (i_*(rho+c[1])-c[1]) % P)
for r in (1, 2):
    print("\n=== r=%d: defect d = s' - i*s after each step, for 6 random inputs (pairs related by i in lanes 0,1 at R0.C; lane 2 is the constant 2^65 in both) ==="%r)
    runs = []
    for _ in range(6):
        nk = rnd.randrange(P); rho = rnd.randrange(P); nk2, rho2 = pair(nk, rho)
        a = step_trace(nk, rho, r); b = step_trace(nk2, rho2, r)
        runs.append([(la, [(y[j]-i_*x[j]) % P for j in range(3)]) for (la, x), (_, y) in zip(a, b)])
    # predicted constant defect after R0.M
    K = pow(PR.CAPACITY+PR.RC[0][2], 5, P)
    m2 = [PR.MDS[j][2] for j in range(3)]
    pred = [(1-i_)*K*m2[j] % P for j in range(3)]
    for t in range(len(runs[0])):
        label = runs[0][t][0]
        defects = [run[t][1] for run in runs]
        zero_lanes = [sum(1 for d in defects if d[j] == 0) for j in range(3)]
        same = all(d == defects[0] for d in defects)
        # tangent test for R0.S/R0.M
        note = ""
        if label == "R0.M": note = " predicted (1-i)*K*M[:,2] equal: %s"%(defects[0] == pred)
        if t < 12 or label.endswith(".M") and t < 20:
            print("%-7s defect identical across inputs: %-5s  #zero-lane-entries (of 6 inputs, per lane): %s%s"%(label, same, zero_lanes, note))
    # when does the defect become input-dependent / what is its nature
    firstdep = next(run_t for run_t in range(len(runs[0])) if not all(run[run_t][1] == runs[0][run_t][1] for run in runs))
    print("first step at which the defect depends on the input:", runs[0][firstdep][0])
    # does the final output keep any relation?
    fin = runs[0][-1][1]
    print("final-state defect lane0 nonzero:", fin[0] != 0)
print("\n=== defect at R1.C: predicted (1-i)(K*M[:,2] + c1) ===")
nk = rnd.randrange(P); rho = rnd.randrange(P); nk2, rho2 = pair(nk, rho)
a = step_trace(nk, rho, 1); b = step_trace(nk2, rho2, 1)
K = pow(PR.CAPACITY+PR.RC[0][2], 5, P)
d = [(b[3][1][j]-i_*a[3][1][j]) % P for j in range(3)]  # index 3 = R1.C ? (R0.C,R0.S,R0.M,R1.C)
pred = [(1-i_)*(K*PR.MDS[j][2]+PR.RC[1][j]) % P for j in range(3)]
print(a[3][0], "defect==pred:", d == pred)
print("\n=== projective scaling (lambda^4 != 1): S(lam x)=lam^5 S(x) one round only ===")
lam = rnd.randrange(2, P)
x = [rnd.randrange(P) for _ in range(3)]
lx = [lam*v % P for v in x]
S = lambda v: [pow(t, 5, P) for t in v]
print("S(lam x) == lam^5 S(x):", S(lx) == [pow(lam, 5, P)*t % P for t in S(x)], "  S(lam x) == lam S(x):", S(lx) == [lam*t % P for t in S(x)])

# --- toys: does the pair map give any output relation? exhaustive on toy
print("\n=== toy exhaustive: pair (nk,rho)->(i(nk+c0)-c0, i(rho+c1)-c1), count inputs with out' = i^k * out, out' = out; expectation q (=q^2/q) each ===")
for q in (257, 769, 1009):
    for r in (1, 2):
        T = make_toy(q, 1000+q+r, r); ii = sqrt_m1(q)
        nk, rho = np.meshgrid(np.arange(q), np.arange(q), indexing='ij'); nk = nk.ravel(); rho = rho.ravel()
        out = toy_trace(T, nk, rho)[0]
        c = T['RC'][0]
        nk2 = (ii*(nk+c[0])-c[0]) % q; rho2 = (ii*(rho+c[1])-c[1]) % q
        out2 = toy_trace(T, nk2, rho2)[0]
        res = []
        for k in range(4):
            res.append(int(np.sum(out2 == (pow(ii, k, q)*out) % q)))
        res.append(int(np.sum(out2 == (-out) % q)) if False else None)
        print("q=%d r=%d i=%d  counts for out'=i^k*out, k=0..3: %s  (expected about %d)"%(q, r, ii, res[:4], q))
# --- toy: where does the exact symmetry survive? (no constants) count
print("\n=== toy, constants set to zero: symmetric map commutes with i? (sanity of the PROVED statement) ===")
q = 257; T = make_toy(q, 5, 1); T['RC'] = [[0, 0, 0] for _ in T['RC']]; ii = sqrt_m1(q)
rr = np.arange(0, 3000)
x = np.random.default_rng(1).integers(0, q, 3000); y = np.random.default_rng(2).integers(0, q, 3000)
T['cap'] = 0
o1 = toy_trace(T, x, y)[0]; o2 = toy_trace(T, ii*x % q, ii*y % q)[0]
print("with zero constants and zero capacity, out(i x, i y) == i*out(x,y) for", int(np.sum(o2 == ii*o1 % q)), "/ 3000")
T['cap'] = 5
o1 = toy_trace(T, x, y)[0]; o2 = toy_trace(T, ii*x % q, ii*y % q)[0]
print("with zero constants but capacity 5 (not i-scaled): relation holds for", int(np.sum(o2 == ii*o1 % q)), "/ 3000 (random-level ~", 3000//q, ")")
