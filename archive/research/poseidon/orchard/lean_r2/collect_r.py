"""Collect first-centre outcomes (per line) and verified collisions for target r (env R) from run logs.
Sources: logs/r<R>_*.txt and logs/ledger_r<R>.txt of this build, plus optional extra directories given in EXTRA (colon separated) holding
seed_*.txt logs of builds with identical arithmetic.  Writes data/sample_r<R>.json and data/collisions_r<R>.json.
Only the FIRST centre of each execution is counted (no stopping-rule bias)."""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import poseidon_ref as ref
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', 'pareto_clone')))
from verifier.hash_functions import digest as org_digest
R = int(os.environ.get('R', '2'))
os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)


def parse(path):
    txt = open(path).read()
    if 'SUMMARY' not in txt:
        return None
    m = re.search(r'^CENTRE 0 j=(\d) degG=(\d+) success=(\d)', txt, re.M)
    if not m:
        return None
    rec = dict(path=path, j=int(m.group(1)), degG=int(m.group(2)), success=int(m.group(3)))
    rec['halt'] = 'BUDGET HALT' in txt
    if rec['success']:
        v = {k: int(x, 16) for k, x in re.findall(r'COLLISION (\w+)\s+0x([0-9a-f]{64})', txt)}
        rec['coll'] = v
    sm = re.search(r'seed=(\d+)', txt)
    rec['seed'] = int(sm.group(1)) if sm else 0
    return rec


def verify(v, R):
    nk1, rho1, nk2, rho2, dg = v['nk1'], v['rho1'], v['nk2'], v['rho2'], v['digest']
    ok = ref.hash_reduced(nk1, rho1, R) == ref.hash_reduced(nk2, rho2, R) == dg and (nk1, rho1) != (nk2, rho2)
    ma = nk1.to_bytes(32, 'little') + rho1.to_bytes(32, 'little')
    mb = nk2.to_bytes(32, 'little') + rho2.to_bytes(32, 'little')
    da, db = org_digest(ma, 'poseidon-orchard', R), org_digest(mb, 'poseidon-orchard', R)
    return bool(ok and da == db and ma != mb and int.from_bytes(da, 'little') == dg)


own = sorted(glob.glob(os.path.join(HERE, 'logs', 'r%d_*.txt' % R))) + [os.path.join(HERE, 'logs', 'ledger_r%d.txt' % R)]
recs = [r for r in (parse(p) for p in own if os.path.exists(p)) if r]
extra_recs = []
for d in filter(None, os.environ.get('EXTRA', '').split(':')):
    for p in sorted(glob.glob(os.path.join(d, 'seed_*.txt'))):
        r = parse(p)
        if r:
            r['extra'] = d
            extra_recs.append(r)
by_j = {str(j): [0, 0] for j in range(3)}
for r in recs + extra_recs:
    by_j[str(r['j'])][1] += 1
    by_j[str(r['j'])][0] += r['success']
base = {}
if os.environ.get('BASE_STATS'):
    base = json.load(open(os.environ['BASE_STATS']))
    for j in range(3):
        k, n = base['by_j'][str(j)]
        by_j[str(j)][0] += k
        by_j[str(j)][1] += n
n_d192 = 0
if os.environ.get('D192'):
    for line in open(os.environ['D192']):
        if line.strip():
            row = json.loads(line)
            n_d192 += 1
            by_j['0'][1] += 1
            by_j['0'][0] += 1 if row['nonzero_square_roots'] > 0 and row['nonzero_square_roots'] <= 16 else 0
colls = []
if os.environ.get('BASE_COLL'):
    for v in json.load(open(os.environ['BASE_COLL'])):
        if v.get('verified'):
            colls.append(dict(v))
for p in own:
    if os.path.exists(p):
        txt = open(p).read()
        for blk in txt.split('COLLISION nk1 ')[1:]:
            blk = 'COLLISION nk1 ' + blk
            v = {k: int(x, 16) for k, x in re.findall(r'COLLISION (\w+)\s+0x([0-9a-f]{64})', blk[:600])}
            if len(v) == 6:
                sm = re.search(r'seed=(\d+)', txt)
                v.update(seed=int(sm.group(1)) if sm else 0, j=0 if os.environ.get('FIXED_LINE') == '1' else int(re.findall(r'CENTRE \d+ j=(\d)', txt)[-1]), build='this')
                v['verified'] = verify(v, R)
                colls.append(v)
for r in []:
    if r['success']:
        v = dict(r['coll'])
        v.update(seed=r['seed'], j=r['j'], build='this' if 'extra' not in r else 'fix')
        v['verified'] = verify(v, R)
        colls.append(v)
seen = set()
uniq = []
for v in colls:
    key = (v['nk1'], v['rho1'], v['nk2'], v['rho2'])
    if key not in seen and v.get('verified'):
        seen.add(key)
        uniq.append(v)
n_own = len(recs)
n_extra = len(extra_recs)
desc = ('Samples: %d executions of this build (one centre each, seeds in the logs, line j given by the seed; only the first centre of an execution is counted)' % n_own)
if n_extra:
    desc += ', %d executions of an earlier build with identical arithmetic whose halts are not looser than those of this build (degree cap 8 instead of 16 and tighter budgets, so a success there is a success here)' % n_extra
if base:
    desc += ', and %d executions of the first build of the program (same arithmetic, degree cap 8, larger budgets than ever reached)' % base['centres']
if n_d192:
    desc += ', and %d centres (line 0) whose odd-part polynomial was formed exactly and whose powering step was run on a GPU, counted as a success when the polynomial has between 1 and 16 nonzero square roots in the field (the gcd stage then returns the same factor)' % n_d192
desc += '. Every counted success was verified by a big-integer reference of the hash and by the organizer\'s hash implementation.'
json.dump(dict(by_j=by_j, desc=desc, n_own=n_own, n_extra=n_extra), open(os.path.join(HERE, 'data', 'sample_r%d.json' % R), 'w'), indent=1)
json.dump(uniq, open(os.path.join(HERE, 'data', 'collisions_r%d.json' % R), 'w'), indent=1)
print('by_j', by_j, 'collisions verified', len(uniq), 'own', n_own, 'extra', n_extra)
