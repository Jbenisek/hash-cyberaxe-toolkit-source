'''Word-level test of "make T1 an input and solve for another word instead" on the exact relation set (ev.REL, 79
relations incl. K1.a1 ^ rol(K1.d1,16) ^ T1 = 0), outer system, F = {Y4,Y9,w8}.
For every k=1 design (B, g) of split_e3/designs.pkl that rebuilds on the outer system, and every released word u in B:
inputs F + (B - u) + {T1}  (same number of free words; T1 now chosen in range by construction).
  (a) does propagation complete with no guess (k=0)?
  (b) for every single guess word x: does F + (B-u) + {T1, x} complete (k=1, i.e. one 32-bit cycle in x)?
A usable "T1-input" design needs (a) or (b).  Worklist peeling (each relation solved when one word is unknown).'''

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
W = sorted(set(ev.WORDS) | {'T1'}); idx = {w: i for i, w in enumerate(W)}; NW = len(W)
RW = [[idx[w] for w in ev.wset(r)] for r in ev.REL]
INC = [[] for _ in range(NW)]
for i, ws in enumerate(RW):
    for w in ws: INC[w].append(i)
def prop(inputs):
    known = [False] * NW; unk = [len(ws) for ws in RW]; done = [False] * len(RW); checks = 0; q = []
    def mark(w):
        known[w] = True
        for i in INC[w]:
            unk[i] -= 1; q.append(i)
    for w in inputs:
        if not known[w]: mark(w)
    nk = sum(known)
    while q:
        i = q.pop()
        if done[i]: continue
        if unk[i] == 0: done[i] = True; checks += 1
        elif unk[i] == 1:
            done[i] = True
            w = next(x for x in RW[i] if not known[x]); mark(w); nk += 1
    return nk, checks, known
F = ('Y4', 'Y9', 'w8')
rows = pickle.load(open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3/designs.pkl'), 'rb'))
seen = set(); res = collections.Counter(); hits = []
for t1g, nl, g, B, *_ in rows:
    for u in B:
        Bs = tuple(sorted(set(B) - {u}))
        if Bs in seen: continue
        seen.add(Bs)
        base = [idx[w] for w in F + Bs + ('T1',)]
        nk, c0, known = prop(base)
        if nk == NW: res['k=0 complete'] += 1; hits.append(('k0', Bs, None, c0)); continue
        comp = 0
        for x in range(NW):
            if known[x]: continue
            nk2, c, _ = prop(base + [x])
            if nk2 == NW: comp += 1; hits.append(('k1', Bs, W[x], c))
        res['k=1 completes for %s guesses' % ('some' if comp else 'no')] += 1
print('distinct input sets F + (B - u) + {T1} tested:', len(seen))
print(dict(res))
for h in hits[:20]: print(h)
