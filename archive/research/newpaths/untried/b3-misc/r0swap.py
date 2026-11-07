#!/usr/bin/env python3
"""b3-misc/r0swap.py -- cell r0 x cost, lever test.

The front line's omega test (omega = Y3 + y + w8) needs 8 member-level lines,
3 of them round-0 inverse lines (D0.d1, D0.a1, w8), because w8 depends on the
member y.  Lever: re-choose the outer words so that w8 is itself an outer word;
then omega costs one add per member and no round-0 line runs before the filter.
Test: replace one or two of the seven outer words (map 2.5) by w8 (and any
other word), keep y = Y4 (member) and c1 = E1.c1 (trial), t_lo solved, and ask
whether the whole system still resolves one assignment at a time, and at what
member-level / trial-level line counts.
"""

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

import sys, random, itertools, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc'))
import split as SP

OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc')


def setup():
    rng = random.Random(7)
    T, st, m, _ = SP.traced_compress([rng.getrandbits(32) for _ in range(16)], 5, 55, 3)
    calls0 = {'K0', 'K1', 'K2', 'K3', 'D0', 'D1', 'D2', 'D3'}
    calls1 = {'C0', 'C1', 'C2', 'C3'}
    rels, e1 = [], 0
    for (c, k, ids) in T.rel:
        if c in calls0 or c in calls1:
            rels.append((c, ids))
        elif c == 'E1' and e1 < 3:
            rels.append((c, ids)); e1 += 1
    byname = {}
    for wid, n in enumerate(T.name):
        byname[n] = wid
        for a in T.alias.get(wid, []):
            byname.setdefault(a, wid)
    fixed = set(range(16)) - {12}
    fixed |= {m[4], m[13], m[14], m[15]}
    X = st['X']
    fixed |= {X[3], X[7], X[11], X[15]}
    return T, rels, byname, fixed, calls0


def propagate(rels, fixed, free):
    dep = {w: frozenset() for w in fixed}
    dep.update(free)
    used = [False] * len(rels)
    det = {}
    changed = True
    while changed:
        changed = False
        for i, (c, ids) in enumerate(rels):
            if used[i]:
                continue
            unk = [w for w in ids if w not in dep]
            if len(unk) == 1:
                dep[unk[0]] = frozenset().union(*(dep[w] for w in ids if w in dep))
                used[i] = True; det[unk[0]] = c; changed = True
    unresolved = sum(1 for u in used if not u)
    return dep, det, unresolved


def evaluate(T, rels, byname, fixed, calls0, outer_names):
    free = {}
    for n in outer_names:
        w = byname[n]
        if w in fixed or w in free:
            return None
        free[w] = frozenset([n])
    for n, tag in (('Y4', 'y'), ('E1.c1', 'c1')):
        w = byname[n]
        if w in free:
            return None
        free[w] = frozenset([tag])
    dep, det, unres = propagate(rels, fixed, free)
    allw = {w for c, ids in rels for w in ids}
    if unres or any(w not in dep for w in allw):
        return {'resolved': False, 'unresolved': unres}
    mem = [w for w, c in det.items() if 'y' in dep[w] and 'c1' not in dep[w]]
    tri = [w for w, c in det.items() if 'c1' in dep[w]]
    r = {'resolved': True,
         'member_lines': len(mem), 'member_r0': sum(1 for w in mem if det[w] in calls0),
         'trial_lines': len(tri), 'trial_r0': sum(1 for w in tri if det[w] in calls0),
         't_from_trial': 'c1' in dep[byname['v12']],
         'w8_dep': sorted(dep[byname['w8']]),
         'E3_trial': [n for n in ('Y4', 'Y9', 'Y14', 'w8') if 'c1' in dep[byname[n]]],
         'E3_member': [n for n in ('Y4', 'Y9', 'Y14', 'w8') if 'y' in dep[byname[n]]]}
    return r


def main():
    log = []
    p = lambda *a: (print(*a, flush=True), log.append(' '.join(str(x) for x in a)))
    T, rels, byname, fixed, calls0 = setup()
    base = ['C0.d1', 'D2.a1', 'D2.b1', 'S11', 'S4', 'X9', 'w6']
    p('front line set:', evaluate(T, rels, byname, fixed, calls0, base))
    names = sorted({SP.nm(T, w).split('(')[0] for c, ids in rels for w in ids} - {T.name[w] for w in fixed})
    p('candidate words:', len(names))
    single, double = [], []
    for o in base:
        s = [x for x in base if x != o] + ['w8']
        r = evaluate(T, rels, byname, fixed, calls0, s)
        single.append((o, r))
        p('swap %-6s -> w8:' % o, r)
    for o1, o2 in itertools.combinations(base, 2):
        keep = [x for x in base if x not in (o1, o2)]
        for nw in names:
            if nw in base or nw == 'w8':
                continue
            r = evaluate(T, rels, byname, fixed, calls0, keep + ['w8', nw])
            if r and r.get('resolved'):
                double.append(((o1, o2, nw), r))
    p('double swaps (two outer words out, w8 + one other word in) that resolve: %d' % len(double))
    good = [d for d in double if not d[1]['E3_trial'] or d[1]['E3_trial'] == ['Y14']]
    good.sort(key=lambda d: (d[1]['member_lines'], d[1]['trial_lines']))
    for d in good[:12]:
        p('  ', d)
    # any 7-subset at all with w8 outer? (w8 + 6 words from the front-line set plus any one word)
    json.dump({'single': single, 'double': [(list(k), v) for k, v in double]}, open(OUT + r'\r0swap_out.json', 'w'), indent=1)
    open(OUT + r'\r0swap_out.txt', 'w').write('\n'.join(log) + '\n')


if __name__ == '__main__':
    main()
