import time, sys, json
from u2lib import *
random.seed(2)
t0 = time.time()
def forms(kmax):
    """F[k][j] = univariate poly in tau=U/V (V=1): top form of lane j after R_k, formal degree 5^k"""
    F = [[[MDS[j][1] % P, MDS[j][0] % P] for j in range(3)]]
    for k in range(1, kmax + 1):
        prev = [p5(f) for f in F[-1]]
        new = []
        for j in range(3):
            acc = []
            for i in range(3): acc = padd(acc, [MDS[j][i] * c % P for c in prev[i]])
            new.append(acc)
        F.append(new)
    return F
F = forms(3)
out = {}
for k in range(0, 4):
    for j in range(3):
        f = F[k][j]; deg = len(f) - 1
        info = dict(formal_degree=5**k, tau_degree=deg, nonzero_coeffs=sum(1 for c in f if c))
        d = pgcd(f, pderiv(f)); info['squarefree'] = (len(d) == 1)
        print(f"form R{k} lane {j}: tau-degree {deg} (formal {5**k}); nonzero coefficients {info['nonzero_coeffs']}/{5**k+1}; squarefree={info['squarefree']}; t={time.time()-t0:.1f}s", flush=True)
        if k <= 2:
            rts = roots_Fp(f); info['roots'] = [hex(r) for r in rts]
            print(f"   F_p roots of f(tau): {len(rts)} ; V=0 direction extra root if degree dropped: {int(deg < 5**k)} => linear factors of the (nk,rho)-form: {len(rts)+int(deg<5**k)}", flush=True)
            dd = ddf(f); info['ddf'] = dd
            print(f"   distinct-degree pattern {{factor degree: total degree}}: {dd}", flush=True)
        else:
            h = ppowmod([0, 1], P, f); g = pgcd(f, psub(h, [0, 1])); info['n_roots'] = len(g) - 1
            print(f"   F_p roots of f(tau) (distinct): {len(g)-1} ; t={time.time()-t0:.1f}s", flush=True)
            if len(g) - 1 > 0:
                info['roots'] = [hex(r) for r in roots_Fp(f)]
        out[f"R{k}_lane{j}"] = info
json.dump(out, open('q2_forms.json', 'w'), indent=1)
print("--- gcds of forms (non-trivial degree only) ---")
names = [(k, j) for k in range(4) for j in range(3)]
for x in range(len(names)):
    for y in range(x + 1, len(names)):
        (k1, j1), (k2, j2) = names[x], names[y]
        g = pgcd(F[k1][j1], F[k2][j2])
        if len(g) > 1: print(f"  gcd(F_R{k1}_lane{j1}, F_R{k2}_lane{j2}) has degree {len(g)-1}")
print("(all other pairs coprime)")
