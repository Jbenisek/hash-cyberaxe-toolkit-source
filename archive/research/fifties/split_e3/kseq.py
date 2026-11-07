'''Over many least-k guess sets with E3 forced (outer F={Y4,Y9,w8}), is any solvable one word at a time?
Also the "decoupled" variant: does some guess set give a check that, with the free words fixed, involves only ONE solved word?'''
import random, sys
sys.dont_write_bytecode = True
from kmin import systems, propagate, greedy, minimise, sequential
tries = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
full, fw, outer, ow = systems(1)
for name, eqs, words, F in (('outer', outer, ow, ('Y4', 'Y9', 'w8')), ('full', full, fw, ('Y4', 'Y9', 'w8', 'Y14'))):
    dof = len(words) - len(eqs); rng = random.Random(11); seen = {}
    for _ in range(tries):
        K = frozenset(minimise(eqs, words, greedy(eqs, words, F, rng), F))
        if K in seen: continue
        seen[K] = sequential(eqs, words, F, set(K), dof)
    byk = {}
    for K, s in seen.items():
        k = len(K) - dof; byk.setdefault(k, [0, 0]); byk[k][0] += 1; byk[k][1] += bool(s)
    print(name, 'F', F, 'distinct minimal guess sets by k: {k: [sets, sets with a sequential order]}', dict(sorted(byk.items())))
    ex = [(len(K) - dof, sorted(K - set(F)), s[0]) for K, s in seen.items() if s]
    for e in sorted(ex)[:4]: print('   seq example k=%d guesses %s -> free %s solve order %s' % (e[0], e[1], e[2][0], e[2][1]))
