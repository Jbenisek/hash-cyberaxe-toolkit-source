#!/usr/bin/env python3
"""check2-1: are two Step-1 CNFs the same formula up to renaming of auxiliary variables?
Primary variables (A/E/W word bits, from each CNF's map.json) and the constant variable 1 keep fixed labels;
every other variable is labelled by colour refinement over the clause structure. If the refined colouring is
discrete in both CNFs and the colour sets agree, the induced renaming is applied and the clause multisets are
compared exactly (a proof of identity up to renaming when it says True).
  python3 cnf_iso.py OLD.cnf NEW.cnf"""
import sys, json, hashlib
from collections import Counter, defaultdict

def load(p):
    cls = []; n = 0
    for line in open(p):
        if line[0] in 'c': continue
        if line[0] == 'p': n = int(line.split()[2]); continue
        l = [int(t) for t in line.split()][:-1]
        cls.append(l)
    wm = json.load(open(p + '.map.json'))['wm']
    prim = {1: 'T'}
    for k in ('A', 'E', 'W'):
        for i, w in wm[k].items():
            for b, lit in enumerate(w):
                if abs(lit) != 1: prim.setdefault(abs(lit), '%s%s.%d%s' % (k, i, b, '' if lit > 0 else '~'))
    return n, cls, prim

def H(x): return hashlib.blake2b(repr(x).encode(), digest_size=12).hexdigest()

def refine(n, cls, prim, rounds=40):
    col = {v: ('P', prim[v]) if v in prim else ('X',) for v in range(1, n + 1)}
    col = {v: H(c) for v, c in col.items()}
    occ = defaultdict(list)
    for ci, c in enumerate(cls):
        for l in c: occ[abs(l)].append(ci)
    prev = -1
    for r in range(rounds):
        sig = {}
        for v in range(1, n + 1):
            items = []
            for ci in occ[v]:
                c = cls[ci]
                me = [l for l in c if abs(l) == v][0] > 0
                others = tuple(sorted((l > 0, col[abs(l)]) for l in c if abs(l) != v))
                items.append((me, others))
            sig[v] = H((col[v], tuple(sorted(items))))
        col = sig
        k = len(set(col.values()))
        if k == prev: break
        prev = k
    return col, len(set(col.values()))

a, b = sys.argv[1], sys.argv[2]
na, ca, pa = load(a); nb, cb, pb = load(b)
print('vars', na, nb, 'clauses', len(ca), len(cb), 'primary vars', len(pa), len(pb), 'primary labels equal:', sorted(pa.values()) == sorted(pb.values()))
cola, ka = refine(na, ca, pa); colb, kb = refine(nb, cb, pb)
print('distinct colours', ka, 'of', na, '|', kb, 'of', nb, '| colour multisets equal:', Counter(cola.values()) == Counter(colb.values()))
if ka == na and kb == nb and set(cola.values()) == set(colb.values()):
    inv = {c: v for v, c in colb.items()}
    mp = {v: inv[c] for v, c in cola.items()}
    ta = Counter(tuple(sorted((mp[abs(l)] if l > 0 else -mp[abs(l)]) for l in c)) for c in ca)
    tb = Counter(tuple(sorted(c)) for c in cb)
    print('renamed clause multisets identical:', ta == tb)
else:
    canon = lambda cls, col: Counter(tuple(sorted((l > 0, col[abs(l)]) for l in c)) for c in cls)
    print('colouring not discrete; canonical clause multisets equal (WL-equivalent):', canon(ca, cola) == canon(cb, colb))
