'''For the k=1 sequential designs (counter 2, full system, F = E3 inputs): is T1 computable from B alone (filter before
the solve)?  Size of the cyclic loop: equations on the path from g to the check (evaluated per candidate g).'''
import random, sys, pickle
sys.dont_write_bytecode = True
import model
from kmin import greedy, minimise, sequential
from loopw import forward
eqs, words = model.system(2, False)
eqs = [(n, frozenset(s)) for n, s in eqs]; words = set(words)
F = ('Y4', 'Y9', 'w8', 'Y14'); dof = len(words) - len(eqs)
rng = random.Random(7); seen = set(); designs = set()
for _ in range(int(sys.argv[1])):
    K = frozenset(minimise(eqs, words, greedy(eqs, words, F, rng), F))
    if K in seen or len(K) - dof != 1: continue
    seen.add(K)
    for B, perm in sequential(eqs, words, F, set(K), dof): designs.add((tuple(sorted(B)), perm[0]))
rows = []
for B, g in sorted(designs):
    dep, order, checks = forward(eqs, set(F) | set(B) | {g})
    ci = checks[0][0]
    # loop: words depending on g needed to evaluate the check
    par = {w: [x for x in eqs[i][1] if x != w] for i, w in order}
    need, st = set(), [x for x in eqs[ci][1]]
    while st:
        x = st.pop()
        if x in need or x not in par or g not in dep[x]: continue
        need.add(x); st += par[x]
    t1g = g in dep['T1']
    pre = [w for _, w in order if g not in dep[w]]
    rows.append((t1g, len(need), g, B, eqs[ci][0], sorted(eqs[ci][1]), [w for _, w in order if w in need], len(pre)))
rows.sort()
print('designs', len(rows), ' T1 independent of g:', sum(not r[0] for r in rows))
for r in rows[:12]:
    print('T1 needs g: %s | loop eqs %d | g=%s B=%s | check eq "%s" over %s | loop path %s | words before g: %d' % r)
pickle.dump(rows, open('designs.pkl', 'wb'))
