'''counter 2 (T1 free, filtered to [1,2^19)), FULL system, F = {Y4, Y9, w8, Y14} (E3 inputs; Y3 pinned).
For every k=1 sequential design (free B, solved g): the check equation's cone over B+g, and LOOP words u in B outside
that cone (moving u keeps the check, so no re-solve).  For each u: does it reach E1's inputs (Y12, Y1, w12, w5, Y6), T1, T0,
and how many equations does it touch (recompute cost per move)?'''
import random, sys
sys.dont_write_bytecode = True
import model
from kmin import propagate, greedy, minimise, sequential
E1IN = ('Y12', 'Y1', 'w12', 'w5', 'Y6')
def forward(eqs, known):
    known = set(known); dep = {w: {w} for w in known}; used = set(); order = []; checks = []
    ch = True
    while ch:
        ch = False
        for i, (_, s) in enumerate(eqs):
            if i in used: continue
            unk = [w for w in s if w not in known]
            if len(unk) == 1:
                w = unk[0]; known.add(w); used.add(i); dep[w] = set().union(*(dep[x] for x in s if x != w)); order.append((i, w)); ch = True
            elif not unk:
                used.add(i); checks.append((i, set().union(*(dep[x] for x in s)))); ch = True
    return dep, order, checks
if __name__ == "__main__":
    eqs, words = model.system(2, False)
    eqs = [(n, frozenset(s)) for n, s in eqs]; words = set(words)
    F = ('Y4', 'Y9', 'w8', 'Y14'); dof = len(words) - len(eqs)
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 1); seen = set(); designs = []
    for _ in range(int(sys.argv[1])):
        K = frozenset(minimise(eqs, words, greedy(eqs, words, F, rng), F))
        if K in seen or len(K) - dof != 1: continue
        seen.add(K)
        for B, perm in sequential(eqs, words, F, set(K), dof):
            designs.append((tuple(B), perm[0]))
    designs = sorted(set(designs))
    print('k=1 sets', len(seen), 'sequential designs', len(designs))
    best = []
    for B, g in designs:
        dep, order, checks = forward(eqs, set(F) | set(B) | {g})
        assert len(checks) == 1
        cdep = checks[0][1] - set(F)
        loop = [u for u in B if u not in cdep]
        for u in loop:
            touched = [w for _, w in order if u in dep[w]]
            reach = [t for t in E1IN if u in dep.get(t, set())]
            best.append((-len(reach), 'T1' not in touched, len(touched), u, g, B, sorted(cdep), reach, 'T1' in touched, 'T0' in touched))
    best.sort()
    print('designs with a loop word:', len({(b[5], b[4]) for b in best}), ' loop (u) entries:', len(best))
    for b in best[:15]:
        print('  u=%-6s touches %2d eqs  E1 inputs moved %s  T1 moved %s T0 moved %s | g=%s B=%s check cone %s' % (b[3], b[2], b[7], b[8], b[9], b[4], list(b[5]), b[6]))
    # also: count designs where the check cone is small
    cones = sorted({(len(forward(eqs, set(F) | set(B) | {g})[2][0][1] - set(F)), B, g) for B, g in designs})
    print('smallest check cones (#words of B+g in the check):', [(c[0], c[2]) for c in cones[:10]])
