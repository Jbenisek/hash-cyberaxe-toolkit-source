'''Rotation-offset census of the cyclic component of every k=1 design (counter 2, T1 free) in split_e3/designs.pkl.
For each loop word W (depends on the solved word g) compute O(W) = set of r in Z_32 such that bit i of W reads bit
(i - r) of g (rol by k adds k; XOR / modular add take the union; add also brings carries from lower bits).
Width of a set = shortest cyclic arc covering it (0 = single offset = T-function-like in a rotated frame).
Also counts, per design: loop length, additions with a g-dependent operand, XOR merges of two g-dependent
operands with different offsets, and whether T1 depends on g.
usage: python offsets.py  (writes offsets_out.txt)'''

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, pickle, collections
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
REL = ev.REL
def arcw(S):
    S = sorted(set(x % 32 for x in S))
    if len(S) <= 1: return 0
    gaps = [(S[(j + 1) % len(S)] - S[j]) % 32 for j in range(len(S))]
    return 32 - max(gaps)
def analyse(d):
    O = {d.g: frozenset([0])}
    adds = 0; mixes = 0; addmix = 0; info = []
    for i, w in d.loop:
        r = REL[i]
        if r[0] == 'add':
            s = set(); gd = 0
            for x in r[1]:
                if x != w and x in O: s |= O[x]; gd += 1
            adds += 1; addmix += len(s) > 1 and gd > 1
            O[w] = frozenset(s); info.append((w, 'add', sorted(s)))
        else:
            ru = dict(r[1])[w]; s = set(); gd = 0
            for x, k in r[1]:
                if x != w and x in O: s |= {(o + k - ru) % 32 for o in O[x]}; gd += 1
            mixes += gd > 1 and len(s) > 1
            O[w] = frozenset(s); info.append((w, 'lin', sorted(s)))
    r = REL[d.chk]; cs = set()
    if r[0] == 'add':
        for x in r[1]:
            if x in O: cs |= O[x]
    else:
        for x, k in r[1]:
            if x in O: cs |= {(o + k) % 32 for o in O[x]}
    return O, sorted(cs), adds, mixes, addmix, info
if __name__ == '__main__':
    rows = pickle.load(open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3/designs.pkl'), 'rb'))
    F = ('Y4', 'Y9', 'w8'); res = []; skipped = 0
    for row in rows:
        g, B = row[2], row[3]
        if g not in ev.WORDS or any(w not in ev.WORDS for w in B):   # 7 designs use the trial word Y2
            skipped += 1; continue
        d = ev.Design(F, B, g)
        O, cs, adds, mixes, addmix, info = analyse(d)
        maxw = max(arcw(s) for s in O.values())
        t1 = d.g in d.dep['T1']   # T1 is off the loop but computed from it
        res.append((arcw(cs), len(cs), maxw, len(d.loop), adds, mixes, addmix, t1, g, B, cs))
    res.sort()
    out = open('offsets_out.txt', 'w')
    def p(*a):
        print(*a); print(*a, file=out)
    p('designs', len(res), 'skipped (trial word Y2 in the design)', skipped)
    p('check arc width histogram', sorted(collections.Counter(r[0] for r in res).items()))
    p('check |offset set| histogram', sorted(collections.Counter(r[1] for r in res).items()))
    p('T1 depends on g in', sum(r[7] for r in res), 'designs')
    p('distinct (g,B) loops by (width,|O|,loop len):', sorted(collections.Counter((r[0], r[1], r[3]) for r in res).items())[:30])
    for r in res[:25]:
        p('w=%d |O|=%d maxw=%d loop=%d adds=%d xormix=%d addmix=%d T1g=%s g=%s B=%s O=%s' % r)
