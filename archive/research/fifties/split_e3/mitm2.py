'''Deeper separability test (any cut, not only the check the greedy order picks): for every k=1 design (B, g) and every
u in B, propagate separately from F+(B-u)+{g} and from F+(B-u)+{u}.  A two-list meet (2^32 + 2^32 work for ~2^32 roots,
O(1) per root) exists iff the two closures cover every word and exactly ONE equation links them.  Also the weaker
per-word count: how many equations are left unresolved by both closures (each extra one is a further 32-bit check).'''
import sys, pickle, collections
sys.dont_write_bytecode = True
import model
from kmin import propagate
eqs, words = model.system(2, False)
eqs = [(n, frozenset(s)) for n, s in eqs]; words = set(words)
F = ('Y4', 'Y9', 'w8', 'Y14')
rows = pickle.load(open('designs.pkl', 'rb'))
hist = collections.Counter(); best = None
for t1g, nl, g, B, cname, cwords, path, pre in rows:
    for u in B:
        k0 = set(F) | (set(B) - {u})
        A = propagate(eqs, k0 | {g})[0]; Bs = propagate(eqs, k0 | {u})[0]
        cover = (A | Bs) >= words
        link = [i for i, (_, s) in enumerate(eqs) if not (s <= A) and not (s <= Bs)]
        hist[(cover, len(link))] += 1
        if cover and (best is None or len(link) < best[0]): best = (len(link), g, u, B, [eqs[i][0] for i in link])
print('(closures cover all words, #linking equations): count over design x u ->', dict(sorted(hist.items())))
print('fewest linking equations with full cover:', best)
