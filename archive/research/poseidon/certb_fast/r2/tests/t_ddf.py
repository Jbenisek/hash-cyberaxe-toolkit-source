import sys, random, time, json, math
sys.path.insert(0, 'tests'); sys.path.insert(0, '.'); sys.path.insert(0, r'../../../../3rd_openai_workspace/luna3')
from fh import *
d = int(sys.argv[1]); kind = sys.argv[2] if len(sys.argv) > 2 else 'natural'
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
rng = random.Random(9000 + d + seed)
os.makedirs('tests/data', exist_ok=True)
def random_irreducible(e):
    t = 0
    while True:
        t += 1
        f = R([rng.randrange(P) for _ in range(e)] + [1])
        if f.is_irreducible(): return f
if kind == 'natural':
    while True:
        g = rand_poly(rng, d)
        if g.is_squarefree(): break
    t = time.time(); lead, fac = g.factor(); print('flint factor_s', time.time() - t, flush=True)
    degs = sorted(f.degree() for f, m in fac); assert all(m == 1 for f, m in fac)
    planted = None
elif kind == 'planted':
    big = int(sys.argv[4]) if len(sys.argv) > 4 else (d // 2 + 11)
    t = time.time(); u = random_irreducible(big); print('irreducible search_s', time.time() - t, flush=True)
    while True:
        v = rand_poly(rng, d - big)
        if v.is_squarefree() and v.gcd(u).degree() == 0: break
    t = time.time(); lead, fac = v.factor(); print('flint factor v_s', time.time() - t, flush=True)
    degs = sorted([big] + [f.degree() for f, m in fac]); g = u * v; planted = (u, v)
print('d', d, 'factor degrees', degs if len(degs) < 40 else (degs[:20], '...', degs[-12:]))
gp = 'tests/data/ddf_g%d_%s_%d.bin' % (d, kind, seed)
write_poly(gp, coeffs(g))
cutoff = d // 2
l = math.ceil(d ** (0.5 * (1.0 - math.log(2.0) / math.log(d))))
args = ['ddf', '--g', gp, '--check-every', '1', '--no-abort', '--cutoff', str(d - 1), '--out', gp[:-4]]
t = time.time(); o, e, rc = run_wsl(args); print('engine wall_s', time.time() - t, 'rc', rc, e[-300:])
ok = True
for line in o.splitlines():
    j = json.loads(line)
    if j['stage'] == 'checkpoint':
        K = j['K']; exp = sum(x for x in degs if x <= K)
        if j['gcd_degree'] != exp: ok = False; print('MISMATCH at K', K, j['gcd_degree'], exp)
    elif j['stage'] in ('start', 'done'): print(line)
print('PATTERN_MATCH', ok)
# default run (cutoff d//2, early abort) and compare outputs
args = ['ddf', '--g', gp, '--check-every', '3', '--out', gp[:-4]]
o, e, rc = run_wsl(args); res = [json.loads(x) for x in o.splitlines()]
done = [x for x in res if x['stage'] == 'done'][0]; print(json.dumps(done))
exp_big = [x for x in degs if x > cutoff]
exp_res = sum(x for x in degs if x > cutoff) if exp_big else None
print('expected leftover degree(s) >cutoff', exp_big, 'engine residual>cutoff', done['residual_gt_cutoff'], done['residual_degree'])
if exp_big:
    assert done['residual_degree'] == exp_big[0] or done['aborted_early'] is False
    f = to_poly(read_poly(gp[:-4] + '_f.bin')); co = to_poly(read_poly(gp[:-4] + '_cofactor.bin'))
    print('f*cofactor==g', f * co == g, 'f irreducible', f.is_irreducible(), 'deg', f.degree())
    if planted: print('f==u', f == planted[0], 'cofactor==v', co == planted[1])
else:
    print('no big factor; engine aborted_early', done['aborted_early'])
