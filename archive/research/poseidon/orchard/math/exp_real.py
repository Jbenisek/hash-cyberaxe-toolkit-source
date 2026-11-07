import sys, time, json
from fpoly import *
r = int(sys.argv[1]); ncent = int(sys.argv[2]); seed = int(sys.argv[3]); outf = sys.argv[4]
random.seed(seed)
Fs = {}
res = []
t0 = time.time()
for it in range(ncent):
    j = it % 3
    if j not in Fs:
        Fs[j] = (Line(j), build_F(Line(j), r))
    L, F = Fs[j]
    c = random.randrange(p)
    Fc = F.compose(R([c, 1]))
    co = Fc.coeffs()
    g = R([co[k] for k in range(1, len(co), 2)])          # h(s) = 2 s g(s^2)  (factor 2 dropped)
    Xp = R([0, 1]).pow_mod((p - 1) // 2, g)
    Gsq = g.gcd(Xp - 1); Gns = g.gcd(Xp + 1)
    rec = dict(j=j, c=hex(c), degg=g.degree(), n_sq=Gsq.degree(), n_nsq=Gns.degree(), zero_root=int(g.coeffs()[0]) == 0)
    if rec['n_sq'] >= 1:
        S = Gsq.roots()[0][0]
        s = int(S.sqrt())
        assert s * s % p == int(S)
        W1, W2 = (c + s) % p, (c - s) % p
        out = []
        for W in (W1, W2):
            tau = pow(W, E5INV, p)
            assert pow(tau, 5, p) == W
            out.append(L.inputs(tau))
        d1, d2 = digest(*out[0], r), digest(*out[1], r)
        rec['collision_verified'] = (d1 == d2 and out[0] != out[1] and all(0 <= v < p for o in out for v in o))
        rec['pair'] = [[hex(v) for v in o] for o in out]
    res.append(rec)
    json.dump(res, open(outf, 'w'))
    print(it, rec['j'], rec['degg'], rec['n_sq'], rec['n_nsq'], rec.get('collision_verified'), f'{time.time()-t0:.0f}s', flush=True)
