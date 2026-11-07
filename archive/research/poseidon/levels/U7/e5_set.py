# E5: S-box on {0,+-1,+-i}^3 and MDS; E4b: can the exact i-relation be made to survive R1.C?
import itertools, random
from common import *
from toy import *
rnd = random.Random(55)
i_ = I_
Sset = [0, 1, P-1, i_, P-i_]
S = set(Sset)
print("S-box fixed point set size check: x^5==x for the 5 values:", all(pow(x, 5, P) == x for x in Sset))
print("number of x in {0,+-1,+-i,...} with x^5 = x : exactly the 5 (PROVED: x^4=1 or x=0)")
trip = list(itertools.product(Sset, repeat=3))
print("triples:", len(trip))
def inset(v): return [x in S for x in v]
res = {"S(v)==v": sum(1 for v in trip if [pow(x, 5, P) for x in v] == list(v))}
back = []; lanes = {0: 0, 1: 0, 2: 0, 3: 0}
for v in trip:
    w = matvec(PR.MDS, list(v))
    k = sum(inset(w)); lanes[k] += 1
    if k == 3: back.append(v)
print(res)
print("M*v for v in the set^3: number of output lanes landing in the set, histogram:", lanes)
print("triples whose M*v is entirely in the set:", back, "(only the zero vector expected)")
# nonzero v: any lane returns?
nz = [v for v in trip if any(v)]
print("nonzero v with at least one output lane in the set:", sum(1 for v in nz if any(inset(matvec(PR.MDS, list(v))))), "of", len(nz))
# with round constants: v = C-step inputs? count triples w such that M S(w+c0)=M(w+c0 if in set) ... w+c in set means w = v - c: S fixes -> M v
# structure: does M map the set to a set up to scaling? check ratios M v / v for 1-dim sets: M*(t,0,0)
print("M * (t,0,0) for t in {1,-1,i,-i}: lanes in set?", [inset(matvec(PR.MDS, [t, 0, 0])) for t in Sset[1:]])
# backward: M^-1 v
def inv3(M, q):
    a = M
    cof = [[(a[(j+1)%3][(i+1)%3]*a[(j+2)%3][(i+2)%3]-a[(j+1)%3][(i+2)%3]*a[(j+2)%3][(i+1)%3]) % q for j in range(3)] for i in range(3)]
    det = sum(a[0][j]*cof[j][0] for j in range(3)) % q
    di = pow(det, -1, q)
    return [[cof[i][j]*di % q for j in range(3)] for i in range(3)]
Mi = inv3(PR.MDS, P)
print("M * M^-1 = I check:", all(sum(PR.MDS[i][k]*Mi[k][j] for k in range(3)) % P == (1 if i == j else 0) for i in range(3) for j in range(3)))
print("M^-1 v lanes in set (histogram over 125):", {k: sum(1 for v in trip if sum(inset(matvec(Mi, list(v)))) == k) for k in range(4)})
# squares of lanes: S-box image at i: fixed
print("\n=== toy ensembles: random Cauchy M over F_q (q = 1 mod 4); count nonzero v in {0,+-1,+-i}^3 with M v having k lanes in the set ===")
def cauchy(q, rnd):
    while True:
        xs = [rnd.randrange(q) for _ in range(3)]; ys = [rnd.randrange(q) for _ in range(3)]
        if len(set(xs)) == 3 and len(set(ys)) == 3 and all((x+y) % q for x in xs for y in ys):
            return [[pow(x+y, -1, q) for y in ys] for x in xs]
for q in (17, 29, 37, 97, 193, 257, 769):
    ii = sqrt_m1(q); st = {0, 1, q-1, ii, q-ii}
    tr = [v for v in itertools.product(sorted(st), repeat=3) if any(v)]
    tot = 0; n = 2000; hist = [0]*4
    for _ in range(n):
        M = cauchy(q, rnd)
        for v in tr:
            w = [sum(M[a][b]*v[b] for b in range(3)) % q for a in range(3)]
            hist[sum(x in st for x in w)] += 1
    # expectation for generic: per nonzero v with weight wgt, each output lane (nonzero combination of nonzero entries) uniform => P(in set)=5/q
    exp = [len(tr)*n*sum([1][0:0]) for _ in range(1)]
    p_ = 5/q; from math import comb
    e = [len(tr)*n*comb(3, k)*p_**k*(1-p_)**(3-k) for k in range(4)]
    print("q=%d  lanes-in-set histogram %s   binomial(3,5/q) expectation %s"%(q, hist, [round(x, 1) for x in e]))
print("\n=== E4b: can the i-relation be made to survive R1.C? needs K = -(M^-1 c1)_2 (one field equality) ===")
K = pow(PR.CAPACITY+PR.RC[0][2], 5, P)
for z, name in ((i_, "i"), (P-i_, "-i"), (P-1, "-1")):
    # pair at R0.C lanes 0,1 related by z, lane 2 constant in both: after R0.M defect = (1-z)K M[:,2]; want (1-z)K m2 = (z-1)c1  <=> K m2 = -c1 => c1 proportional to column 2 with ratio -K
    t = [(PR.RC[1][j]*inv(PR.MDS[j][2])) % P for j in range(3)]
    print("z=%s: c1_j / M[j,2] =  (lane0 %s, lane1 %s, lane2 %s)  needs all three == -K=%s : %s"%(name, hex(t[0])[:14], hex(t[1])[:14], hex(t[2])[:14], hex((-K) % P)[:14], t[0] == t[1] == t[2] == (-K) % P))
