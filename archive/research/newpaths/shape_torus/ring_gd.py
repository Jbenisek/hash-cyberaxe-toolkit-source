"""Rings in the idea-1 system: cut-and-run-around orders, block-triangular structure, bit-level seed cost.

Word level (same model as ../gd_order.py): every G call = 8 primitive equations, each solvable for any one word.
A guess-and-determine order makes g guesses; F of them are the family index (F = freedom), the other g - F are
CUTS.  Each of the g - F checks is the closure of a ring through one or more cuts.  We match checks to cuts
(perfect matching, then strongly connected components = Dulmage-Mendelsohn blocks).  A block of size 1 is a
single-cut ring: cut one word, run around, close on one 32-bit equation.  A block of size b is a b-cut ring.

Bit level (bitgd.py): a block's subsystem (words that depend on its cuts and feed its checks) is solved by seeding
s bits and propagating; cost 2^s passes for ~1 root on average.  A block whose parameters (known, varying words
feeding it) number p can instead be tabulated once if 32*p + s <= 85 (memory free, preprocessing <= 2^85).

Sub-family: only 2^64 members are needed, so F - 2 index words may be frozen (they become constants for tables).
Usage: python ring_gd.py <fixed|outhalf> <runs> <seed> [maxguess] [bitTries]
"""
import itertools
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from gd_order import build  # noqa: E402
from bitgd import BitSystem  # noqa: E402


def gd_run(eqs, const, vars_, rng):
    """Greedy GD like gd_order.run, with provenance.  Returns guesses, solved{word: (eqname, inputs)},
    checks [(eqname, words)], and anc{word: bitmask of guess indices}."""
    known = {c: 0 for c in const}
    solved = {}
    guesses = []
    used = set()
    checks = []
    occ = {}
    for k, (n, vs) in enumerate(eqs):
        for v in vs:
            occ.setdefault(v, []).append(k)
    done = [False] * len(eqs)

    def prop(queue):
        while queue:
            v = queue.pop()
            for k in occ.get(v, ()):
                if done[k]:
                    continue
                n, vs = eqs[k]
                unk = [u for u in vs if u not in known]
                if len(unk) == 1:
                    u = unk[0]
                    a = 0
                    for x in vs:
                        if x != u:
                            a |= known[x]
                    known[u] = a
                    solved[u] = (n, [x for x in vs if x != u])
                    done[k] = True
                    used.add(n)
                    queue.append(u)
                elif not unk:
                    done[k] = True
                    checks.append((n, vs))

    # initial propagation from constants
    q = []
    for k, (n, vs) in enumerate(eqs):
        unk = [u for u in vs if u not in known]
        if len(unk) <= 1:
            q.extend(vs)
    prop([v for v in set(q) if v in known])
    allv = set(vars_)
    while not allv <= set(known):
        cand = {}
        for k, (n, vs) in enumerate(eqs):
            if done[k]:
                continue
            unk = [u for u in vs if u not in known]
            if len(unk) == 2:
                for v in unk:
                    cand[v] = cand.get(v, 0) + 1
        if not cand:
            cand = {v: 1 for v in allv if v not in known}
        best = max(cand.values())
        pool = [v for v, c in cand.items() if c >= best - rng.choice((0, 0, 1))]
        g = rng.choice(sorted(pool))
        known[g] = 1 << len(guesses)
        guesses.append(g)
        prop([g])
    return guesses, solved, checks, known


def anc_of_check(vs, anc):
    a = 0
    for x in vs:
        a |= anc[x]
    return a


def match_blocks(ncut_list, check_masks):
    """ncut_list: list of guess indices that are cuts; check_masks: ancestry masks of checks.
    Returns list of blocks [(cuts, checks)] in solving order, or None if no perfect matching."""
    cuts = ncut_list
    n = len(cuts)
    if len(check_masks) != n:
        return None
    adj = [[j for j, c in enumerate(cuts) if (m >> c) & 1] for m in check_masks]
    matchc = [-1] * n   # cut j -> check
    matchk = [-1] * n

    def aug(k, seen):
        for j in adj[k]:
            if j in seen:
                continue
            seen.add(j)
            if matchc[j] < 0 or aug(matchc[j], seen):
                matchc[j] = k
                matchk[k] = j
                return True
        return False

    for k in range(n):
        if not aug(k, set()):
            return None
    # directed graph on checks: k -> k' if check k needs cut matched to k'
    edges = {k: [matchc[j] for j in adj[k] if j != matchk[k]] for k in range(n)}
    # Tarjan SCC
    index, low, onst, st, sccs = {}, {}, set(), [], []
    cnt = [0]

    def strong(v):
        index[v] = low[v] = cnt[0]
        cnt[0] += 1
        st.append(v)
        onst.add(v)
        for u in edges[v]:
            if u not in index:
                strong(u)
                low[v] = min(low[v], low[u])
            elif u in onst:
                low[v] = min(low[v], index[u])
        if low[v] == index[v]:
            comp = []
            while True:
                u = st.pop()
                onst.discard(u)
                comp.append(u)
                if u == v:
                    break
            sccs.append(comp)

    for v in range(n):
        if v not in index:
            strong(v)
    # Tarjan emits SCCs in reverse topological order of "needs" edges -> dependencies first
    return [([cuts[matchk[k]] for k in comp], comp) for comp in sccs]


