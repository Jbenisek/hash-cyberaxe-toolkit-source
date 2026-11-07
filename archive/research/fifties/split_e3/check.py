'''Read GPU roots, rebuild every solution exactly (Python propagation of the design), verify on the real 2-round
compression (compress2, counter T0 + 2^32*T1, flags 3) that E3's inputs equal the forced ones and the half-collision
holds, and collect roots-per-target, T1 range and E1 inputs.  usage: python check.py <seed> [max_verify]'''
import sys, json, math, collections
sys.dont_write_bytecode = True
from ev import Design, DESIGN, verify, M
d = Design(*DESIGN)
seed = int(sys.argv[1]); maxv = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
inst = {i['id']: i for i in json.load(open('inst_%d.json' % seed))}
roots = {}
for line in open('roots_%d.txt' % seed):
    p = line.split(); roots[int(p[0])] = (int(p[1]), [int(x, 16) for x in p[2:]])
t1all = []
hist = collections.Counter(); gen_found = 0; gen_n = 0; nver = 0; bad = 0; t1_ok = []; e1 = []; total_roots = 0
for pid, (c, rs) in sorted(roots.items()):
    it = inst[pid]
    if it['gen']:
        gen_n += 1; gen_found += it['g_true'] in rs
        continue
    hist[c] += 1; total_roots += c
    for g in rs:
        start = dict(it['E3'], **it['B']); start[d.g] = g
        v, h = d.run(start)
        if not h: bad += 1; continue
        if nver < maxv or v['T1'] < (1 << 19):
            ok, info = verify(v, it['E3'], it['Y14']); nver += 1
            if not ok: bad += 1; continue
            e1.append((it['e3'], info['E1'], v['T1']))
        if 0 < v['T1'] < (1 << 19): t1_ok.append((pid, g, v['T1']))
        t1all.append(v['T1'])
nB = sum(hist.values())
print('seed', seed, 'random-B instances', nB, 'generating instances with true g among roots %d/%d' % (gen_found, gen_n))
print('roots per instance histogram', dict(sorted(hist.items())), 'mean %.4f' % (total_roots / nB), 'P(0) %.4f' % (hist[0] / nB))
print('roots rebuilt and verified on compress2: %d, failures %d' % (nver, bad))
print('roots with T1 in [1, 2^19): %d of %d (expected %.2f at 2^-12.95)' % (len(t1_ok), total_roots, total_roots * 2 ** -12.95), t1_ok[:5])
for lim in (28, 24, 22, 20, 19):
    k = sum(1 for t in t1all if t < (1 << lim))
    print('  T1 < 2^%d: %d/%d = 2^%.2f (uniform 2^%d)' % (lim, k, len(t1all), math.log2(k / len(t1all)) if k else -99, lim - 32))
json.dump([[a, list(b), c] for a, b, c in e1], open('e1_%d.json' % seed, 'w'))
