"""Summarise K3 solution records (A delta D nsol hit) from k3gpu: distinct deltas, 2-adic valuations,
per-delta multiplicity.  Usage: python k3recs.py FILE"""
import sys, collections
recs = []
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) >= 5:
        recs.append((int(p[0], 16), int(p[1], 16), int(p[2], 16), int(p[3]), int(p[4])))
def v2(x):
    return (x & -x).bit_length() - 1 if x else 32
print('records', len(recs))
if recs:
    dc = collections.Counter(r[1] for r in recs)
    print('distinct delta', len(dc), 'top', [(hex(d), c) for d, c in dc.most_common(8)])
    print('v2(delta) hist', sorted(collections.Counter(v2(r[1]) for r in recs).items()))
    print('v2(D) hist', sorted(collections.Counter(v2(r[2]) for r in recs).items()))
    print('popcount(delta) hist', sorted(collections.Counter(bin(r[1]).count('1') for r in recs).items()))
    print('distinct D', len(set(r[2] for r in recs)))
    print('hits', sum(r[4] for r in recs))
    print('nsol (log2) hist', sorted(collections.Counter(r[3].bit_length() - 1 for r in recs).items()))
    for r in recs[:10]:
        print('  A %08x delta %08x D %08x nsol %d' % r[:4])
