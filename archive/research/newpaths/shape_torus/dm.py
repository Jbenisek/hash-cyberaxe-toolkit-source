"""Ring decomposition of the idea-1 system by Dulmage-Mendelsohn blocks (shape_torus, 2026-10-08).

Fix an index set I (F words: the family index; F = freedom).  The rest is a square system (unknown words =
equations).  Its fine DM decomposition (perfect matching + strongly connected components) is unique: the
blocks are the irreducible rings of the system, solved one after another (block-triangular order).
Per family member the cost is SUM over blocks of 2^(32 t_b), t_b = tearing number (cut words) of block b,
instead of 2^(32 * total checks): early abort turns a product of rings into a sum.   [DERIVED]
t_b is estimated by greedy guess-and-determine inside the block (upper bound).
Usage: python dm.py <fixed|outhalf> <mode: orders|msg|random> <n> <seed>
"""
import itertools
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from gd_order import build  # noqa: E402


def dm_blocks(eqs, const, vars_, index):
    unk = [v for v in vars_ if v not in index]
    known = set(const) | set(index)
    vid = {v: i for i, v in enumerate(unk)}
    E = [[vid[u] for u in vs if u not in known] for _, vs in eqs]
    n = len(unk)
    if len(E) != n:
        return None
    # Hopcroft-Karp-lite: augmenting paths
    match_v = [-1] * n   # var -> eq
    match_e = [-1] * n
    adj = E
    sys.setrecursionlimit(10000)

    def aug(e, seen):
        for v in adj[e]:
            if seen[v]:
                continue
            seen[v] = True
            if match_v[v] < 0 or aug(match_v[v], seen):
                match_v[v] = e
                match_e[e] = v
                return True
        return False

    # greedy init
    for e in range(n):
        for v in adj[e]:
            if match_v[v] < 0:
                match_v[v] = e
                match_e[e] = v
                break
    for e in range(n):
        if match_e[e] < 0:
            if not aug(e, [False] * n):
                return None
    # var v (solved by eq match_v[v]) depends on the other vars of that eq
    dep = [[u for u in adj[match_v[v]] if u != v] for v in range(n)]
    # iterative Tarjan
    index_, low, onst, st, comps = [None] * n, [0] * n, [False] * n, [], []
    cnt = 0
    for root in range(n):
        if index_[root] is not None:
            continue
        work = [(root, 0)]
        while work:
            v, pi = work.pop()
            if pi == 0:
                index_[v] = low[v] = cnt
                cnt += 1
                st.append(v)
                onst[v] = True
            recurse = False
            for k in range(pi, len(dep[v])):
                u = dep[v][k]
                if index_[u] is None:
                    work.append((v, k + 1))
                    work.append((u, 0))
                    recurse = True
                    break
                elif onst[u]:
                    low[v] = min(low[v], index_[u])
            if recurse:
                continue
            if low[v] == index_[v]:
                comp = []
                while True:
                    u = st.pop()
                    onst[u] = False
                    comp.append(u)
                    if u == v:
                        break
                comps.append(comp)
            if work:
                p = work[-1][0]
                low[p] = min(low[p], low[v])
    # comps come out dependencies-first
    blocks = []
    for comp in comps:
        words = [unk[v] for v in comp]
        beqs = [match_v[v] for v in comp]
        blocks.append((words, beqs))
    return blocks


def tearing(eqs, block_words, block_eqs, known_before, rng, runs=200):
    """Greedy GD inside one block: min number of guessed words so that propagation (with the block's own
    equations, earlier words known) determines the whole block."""
    bw = set(block_words)
    beq = [eqs[k][1] for k in block_eqs]
    best = None
    for _ in range(runs):
        known = set()
        guesses = []
        while True:
            changed = True
            while changed:
                changed = False
                for vs in beq:
                    u = [x for x in vs if x in bw and x not in known]
                    if len(u) == 1:
                        known.add(u[0])
                        changed = True
            if known >= bw:
                break
            cand = {}
            for vs in beq:
                u = [x for x in vs if x in bw and x not in known]
                if len(u) == 2:
                    for x in u:
                        cand[x] = cand.get(x, 0) + 1
            if not cand:
                cand = {x: 1 for x in bw - known}
            m = max(cand.values())
            pool = sorted(x for x, c in cand.items() if c >= m - rng.choice((0, 0, 1)))
            g = rng.choice(pool)
            known.add(g)
            guesses.append(g)
            if best is not None and len(guesses) >= len(best):
                break
        if known >= bw and (best is None or len(guesses) < len(best)):
            best = guesses
    return best


def analyse(eqs, const, vars_, index, rng, truns=100):
    blocks = dm_blocks(eqs, const, vars_, index)
    if blocks is None:
        return None
    out = []
    for words, beqs in blocks:
        if len(words) == 1:
            out.append((words, beqs, []))
            continue
        t = tearing(eqs, words, beqs, None, rng, truns)
        out.append((words, beqs, t))
    return out


def main():
    variant, mode, n, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    eqs, const, vars_ = build(variant, "len64")
    F = len(vars_) - len(eqs)
    rng = random.Random(seed)
    cands = []
    if mode == "msg":
        pool = sorted(v for v in vars_ if v.startswith("m"))
        cands = list(itertools.combinations(pool, F))
        rng.shuffle(cands)
        cands = cands[:n]
    elif mode == "random":
        for _ in range(n):
            cands.append(tuple(rng.sample(sorted(vars_), F)))
    elif mode == "orders":
        from ring_gd import gd_run
        seen = set()
        for _ in range(n):
            g, solved, checks, anc = gd_run(eqs, const, vars_, rng)
            for idx in itertools.combinations(sorted(g), F):
                if idx not in seen:
                    seen.add(idx)
                    cands.append(idx)
    hist = {}
    best = []
    for idx in cands:
        blocks = dm_blocks(eqs, const, vars_, idx)
        if blocks is None:
            hist["singular"] = hist.get("singular", 0) + 1
            continue
        sizes = sorted((len(b[0]) for b in blocks if len(b[0]) > 1), reverse=True)
        key = tuple(sizes)
        hist[key] = hist.get(key, 0) + 1
        best.append((sizes, idx, blocks))
    best.sort(key=lambda t: (t[0][0] if t[0] else 0, -len(t[0])))
    lines = [f"{variant} mode={mode} candidates={len(cands)} freedom={F}",
             "non-trivial block-size profiles (count):"]
    for k, c in sorted(hist.items(), key=lambda kv: -kv[1])[:25]:
        lines.append(f"   {k}: {c}")
    lines.append("best index sets (smallest largest block), with tearing numbers:")
    for sizes, idx, blocks in best[:8]:
        res = []
        for words, beqs in blocks:
            if len(words) > 1:
                t = tearing(eqs, words, beqs, None, rng, 150)
                res.append(f"{len(words)}w/t{len(t)}{t}")
        lines.append(f"   index {list(idx)}: blocks {res}")
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(HERE, f"dm_{variant}_{mode}_s{seed}.txt"), "w") as fh:
        fh.write(txt + "\n")


if __name__ == "__main__":
    main()
