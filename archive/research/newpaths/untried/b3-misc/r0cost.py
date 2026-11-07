#!/usr/bin/env python3
"""b3-misc/r0cost.py -- cell r0 x cost.

Using the front line's free words as listed in BLAKE3_2ROUND_MAP.md 2.5
(seven outer words C0.d1, D2.a1, D2.b1, S11, S4, X9, w6; member y = Y4;
trial word c1 = E1.c1; counter t_lo free and solved), propagate the word
relations of round 0 + round-1 columns + E1's first half, one assignment at
a time, and classify every relation by what it depends on:
  context  - outer words only (run once per context)
  member   - needs y but not c1 (run per outer step)
  trial    - needs c1 (run per trial / inside the joint solver)
Then count round-0 relations in each class. This bounds what any saving in the
round-0 inverse step can be worth, given the map's charged rows.
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

import sys, json, math
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc'))
import random
import split as SP

OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc')


def main():
    log = []
    p = lambda *a: (print(*a, flush=True), log.append(' '.join(str(x) for x in a)))
    rng = random.Random(7)
    T, st, m, _ = SP.traced_compress([rng.getrandbits(32) for _ in range(16)], 5, 55, 3)
    calls0 = {'K0', 'K1', 'K2', 'K3', 'D0', 'D1', 'D2', 'D3'}
    calls1 = {'C0', 'C1', 'C2', 'C3'}
    rels = []
    e1 = 0
    for (c, k, ids) in T.rel:
        if c in calls0 or c in calls1:
            rels.append((c, ids))
        elif c == 'E1' and e1 < 3:          # E1.a1, E1.d1, E1.c1
            rels.append((c, ids)); e1 += 1
    byname = {}
    for wid, n in enumerate(T.name):
        byname[n] = wid
        for a in T.alias.get(wid, []):
            byname.setdefault(a, wid)
    fixed = set(range(16)) - {12}
    fixed |= {m[4], m[13], m[14], m[15]}
    X = st['X']; Y = st['Y']
    fixed |= {X[3], X[7], X[11], X[15]}
    # constants first (propagate), recording nothing
    dep = {w: frozenset() for w in fixed}
    outer = ['C0.d1', 'D2.a1', 'D2.b1', 'S11', 'S4', 'X9', 'w6']
    free = {byname[n]: frozenset([n]) for n in outer}
    free[byname['Y4']] = frozenset(['y'])
    free[byname['E1.c1']] = frozenset(['c1'])
    for w in free:
        assert w not in fixed, T.name[w]
    dep.update(free)
    order = []
    used = [False] * len(rels)
    changed = True
    while changed:
        changed = False
        for i, (c, ids) in enumerate(rels):
            if used[i]:
                continue
            unk = [w for w in ids if w not in dep]
            if len(unk) == 1:
                d = frozenset().union(*(dep[w] for w in ids if w in dep))
                dep[unk[0]] = d
                used[i] = True
                order.append((c, unk[0], d))
                changed = True
    left = [(c, [SP.nm(T, w) for w in ids if w not in dep]) for i, (c, ids) in enumerate(rels) if not used[i]]
    unsolved_words = sorted({w for i, (c, ids) in enumerate(rels) if not used[i] for w in ids if w not in dep})
    checks = [(c, ids) for i, (c, ids) in enumerate(rels) if not used[i] and all(w in dep for w in ids)]
    p('relations %d, determined by propagation %d, left %d (unsolved words %d, consistency checks %d)'
      % (len(rels), len(order), len(left), len(unsolved_words), len(checks)))
    for c, ws in left[:40]:
        p('  left:', c, ws)
    cls = lambda d: 'trial' if 'c1' in d else ('member' if 'y' in d else ('context' if d else 'const'))
    table = {}
    for c, w, d in order:
        rnd = 'r0' if c in calls0 else ('r1c' if c in calls1 else 'E1')
        table.setdefault((rnd, cls(d)), []).append('%s:%s' % (c, SP.nm(T, w)))
    for key in sorted(table):
        p('%s %-7s %3d  %s' % (key[0], key[1], len(table[key]), ' '.join(table[key])))
    for nmx in ('Y4', 'Y9', 'Y14', 'w8', 'Y1', 'Y6', 'Y12', 'w12', 'w5', 'v12'):
        w = byname[nmx]
        p('  %-4s depends on %s' % (nmx, sorted(dep.get(w, {'UNSOLVED'}))))
    # charged-row bound (map 2.7 numbers, DERIVED)
    rows = {'opened clusters': 71.018, 'solver credit': 69.518, 'fills': 69.476, 'E lanes': 67.723,
            'representative batches': 67.239, 'passing lanes': 65.068, 'contexts': 59.344}
    tot = math.log2(sum(2 ** v for v in rows.values()))
    p('sum of rows 2^%.3f (map: 2^71.935)' % tot)
    sav = lambda share: -math.log2(1 - share)
    p('removing the contexts row entirely saves %.6f bit' % sav(2 ** (rows['contexts'] - tot)))
    mem = sum(2 ** rows[k] for k in ('opened clusters', 'fills', 'E lanes', 'representative batches', 'passing lanes'))
    p('member-level rows share %.4f; per outer step %.3f machine units (2^71.935 / 2^69.115 = %.3f)'
      % (mem / 2 ** tot, mem / 2 ** 69.115, 2 ** (71.935 - 69.115)))
    nm0 = len(table.get(('r0', 'member'), [])); nmall = sum(len(v) for (r, k), v in table.items() if k == 'member')
    share = nm0 / nmall if nmall else 0
    p('member-dependent relations: %d, of which round 0: %d (%.3f)' % (nmall, nm0, share))
    p('if per-member round-0 work were FREE (line-share GUESS): saving %.3f bit'
      % sav(share * mem / 2 ** tot))
    # ancestry of the member-level targets through member-level words only
    det = {w: (c, i) for i, (c, w, d) in enumerate(order)}
    rel_of = {}
    k = 0
    for i, (c, ids) in enumerate(rels):
        if used[i]:
            pass
    # rebuild: which relation determined each word (re-run propagation recording ids)
    dep2 = {w: frozenset() for w in fixed}; dep2.update(free)
    used2 = [False] * len(rels); detrel = {}
    changed = True
    while changed:
        changed = False
        for i, (c, ids) in enumerate(rels):
            if used2[i]:
                continue
            unk = [w for w in ids if w not in dep2]
            if len(unk) == 1:
                dep2[unk[0]] = frozenset().union(*(dep2[w] for w in ids if w in dep2))
                used2[i] = True; detrel[unk[0]] = (c, ids); changed = True
    ismem = lambda w: ('y' in dep2.get(w, ())) and ('c1' not in dep2.get(w, ()))

    def ancestry(target):
        seen, stack, lines = set(), [target], []
        while stack:
            w = stack.pop()
            if w in seen or not ismem(w) or w not in detrel:
                continue
            seen.add(w)
            c, ids = detrel[w]
            lines.append((c, w))
            stack.extend(x for x in ids if x != w)
        return lines

    anc = {}
    for tgt in ('w8', 'Y9'):
        L = ancestry(byname[tgt])
        r0n = sum(1 for c, w in L if c in calls0)
        anc[tgt] = (len(L), r0n)
        p('ancestry of %s through member-level words: %d lines, %d in round 0: %s'
          % (tgt, len(L), r0n, ' '.join('%s:%s' % (c, SP.nm(T, w)) for c, w in L)))
    om = anc['w8']
    A8 = set(w for c, w in ancestry(byname['w8']))
    L9 = [(c, w) for c, w in ancestry(byname['Y9']) if w not in A8]
    y9 = (len(L9), sum(1 for c, w in L9 if c in calls0))
    p('Y9-only lines (Y9 ancestry minus the omega lines): %d, %d in round 0: %s'
      % (y9[0], y9[1], ' '.join('%s:%s' % (c, SP.nm(T, w)) for c, w in L9)))
    # ceiling: every member-level round-0 line free, uniform cost per line inside a row (GUESS)
    f_om = om[1] / om[0]
    f_y9 = y9[1] / y9[0]
    cut = (2 ** rows['opened clusters'] * f_om * (238 / 267) + 2 ** rows['representative batches'] * f_om * (52 / 61)
           + 2 ** rows['fills'] * f_y9)
    p('ceiling if all member-level round-0 lines were free (uniform line cost, GUESS): %.3f bit '
      '(opened clusters r0 share %.3f x 238/267, rep. batches %.3f x 52/61, fills %.3f)'
      % (sav(cut / 2 ** tot), f_om, f_om, f_y9))
    json.dump({k[0] + '/' + k[1]: v for k, v in table.items()}, open(OUT + r'\r0cost_out.json', 'w'), indent=1)
    open(OUT + r'\r0cost_out.txt', 'w').write('\n'.join(log) + '\n')


if __name__ == '__main__':
    main()
