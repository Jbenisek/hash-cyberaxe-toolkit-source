'''Separability of the single check (k=1 designs, counter 2, full system, F = E3 inputs): can B+g be split into two
groups so that every word of the check equation depends on one group only?  Then all solutions of the check over a
2^32 x 2^32 grid come from a list match in ~2^33 work (amortised O(1) per solution).'''
import pickle, sys, itertools
sys.dont_write_bytecode = True
import model
from loopw import forward
rows = pickle.load(open('designs.pkl', 'rb'))
eqs, words = model.system(2, False)
eqs = [(n, frozenset(s)) for n, s in eqs]
F = ('Y4', 'Y9', 'w8', 'Y14')
hits, n = [], 0
for t1g, nl, g, B, cname, cwords, path, pre in rows:
    dep, order, checks = forward(eqs, set(F) | set(B) | {g})
    ci, cdep = checks[0]
    ds = [dep[w] - set(F) for w in eqs[ci][1]]
    n += 1
    V = list(B) + [g]
    for r in range(1, len(V)):
        for G1 in itertools.combinations(V, r):
            G1 = set(G1); G2 = set(V) - G1
            if all(d <= G1 or d <= G2 for d in ds):
                hits.append((g, B, sorted(G1), cname, [(w, sorted(dep[w] - set(F))) for w in eqs[ci][1]]))
print('designs', n, 'separable splits', len(hits))
for h in hits[:5]: print(h)
# how many check words depend on ALL 7 basis words
full = sum(1 for t1g, nl, g, B, cname, cwords, path, pre in rows
           if any(len(forward(eqs, set(F)|set(B)|{g})[0][w] - set(F)) == 7 for w in cwords))
print('designs where some check word depends on all 7 basis words:', full)