def block_subsystem(block_cuts, block_checks, checks, solved, anc, const, frozen_mask):
    """Words that depend on the block's cuts and feed its checks; equations deriving them + the checks."""
    cm = 0
    for c in block_cuts:
        cm |= 1 << c
    need = set()
    stack = []
    for k in block_checks:
        stack.extend(checks[k][1])
    while stack:
        v = stack.pop()
        if v in need or v in const or not (anc.get(v, 0) & cm):
            continue
        need.add(v)
        if v in solved:
            stack.extend(solved[v][1])
    eqs = [(solved[v][0], None) for v in need if v in solved]
    # side parameters: known, non-constant words in the equations, varying (not frozen-only)
    return need, eqs


MAXB = int(os.environ.get("MAXB", "2"))
NBEST = int(os.environ.get("NBEST", "12"))


def main():
    variant = sys.argv[1]
    runs = int(sys.argv[2])
    seed = int(sys.argv[3])
    maxg = int(sys.argv[4]) if len(sys.argv) > 4 else 99
    btries = int(sys.argv[5]) if len(sys.argv) > 5 else 60
    eqs, const, vars_ = build(variant, "len64")
    eqd = dict(eqs)
    F = len(vars_) - len(eqs)
    rng = random.Random(seed)
    seen = set()
    results = []
    stats = {}
    for r in range(runs):
        guesses, solved, checks, anc = gd_run(eqs, const, vars_, rng)
        g = len(guesses)
        if g > maxg:
            continue
        key = tuple(sorted(guesses))
        if key in seen:
            continue
        seen.add(key)
        cmask = [anc_of_check(vs, anc) for _, vs in checks]
        assert len(checks) == g - F, (len(checks), g, F)
        best_for_run = None
        for idx in itertools.combinations(range(g), F):
            cuts = [i for i in range(g) if i not in idx]
            # a check that depends on no cut constrains the index: invalid choice
            if any(not any((m >> c) & 1 for c in cuts) for m in cmask):
                continue
            blocks = match_blocks(cuts, cmask)
            if blocks is None:
                continue
            sizes = sorted(len(b[0]) for b in blocks)
            stats[(g, tuple(sizes))] = stats.get((g, tuple(sizes)), 0) + 1
            cand = (max(sizes), len(blocks) * -1, idx, blocks)
            if best_for_run is None or cand[:2] < best_for_run[:2]:
                best_for_run = cand
        if best_for_run is None:
            continue
        results.append((best_for_run[0], g, guesses, best_for_run[2], best_for_run[3], solved, checks, anc))
    print(f"{variant}: freedom {F}; distinct guess sets {len(seen)}")
    print("block-size profile counts (guesses, sorted block sizes): ")
    for k in sorted(stats):
        print("   ", k, stats[k])
    results.sort(key=lambda t: (t[0], t[1]))
    out = []
    # bit-level evaluation of the best few runs with only single-cut blocks
    nb = 0
    for maxb, g, guesses, idx, blocks, solved, checks, anc in results:
        if maxb > MAXB or nb >= NBEST:
            continue
        nb += 1
        line = [f"run: guesses {g} {guesses}; index {[guesses[i] for i in idx]}"]
        tot = []
        for bcuts, bchk in blocks:
            need, beqs = block_subsystem(bcuts, bchk, checks, solved, anc, const, 0)
            names = [n for n, _ in beqs] + [checks[k][0] for k in bchk]
            sub = [(n, eqd[n]) for n in names]
            bs = BitSystem(sub, need, 32)
            if len(need) <= 6:
                res = bs.solve_multiwindow(random.Random(1), tries=btries)
            else:
                res = None
            cutw = [guesses[c] for c in bcuts]
            mn = bs.minimize(cutw, random.Random(2), rounds=max(1, btries // 20))
            if res is None or len(mn) < res[0]:
                per = {}
                for v in mn:
                    nm = bs.name(v)[0]
                    per[nm] = per.get(nm, 0) + 1
                res = (len(mn), per)
            s = res[0] if res else None
            side = set()
            for n in names:
                for x in eqd[n]:
                    if x not in need and x not in const:
                        side.add(x)
            sanc = 0
            for x in side:
                sanc |= anc[x]
            nanc = bin(sanc).count("1")
            line.append(f"   block cuts {[guesses[c] for c in bcuts]} checks {[checks[k][0] for k in bchk]}: "
                        f"{len(need)} words, {len(sub)} eqs, side words {len(side)}, side ancestry guesses {nanc}, "
                        f"bit seeds s = {s}" + (f" plan {res[1]}" if res else ""))
            tot.append(s if s is not None else 999)
        line.append(f"   max s {max(tot)}  sum-cost log2 ~ {max(tot) + (len(tot) > 1)}")
        print("\n".join(line))
        out.append("\n".join(line))
    with open(os.path.join(HERE, f"ring_{variant}_s{seed}.txt"), "w") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
