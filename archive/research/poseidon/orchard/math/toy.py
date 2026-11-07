import sys, time, json, random, collections, math
from flint import nmod_poly, nmod

ALT_EVERY = 1
class Toy:
    def __init__(self, p, seed, r):
        self.p = p; self.r = r
        rng = random.Random(seed)
        self.RC = [[rng.randrange(p) for _ in range(3)] for _ in range(64)]
        xs = rng.sample(range(p), 3); ys = rng.sample(range(p), 3)
        self.M = [[pow((xs[i] + ys[j]) % p, -1, p) for j in range(3)] for i in range(3)]
        self.e5inv = pow(5, -1, p - 1)
        self.CAP = (1 << 65) % p
        self.K = pow((self.CAP + self.RC[0][2]) % p, 5, p)
    def mds(self, s):
        p = self.p
        return [sum(self.M[i][j] * s[j] for j in range(3)) % p for i in range(3)]
    def rnd(self, s, k, full):
        p = self.p
        s = [(s[i] + self.RC[k][i]) % p for i in range(3)]
        s = [pow(x, 5, p) if (full or i == 0) else x for i, x in enumerate(s)]
        return self.mds(s)
    def rounds(self):
        r = self.r
        return [(k, True) for k in range(4)] + [(4 + i, False) for i in range(r)] + [(k, True) for k in range(60, 64)]
    def digest(self, nk, rho):
        s = [nk % self.p, rho % self.p, self.CAP]
        for k, f in self.rounds(): s = self.rnd(s, k, f)
        return s[0]

class TLine:
    def __init__(self, T, j):
        p = T.p; M = T.M; self.T = T; self.j = j
        I = [k for k in range(3) if k != j]; i1, i2 = I
        base = [(M[k][2] * T.K + T.RC[1][k]) % p for k in range(3)]
        det = (M[i1][0] * M[i2][1] - M[i1][1] * M[i2][0]) % p; inv = pow(det, -1, p)
        e, f = -base[i1] % p, -base[i2] % p
        self.UQ = ((e * M[i2][1] - M[i1][1] * f) * inv) % p
        self.VQ = ((M[i1][0] * f - e * M[i2][0]) * inv) % p
        self.a, self.b = M[j][1], (-M[j][0]) % p
        self.d = [(M[k][0] * self.a + M[k][1] * self.b) % p for k in range(3)]
        self.xQ = [(M[k][0] * self.UQ + M[k][1] * self.VQ + base[k]) % p for k in range(3)]
        self.v0 = [pow(self.xQ[k], 5, p) if k == j else 0 for k in range(3)]
        self.v1 = [pow(self.d[k], 5, p) if k != j else 0 for k in range(3)]
    def inputs(self, tau):
        T = self.T; p = T.p
        U = (self.UQ + tau * self.a) % p; V = (self.VQ + tau * self.b) % p
        return (pow(U, T.e5inv, p) - T.RC[0][0]) % p, (pow(V, T.e5inv, p) - T.RC[0][1]) % p
    def F(self, W):
        T = self.T
        s = T.mds([(self.v0[k] + W * self.v1[k]) % T.p for k in range(3)])
        for k, f in T.rounds()[2:]: s = T.rnd(s, k, f)
        return s[0]
    def Fpoly(self):
        T = self.T; p = T.p
        P = lambda c: nmod_poly([c % p], p)
        s = [nmod_poly([self.v0[k], self.v1[k]], p) for k in range(3)]
        mdsp = lambda s: [sum((s[j] * T.M[i][j] for j in range(3)), P(0)) for i in range(3)]
        s = mdsp(s)
        for k, f in T.rounds()[2:]:
            s = [s[i] + T.RC[k][i] for i in range(3)]
            s = [(s[i] ** 5) if (f or i == 0) else s[i] for i in range(3)]
            s = mdsp(s)
        return s[0]

def run(p, cseed, r, j, ncent, rng, verify_every=1):
    T = Toy(p, cseed, r); L = TLine(T, j)
    F = L.Fpoly(); D = F.degree()
    # sanity vs direct
    for _ in range(3):
        x = rng.randrange(p); assert int(F(x)) == L.F(x)
    nk, rho = L.inputs(rng.randrange(1, p))
    stats = dict(p=p, cseed=cseed, r=r, j=j, D=D, ncent=ncent, n_sq=collections.Counter(), n_nsq=collections.Counter(),
                 n_all=collections.Counter(), succ=0, alt_n=collections.Counter(), alt_succ=0, verified=0, verify_fail=0, zero_root=0)
    X = nmod_poly([0, 1], p)
    for it in range(ncent):
        c = rng.randrange(p)
        Fc = F.compose(nmod_poly([c, 1], p))
        co = [int(x) for x in Fc.coeffs()]
        g = nmod_poly([co[k] for k in range(1, len(co), 2)], p)
        if int(g.coeffs()[0]) == 0: stats['zero_root'] += 1
        Xh = X.pow_mod((p - 1) // 2, g)
        Gsq = g.gcd(Xh - 1); Gns = g.gcd(Xh + 1)
        stats['n_sq'][Gsq.degree()] += 1; stats['n_nsq'][Gns.degree()] += 1
        # all distinct roots in F_p (excluding root 0 ; zero_root is flagged)
        if Gsq.degree() >= 1:
            stats['succ'] += 1
            if it % verify_every == 0:
                S = Gsq.roots()[0][0]
                s = int(nmod(int(S), p).sqrt())
                assert s * s % p == int(S) % p
                outs = [L.inputs(pow((c + sg * s) % p, T.e5inv, p)) for sg in (1, -1)]
                ok = T.digest(*outs[0]) == T.digest(*outs[1]) and outs[0] != outs[1]
                stats['verified' if ok else 'verify_fail'] += 1
        # alternative: F(W)-F(W0), W0 random: distinct roots !=W0
        if it % ALT_EVERY: continue
        stats['alt_tried'] = stats.get('alt_tried', 0) + 1
        W0 = rng.randrange(p)
        A = F - int(F(W0))
        A, _ = divmod(A, nmod_poly([-W0 % p, 1], p))
        Xp = X.pow_mod(p, A)
        nal = A.gcd(Xp - X).degree()
        stats['alt_n'][nal] += 1
        if nal >= 1: stats['alt_succ'] += 1
    return stats

if __name__ == '__main__':
    p = int(sys.argv[1]); r = int(sys.argv[2]); ncent = int(sys.argv[3]); ncs = int(sys.argv[4]); outf = sys.argv[5]; ALT_EVERY = int(sys.argv[6]); seed0 = int(sys.argv[7])
    rng = random.Random(seed0)
    allst = []
    for cs in range(ncs):
        for j in range(3):
            t = time.time()
            st = run(p, 1000 + cs, r, j, ncent, rng)
            st['n_sq'] = dict(st['n_sq']); st['n_nsq'] = dict(st['n_nsq']); st['alt_n'] = dict(st['alt_n']); st['n_all'] = {}
            allst.append(st)
            print(f"p={p} cs={cs} j={j} r={r} D={st['D']} succ={st['succ']}/{ncent} alt={st['alt_succ']}/{st.get('alt_tried',0)} sq={st['n_sq']} verified={st['verified']} fail={st['verify_fail']} t={time.time()-t:.0f}s", flush=True)
            json.dump(allst, open(outf, 'w'))
