"""g1exact.py: EXACT number of Y9 in [0, 2^32) for which some h1 gives g1 ^ g1' = dg1 for at least one of the
beta* outcomes (g1 = Y9 + h1, g1' = Y9 + (h1 ^ eta)).  Dynamic programme over the bits of Y9, low to high: the
state is, for each target, the set of carry pairs (into the current bit, for g1 and g1') reachable by some choice
of the low bits of h1; Y9 prefixes with the same state are counted together.  Exact integer arithmetic.
Cross-check: the same programme with one target against g1feas.py's sampled shares."""
import sys
from collections import defaultdict
sys.dont_write_bytecode = True
import e3dfs as D

ETA = D.ETA
rows, _ = D.load_targets()
bstar = [r for r in rows if r[1] == 0x18b0e098]
TG = [D.outcome_target(r[2], r[3])[0] for r in bstar]


def step(reach, ybit, ebit, tbit):
    """reach: frozenset of carry pairs (ca, cb); returns the set after one bit for one target."""
    out = set()
    for ca, cb in reach:
        for hb in (0, 1):
            sa = ybit + hb + ca
            sb = ybit + (hb ^ ebit) + cb
            if ((sa & 1) ^ (sb & 1)) != tbit:
                continue
            out.add((sa >> 1, sb >> 1))
    return frozenset(out)


def count(targets):
    init = tuple(frozenset({(0, 0)}) for _ in targets)
    states = {init: 1}
    for k in range(32):
        eb = (ETA >> k) & 1
        new = defaultdict(int)
        for st, n in states.items():
            for yb in (0, 1):
                ns = tuple(step(r, yb, eb, (t >> k) & 1) if r else r for r, t in zip(st, targets))
                if all(not r for r in ns):
                    continue                       # dead for every target: drop (counts as infeasible)
                new[ns] += n
        states = new
    feas_any = sum(n for st, n in states.items() if any(st))
    each = [sum(n for st, n in states.items() if st[i]) for i in range(len(targets))]
    return feas_any, each


import math
fa, each = count(TG)
print(f'exact count over all 2^32 Y9: feasible for at least one of the {len(TG)} beta* outcomes: {fa} '
      f'= 2^{math.log2(fa) - 32:.4f} of all Y9 (share {fa / 2**32:.6f})')
for r, t, e in zip(bstar, TG, each):
    print(f'  tau {r[2]:08x} dg1 {t:08x}: {e} = 2^{math.log2(e) - 32:.4f}')
print(f'gain of skipping infeasible outer steps in the cube program (rate per kept outer step / average): '
      f'{2**32 / fa:.3f} = 2^{32 - math.log2(fa):.4f}')
