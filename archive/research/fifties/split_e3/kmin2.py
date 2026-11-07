'''counter 2 (T1 = high counter word free, must be < 2^19 when computed): least k and sequential orders with E3 forced.'''
import random, sys
sys.dont_write_bytecode = True
import model
from kmin import TRIAL, propagate, greedy, minimise, sequential
eqs, words = model.system(2, False)
full = [(n, frozenset(s)) for n, s in eqs]; fw = set(words)
outer = [(n, s) for n, s in full if not s & TRIAL]; ow = fw - TRIAL
for name, E, W, F in (('outer c2', outer, ow, ('Y4', 'Y9', 'w8')), ('full c2', full, fw, ('Y4', 'Y9', 'w8', 'Y14')),
                      ('outer c2 +T1 kept', outer, ow, ('Y4', 'Y9', 'w8', 'T1'))):
    dof = len(W) - len(E); rng = random.Random(3); seen = {}
    for _ in range(int(sys.argv[1])):
        K = frozenset(minimise(E, W, greedy(E, W, F, rng), F))
        if K not in seen: seen[K] = sequential(E, W, F, set(K), dof)
    byk = {}
    for K, s in seen.items():
        k = len(K) - dof; byk.setdefault(k, [0, 0]); byk[k][0] += 1; byk[k][1] += bool(s)
    print(name, 'DOF', dof, 'F', F, '{k: [sets, sequential]}', dict(sorted(byk.items())))
    for K, s in seen.items():
        if s: print('   seq: k=%d free %s order %s' % (len(K) - dof, s[0][0], s[0][1])); break
