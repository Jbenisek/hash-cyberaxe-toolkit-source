"""Collect centre outcomes and verified collisions from logs/stats/seed_*.txt (+ dev logs); verify each collision twice
(big-int reference + organizer verifier) and write data/collisions.json and data/stats.json."""
import glob, json, os, re, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import poseidon_ref as ref
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', 'pareto_clone')))
from verifier.hash_functions import digest as org_digest
os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
centres = []      # one record per single-centre run (first centre only: avoids the stopping-rule bias)
colls = []
files = sorted(glob.glob(os.path.join(HERE, 'logs', 'r2_*.txt')))
for f in files:
    txt = open(f).read()
    m = re.search(r'^CENTRE 0 j=(\d) degG=(\d+) success=(\d) arith=(\d+) all=(\d+) sec=([\d.]+)', txt, re.M)
    if not m: continue          # run still in progress
    if 'SUMMARY' not in txt: continue
    seed = int(re.search(r'seed=(\d+)', txt).group(1))
    build = 'B'
    gm = re.search(r'gcd\(g, S\^h-1\) \(half-gcd\)\s+arith=\s*\d+ other=\s*\d+ total=\s*(\d+)', txt)
    rec = dict(build=build, gcd=int(gm.group(1)) if gm else None, seed=seed, j=int(m.group(1)), degG=int(m.group(2)), success=int(m.group(3)), all=int(m.group(5)), sec=float(m.group(6)))
    pk = re.search(r'heap_peak=(\d+)', txt); rec['heap_peak'] = int(pk.group(1))
    centres.append(rec)
    if rec['success']:
        v = {k: int(x, 16) for k, x in re.findall(r'COLLISION (\w+)\s+0x([0-9a-f]{64})', txt)}
        v.update(seed=seed, j=rec['j'], build=build)
        nk1, rho1, nk2, rho2 = v['nk1'], v['rho1'], v['nk2'], v['rho2']
        ok = ref.hash_reduced(nk1, rho1, 2) == ref.hash_reduced(nk2, rho2, 2) == v['digest'] and (nk1, rho1) != (nk2, rho2)
        ma = nk1.to_bytes(32, 'little') + rho1.to_bytes(32, 'little'); mb = nk2.to_bytes(32, 'little') + rho2.to_bytes(32, 'little')
        ok = ok and org_digest(ma, 'poseidon-orchard', 2) == org_digest(mb, 'poseidon-orchard', 2) and ma != mb
        v['verified'] = ok
        colls.append(v)
n = len(centres); k = sum(c['success'] for c in centres)
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d, (c + r) / d
lo, hi = wilson(k, n) if n else (0, 0)
hist = {}
for c in centres: hist[c['degG']] = hist.get(c['degG'], 0) + 1
byj = {j: [sum(1 for c in centres if c['j'] == j and c['success']), sum(1 for c in centres if c['j'] == j)] for j in range(3)}
stats = dict(centres=n, successes=k, rate=k / n if n else None, wilson95=[lo, hi], degG_histogram=hist, by_j=byj,
             all_verified=all(c['verified'] for c in colls), n_collisions=len(colls),
             all_values=sorted(set(c['all'] for c in centres if c['build'] == 'B')), heap_peaks=sorted(set(c['heap_peak'] for c in centres if c['build'] == 'B')),
             gcd_values=sorted(set(c['gcd'] for c in centres if c['build'] == 'B' and c['gcd'])), n_build_A=sum(1 for c in centres if c['build'] == 'A'), n_build_B=sum(1 for c in centres if c['build'] == 'B'))
json.dump(stats, open(os.path.join(HERE, 'data', 'stats.json'), 'w'), indent=1)
json.dump(colls, open(os.path.join(HERE, 'data', 'collisions.json'), 'w'), indent=1)
print(json.dumps(stats))
