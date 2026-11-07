import json, sys, math, collections
def wilson(k, n, z=1.96):
    ph = k / n; d = 1 + z*z/n
    c = (ph + z*z/(2*n)) / d; h = z*math.sqrt(ph*(1-ph)/n + z*z/(4*n*n)) / d
    return c - h, c + h
def pois(lam, k): return math.exp(-lam) * lam**k / math.factorial(k)
def hist_report(name, cnt, lam, n):
    ks = sorted(set(list(cnt) + [0,1,2,3]))
    kmax = max(ks); 
    rows = []; chi = 0; dof = -1
    tail_obs = 0; tail_exp = 0
    print(f'  {name}: counts of k roots (obs / expected Poisson({lam}) x n):')
    for k in range(0, 5):
        o = cnt.get(k, 0); e = n * pois(lam, k)
        print(f'     k={k}: {o:6d} / {e:8.1f}')
    o4 = sum(v for kk, v in cnt.items() if kk >= 5); e4 = n * (1 - sum(pois(lam, k) for k in range(5)))
    print(f'     k>=5: {o4:5d} / {e4:8.2f}')
    # chi-square over bins 0,1,2,3,>=4
    obs = [cnt.get(k, 0) for k in range(4)] + [sum(v for kk, v in cnt.items() if kk >= 4)]
    exp = [n * pois(lam, k) for k in range(4)] + [n * (1 - sum(pois(lam, k) for k in range(4)))]
    chi = sum((o - e)**2 / e for o, e in zip(obs, exp))
    print(f'     chi2 (5 bins, 4 dof, no fitted param) = {chi:.2f}   (p=0.05 critical 9.49)')
    mean = sum(k*v for k, v in cnt.items()) / n
    print(f'     mean = {mean:.4f}  (expected {lam})')
for f in sys.argv[1:]:
    data = json.load(open(f))
    print('FILE', f)
    groups = collections.defaultdict(list)
    for st in data:
        groups[(st.get('p', 'real'), st.get('r'), st.get('D'), st.get('q'))].append(st)
    tot = collections.Counter(); totn = collections.Counter()
    if 'ncent' not in data[0]:   # real format
        n = len(data); succ = sum(1 for d in data if d['n_sq'] >= 1)
        sq = collections.Counter(d['n_sq'] for d in data); ns = collections.Counter(d['n_nsq'] for d in data)
        lo, hi = wilson(succ, n)
        print(f'  REAL p: centres={n} success={succ} rate={succ/n:.4f} Wilson95=[{lo:.3f},{hi:.3f}]  verified collisions={sum(1 for d in data if d.get("collision_verified"))}/{succ}, failures={sum(1 for d in data if "collision_verified" in d and not d["collision_verified"])}')
        hist_report('square roots', dict(sq), 0.5, n); hist_report('nonsquare roots', dict(ns), 0.5, n)
        print('  zero_root flagged:', sum(d['zero_root'] for d in data), ' deg g set:', set(d['degg'] for d in data))
        continue
    for key, sts in groups.items():
        n = sum(s['ncent'] for s in sts); succ = sum(s['succ'] for s in sts)
        sq = collections.Counter(); ns = collections.Counter(); al = collections.Counter()
        for s in sts:
            for k, v in s['n_sq'].items(): sq[int(k)] += v
            for k, v in s['n_nsq'].items(): ns[int(k)] += v
            for k, v in s['alt_n'].items(): al[int(k)] += v
        at = sum(s.get('alt_tried', 0) for s in sts); asucc = sum(s['alt_succ'] for s in sts)
        lo, hi = wilson(succ, n)
        print(f'  TOY key(p,r,D,q)={key}: centres={n}  success={succ} rate={succ/n:.4f} Wilson95=[{lo:.3f},{hi:.3f}] (theory 0.3935)  verified={sum(s["verified"] for s in sts)} verify_fail={sum(s["verify_fail"] for s in sts)} zero-root centres={sum(s["zero_root"] for s in sts)}')
        for s in sts:
            print(f'      j={s["j"]} cs={s["cseed"]}: {s["succ"]}/{s["ncent"]}')
        hist_report('square roots', dict(sq), 0.5, n); hist_report('nonsquare roots', dict(ns), 0.5, n)
        if at:
            lo, hi = wilson(asucc, at)
            print(f'  ALT F(W)-F(W0): tried={at} success={asucc} rate={asucc/at:.4f} Wilson95=[{lo:.3f},{hi:.3f}] (theory 0.6321)')
            hist_report('alt roots', dict(al), 1.0, at)
