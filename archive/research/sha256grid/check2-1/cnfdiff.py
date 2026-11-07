#!/usr/bin/env python3
"""check2-1: compare two DIMACS CNFs as clause multisets (literal order inside a clause ignored)."""
import sys
from collections import Counter

def load(p):
    hdr = None; cls = []
    with open(p) as f:
        for line in f:
            if line.startswith('c'): continue
            if line.startswith('p'): hdr = line.split(); continue
            lits = [int(t) for t in line.split()]
            assert lits[-1] == 0
            cls.append(tuple(sorted(lits[:-1])))
    return hdr, cls

a, b = sys.argv[1], sys.argv[2]
ha, ca = load(a); hb, cb = load(b)
print('headers', ha, hb)
A, B = Counter(ca), Counter(cb)
print('clauses', len(ca), len(cb), 'identical as multisets:', A == B, ' same order:', ca == cb)
onlyA = A - B; onlyB = B - A
print('only in first:', sum(onlyA.values()), ' only in second:', sum(onlyB.values()))
for c in list(onlyA)[:8]: print('  first-only', c)
for c in list(onlyB)[:8]: print('  second-only', c)
if ca != cb and A == B:
    i = next(i for i in range(len(ca)) if ca[i] != cb[i])
    print('first order difference at clause index', i)
