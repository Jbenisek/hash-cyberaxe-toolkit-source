# diff_prog.py - decision equivalence of the derivative's counted program (work/A/vt38.py) with the base program
# (37742a53) on designed buckets.  Same chaining value, same variants, same G words, each in its own entry format; compared:
# table requests, the full sequence of stage marks (W7, E17, A17, A17int, rows 18..37), the success (block, entry), the
# E17 values seen, and the counters NE, NW, N1.
#  part 1: SMC successes of the estimator replica (own seeds), each forced as the chaining value; the bucket holds a decoy,
#          the success entry with its true G word, and the same variant with K other G words (live and dead);
#  part 2: random chaining values, buckets of 1..6 embedded valid variants with random G words, all 4 lanes.
import sys, os, random, importlib.util
W = os.path.dirname(os.path.abspath(__file__)); sys.dont_write_bytecode = True
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
B = load('vtbase', os.path.join(W, 'basecopy', 'vt38.py')); N = load('vtnew', os.path.join(W, sys.argv[1] if len(sys.argv) > 1 else 'A', 'vt38.py'))
NREP = int(sys.argv[2]) if len(sys.argv) > 2 else 20; K = 6; M = B.M
def bent(a0, a1, a2, a2i, gi): return (B.c7of(B.variant(a0, a1, a2)) + (1 << 32), a1 | B.S0(a1) << 32 | (B.A2T + 2 * a2i) << 64, B.gaddr(gi))
progs = {}
def prog(mod, q):
    k = (mod.__name__, q)
    if k not in progs: progs[k] = mod.allocated_program(list(range(4 * q, 4 * q + 4)))
    return progs[k]
TB, TN = B.tables(), N.tables()
def run(mod, tab, q, cv, buckets):
    p, mp = prog(mod, q); m = mod.Machine([1, 2], lambda j, y, z: buckets.get(j, []), tab, cvforce=cv); m.run(p)
    e17 = [x & M for x in (m.obs[1::2] if mod is B else m.obs)]
    return dict(trace=m.trace, marks=m.marks, succ=None if m.succ is None else (m.succ[0], m.succ[1] & ((1 << 64) - 1)), e17=e17,
                cnt=tuple(m.r.get(mp.get(r, r), 0) for r in ('NE', 'NW', 'N1')))
stats = dict(cases=0, mism=0, succ=0, e17=0, a17=0, a17int=0, deep=0, w7=0)
def compare(q, cv, bb, bn):
    x = run(B, TB, q, cv, bb); y = run(N, TN, q, cv, bn); stats['cases'] += 1
    if x != y:
        stats['mism'] += 1
        if stats['mism'] < 4: print('MISMATCH', {k: (x[k], y[k]) for k in x if x[k] != y[k]})
    for k, mk in (('w7', 'W7'), ('e17', 'E17'), ('a17', 'A17'), ('a17int', 'A17int')): stats[k] += x['marks'].count(mk)
    stats['deep'] += sum(1 for t in x['marks'] if isinstance(t, tuple)); stats['succ'] += x['succ'] is not None
rr = random.Random(20261010); SV = B.sample_variants(); EV = B.entry_variants(); nsucc = 0
for rep in range(NREP):
    z, pairs, bad = B.smc_replicate(B.Shake('r38d-diff|%d' % rep), SV); assert bad == 0
    for cv, mx, my, (a0, a1, a2) in pairs:
        nsucc += 1; j = B.A0L.index(a0); a2i = B.A2L.index(a2); q = j // 4; g0 = B.GSET[B.w16_closed(cv, a0, a1, a2)]
        gs = [g0] + rr.sample([g for g in range(32) if g != g0], K)
        eb = [bent(a0, a1, a2, a2i, g) for g in gs[1:]] + [bent(a0, a1, a2, a2i, g0)]; en = [N.mkent(a0, a1, a2, a2i, g) for g in gs[1:]] + [N.mkent(a0, a1, a2, a2i, g0)]
        db = (eb[-1][0] ^ 0x5a5a5,) + eb[-1][1:]; dn = (en[-1][0] ^ 0x5a5a5,) + en[-1][1:]
        compare(q, cv, {j: [db] + eb}, {j: [dn] + en})
print('part 1: %d SMC successes from %d replicates' % (nsucc, NREP), stats, flush=True)
for t in range(int(sys.argv[3]) if len(sys.argv[3:]) else 400):
    cv = [rr.getrandbits(32) for _ in range(8)]; q = rr.randrange(64); bb, bn = {}, {}
    for j in range(4 * q, 4 * q + 4):
        for _ in range(rr.randrange(0, 7)):
            a1, a2i = EV[j]
            g = rr.randrange(32); bb.setdefault(j, []).append(bent(B.A0L[j], a1, B.A2L[a2i], a2i, g)); bn.setdefault(j, []).append(N.mkent(B.A0L[j], a1, B.A2L[a2i], a2i, g))
    compare(q, cv, bb, bn)
print('part 1+2:', stats)
print('EQUIVALENT' if stats['mism'] == 0 else 'NOT EQUIVALENT')
