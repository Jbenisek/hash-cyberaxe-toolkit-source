import sys, random, time, json, math
sys.path.insert(0, 'tests'); from fh import *
rng = random.Random(555)
f = to_poly(read_poly('out/m1_f.bin'))
print('f degree', f.degree(), 'monic', int(f[f.degree()]) == 1)
dv = 39062 - f.degree()
while True:
    v = rand_poly(rng, dv)
    if v.is_squarefree() and v.gcd(f).degree() == 0: break
t = time.time(); lead, fac = v.factor(); print('flint factor v_s', time.time() - t, flush=True)
degs = sorted(x.degree() for x, m in fac); print('v factor degrees', degs)
g = f * v; assert g.degree() == 39062
write_poly('tests/data/planted_full.bin', coeffs(g))
o, e, rc = run_wsl(['ddf', '--g', 'tests/data/planted_full.bin', '--check-every', '1', '--no-abort', '--out', 'out/planted'])
ok = True
l = 140; cutoff = 19531
for line in o.splitlines():
    j = json.loads(line)
    if j['stage'] == 'checkpoint':
        exp = sum(x for x in degs if x <= j['K'])
        if exp != j['gcd_degree']: ok = False; print('MISMATCH', j['K'], j['gcd_degree'], exp)
    if j['stage'] in ('done', 'output'): print(line)
print('PATTERN_MATCH', ok)
ff = to_poly(read_poly('out/planted_f.bin')); co = to_poly(read_poly('out/planted_cofactor.bin'))
print('leftover == f:', ff == f, ' cofactor == v:', co == v, ' f*cofactor == g:', ff * co == g)
