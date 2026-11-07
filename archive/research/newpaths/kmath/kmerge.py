"""k-list merge (Wagner k-tree, many solutions) on random lists, mixed xor / modular-add coordinates.

Toy group G = product of c coordinates of w bits, each 'add' (Z/2^w) or 'xor' ((Z/2)^w).  n = c*w.
Leaves = random lists (random function of the side's guess value).  A join node matches, per coordinate,
a number of LOW bits (low bits of a modular sum depend only on low bits of the summands, so this is exact for
'add'; for 'xor' any bits would do).  Goal: tuples with sum = 0 in G.

Cost counted in element-steps: build (leaf elements computed), ins (table inserts), look (streamed lookups),
out (elements produced at every join node, root outputs = solutions).  Predicted = the same recursion on
expected sizes (prod of leaf sizes / 2^matched bits), plus the closed forms written in RESULTS.txt.
Usage: python kmerge.py  (runs all configurations, writes kmerge_results.txt)
"""
import sys
import time

import numpy as np

RNG = np.random.default_rng(20261008)


class Group:
    def __init__(self, w, types):
        self.w, self.types, self.c = w, list(types), len(types)
        self.mask = np.uint32((1 << w) - 1)

    def op(self, a, b):
        r = np.empty_like(a)
        for j, t in enumerate(self.types):
            r[:, j] = ((a[:, j] + b[:, j]) & self.mask) if t == "add" else (a[:, j] ^ b[:, j])
        return r

    def sub(self, tau, a):            # tau (-) a, coordinatewise
        r = np.empty_like(a)
        for j, t in enumerate(self.types):
            tj = np.uint32(int(tau[j]))
            r[:, j] = ((tj - a[:, j]) & self.mask) if t == "add" else (tj ^ a[:, j])
        return r

    def subv(self, tau, t):           # vectors
        return [((tau[j] - t[j]) & int(self.mask)) if self.types[j] == "add" else (tau[j] ^ t[j])
                for j in range(self.c)]

    def pack(self, vals, bits):
        key = np.zeros(len(vals), np.uint64)
        sh = 0
        for j, b in enumerate(bits):
            if b:
                key |= (vals[:, j].astype(np.uint64) & np.uint64((1 << b) - 1)) << np.uint64(sh)
                sh += b
        return key

    def targets(self, bits):          # all target vectors on the given low-bit counts
        tot = sum(bits)
        for x in range(1 << tot):
            v, sh = [], 0
            for b in bits:
                v.append((x >> sh) & ((1 << b) - 1))
                sh += b
            yield v


class Leaf:
    def __init__(self, G, lid, lbits):
        self.lid, self.size = lid, 1 << lbits
        self.vals = RNG.integers(0, 1 << G.w, size=(self.size, G.c), dtype=np.uint32)
        self.B = [0] * G.c
        self.leaves = [self]


class Join:
    def __init__(self, s, t, A, G):    # s streamed child, t stored child, A new low bits per coordinate
        assert s.B == t.B
        self.s, self.t, self.A = s, t, list(A)
        self.B = [b + a for b, a in zip(s.B, A)]
        assert all(b <= G.w for b in self.B)
        self.leaves = s.leaves + t.leaves


class Ctr:
    def __init__(self):
        self.ins = self.look = self.out = 0
        self.tables = {}


def table(G, Y, bits):
    k = G.pack(Y[0], bits)
    order = np.argsort(k, kind="stable")
    return k[order], order


def join_one(G, X, Ytab, Y, bits, tau, ctr):
    ks, order = Ytab
    need = G.pack(G.sub(tau, X[0]), bits)
    lo = np.searchsorted(ks, need, "left")
    hi = np.searchsorted(ks, need, "right")
    cnt = hi - lo
    tot = int(cnt.sum())
    ctr.look += len(X[0])
    ctr.out += tot
    if tot == 0:
        return (np.zeros((0, G.c), np.uint32), np.zeros((0, X[1].shape[1] + Y[1].shape[1]), np.int64))
    ix = np.repeat(np.arange(len(cnt)), cnt)
    start = np.repeat(lo - (np.cumsum(cnt) - cnt), cnt)
    iy = order[start + np.arange(tot)]
    return G.op(X[0][ix], Y[0][iy]), np.hstack([X[1][ix], Y[1][iy]])


def produce(G, node, tau, ctr, limit=None, sink=None):
    if isinstance(node, Leaf):
        return node.vals, np.arange(node.size, dtype=np.int64)[:, None]
    outs, got = [], 0
    for tc in G.targets(node.s.B):
        X = produce(G, node.s, tc, ctr)
        Y = produce(G, node.t, G.subv(tau, tc), ctr)
        if isinstance(node.t, Leaf):
            key = (node.t.lid, tuple(node.B))
            if key not in ctr.tables:
                ctr.tables[key] = table(G, Y, node.B)
                ctr.ins += len(Y[0])
            tab = ctr.tables[key]
        else:
            tab = table(G, Y, node.B)
            ctr.ins += len(Y[0])
        r = join_one(G, X, tab, Y, node.B, tau, ctr)
        got += len(r[0])
        if sink is not None:
            sink(r)
        else:
            outs.append(r)
        if limit is not None and got >= limit:
            break
    if sink is not None:
        return got
    if not outs:
        return (np.zeros((0, G.c), np.uint32), np.zeros((0, len(node.leaves)), np.int64))
    return np.concatenate([o[0] for o in outs]), np.concatenate([o[1] for o in outs])


def expected(G, node, ntarg_root=None):
    """expected (size per call, cost per call) of produce(node, .) on random lists; tables of leaves counted once
    by the caller.  ntarg = number of child targets looped (all, or ntarg_root at the root)."""
    if isinstance(node, Leaf):
        return float(node.size), 0.0
    prod = 1.0
    for lf in node.leaves:
        prod *= lf.size
    size_per_target = prod / 2.0 ** sum(node.B) / 2.0 ** sum(node.s.B)   # per child target
    nt = 2 ** sum(node.s.B) if ntarg_root is None else ntarg_root
    sx, cx = expected(G, node.s)
    sy, cy = expected(G, node.t)
    per = cx + cy + sx + size_per_target + (0 if isinstance(node.t, Leaf) else sy)
    return size_per_target * nt, per * nt


def leaf_table_cost(node):
    if isinstance(node, Leaf):
        return 0.0
    c = leaf_table_cost(node.s) + leaf_table_cost(node.t)
    if isinstance(node.t, Leaf):
        c += node.t.size
    return c


def run(name, G, root, M, log, check=True):
    ctr = Ctr()
    stat = {"bad": 0, "dup": 0, "n": 0}

    def sink(r):
        vals, idx = r
        stat["n"] += len(idx)
        stat["targets"] = stat.get("targets", 0) + 1
        if check and len(idx):
            s = np.zeros((len(idx), G.c), np.uint32)
            for i, lf in enumerate(root.leaves):
                s = G.op(s, lf.vals[idx[:, i]])
            stat["bad"] += int((s != 0).any(axis=1).sum())
            if len(idx) < 4_000_000:
                stat["dup"] += len(idx) - len(np.unique(idx, axis=0))
    t0 = time.time()
    nsol = produce(G, root, [0] * G.c, ctr, limit=M, sink=sink)
    dt = time.time() - t0
    build = sum(lf.size for lf in root.leaves)
    total = build + ctr.ins + ctr.look + ctr.out
    ok = f"bad={stat['bad']} dup={stat['dup']}" if check else "unchecked"
    prod = 1.0
    for lf in root.leaves:
        prod *= lf.size
    per_t = prod / 2.0 ** sum(root.B) / 2.0 ** sum(root.s.B)      # expected solutions per root target
    ntr = stat.get("targets", 1)                                    # root targets actually used
    esol, ecost = expected(G, root, ntarg_root=ntr)
    epred = build + leaf_table_cost(root) + ecost
    line = (f"{name:44s} n={G.c * G.w:3d} M=2^{np.log2(M):5.2f} sols={nsol:9d} (exp {esol:11.0f}) "
            f"steps={total:11d} (exp {epred:11.0f}, ratio {total / epred:5.3f}) steps/sol={total / max(nsol, 1):7.2f} "
            f"[T={ntr} build {build} ins {ctr.ins} look {ctr.look} out {ctr.out}] {ok} {dt:6.1f}s")
    print(line, flush=True)
    log.write(line + chr(10))
    log.flush()
    return nsol, total


def configs(w, which):
    """scaled attack: word = w bits, members needed M = 2^(2w) (the analogue of 2^64 with 32-bit words)."""
    M = 1 << (2 * w)
    out = []
    W = w
    if "c4k2" in which:
        G = Group(w, ["add", "xor", "add", "xor"])
        # 2 lists: L1 stored 2^(3w) (n+m)/2 = 3w; L2 streamed: expected 2^(m+n-l1) = 2^(3w)
        L1, L2 = Leaf(G, 0, 3 * W), Leaf(G, 1, 3 * W)
        out.append(("c4 k2 sides 3w,3w", G, Join(L2, L1, [W] * 4, G), M))
    if "c4k4" in which:
        G = Group(w, ["add", "xor", "add", "xor"])
        L = [Leaf(G, i, 2 * W) for i in range(4)]
        A1 = [W, W, 0, 0]
        p12, p34 = Join(L[0], L[1], A1, G), Join(L[2], L[3], A1, G)
        out.append(("c4 k4 sides 2w x4, level1 = coords 0,1", G, Join(p12, p34, [0, 0, W, W], G), M))
        # partial low bits on additive coordinates at level 1 (2w bits spread over 3 coordinates)
        G2 = Group(w, ["add", "add", "xor", "add"])
        L = [Leaf(G2, i, 2 * W) for i in range(4)]
        h = W // 2
        A1 = [W, h, W - h, 0]
        p12, p34 = Join(L[0], L[1], A1, G2), Join(L[2], L[3], A1, G2)
        out.append(("c4 k4 sides 2w x4, level1 partial add bits", G2,
                    Join(p12, p34, [W - a for a in A1], G2), M))
    if "c4k8" in which:
        G = Group(w, ["add", "xor", "add", "add"])
        L = [Leaf(G, i, W) for i in range(8)]
        A1, A2 = [W, 0, 0, 0], [0, W, 0, 0]
        pr = [Join(L[2 * i], L[2 * i + 1], A1, G) for i in range(4)]
        qa, qb = Join(pr[0], pr[1], A2, G), Join(pr[2], pr[3], A2, G)
        out.append(("c4 k8 sides 1w x8", G, Join(qa, qb, [0, 0, W, W], G), M))
    if "c3k4" in which:
        G = Group(w, ["add", "xor", "add"])
        L = [Leaf(G, 0, W), Leaf(G, 1, 2 * W), Leaf(G, 2, W), Leaf(G, 3, 2 * W)]
        A1 = [W, 0, 0]
        p12, p34 = Join(L[0], L[1], A1, G), Join(L[2], L[3], A1, G)
        out.append(("c3 k4 sides (1w,2w),(1w,2w)", G, Join(p12, p34, [0, W, W], G), M))
    if "c3k6" in which:
        G = Group(w, ["add", "xor", "add"])
        L = [Leaf(G, i, W) for i in range(6)]
        z = [0, 0, 0]
        hA = Join(Join(L[0], L[1], z, G), L[2], [W, 0, 0], G)
        hB = Join(Join(L[3], L[4], z, G), L[5], [W, 0, 0], G)
        out.append(("c3 k6 sides 1w x6 (3+3, product halves)", G, Join(hA, hB, [0, W, W], G), M))
    if "c3k2" in which:
        G = Group(w, ["add", "xor", "add"])
        l = (3 * W + 2 * W) // 2
        L1, L2 = Leaf(G, 0, l), Leaf(G, 1, 5 * W - l)
        out.append((f"c3 k2 sides {l},{5 * W - l} bits", G, Join(L2, L1, [W] * 3, G), M))
    if "c2k4" in which:
        G = Group(w, ["add", "xor"])
        L = [Leaf(G, i, W) for i in range(4)]
        A1 = [W, 0]
        p12, p34 = Join(L[0], L[1], A1, G), Join(L[2], L[3], A1, G)
        out.append(("c2 k4 sides 1w x4 (all targets)", G, Join(p12, p34, [0, W], G), M))
    if "c2k2" in which:
        G = Group(w, ["add", "xor"])
        L1, L2 = Leaf(G, 0, 2 * W), Leaf(G, 1, 2 * W)
        out.append(("c2 k2 sides 2w,2w", G, Join(L2, L1, [W, W], G), M))
    return out


def claim2(n_half, ms, log):
    """4 lists of 2^(n/2), n = 2*n_half bits as two add + two xor coords; M = 2^m for m up to n."""
    w = n_half // 2
    G = Group(w, ["add", "xor", "add", "xor"])
    L = [Leaf(G, i, n_half) for i in range(4)]
    A1 = [w, w, 0, 0]
    for m in ms:
        p12, p34 = Join(L[0], L[1], A1, G), Join(L[2], L[3], A1, G)
        run(f"claim2 4x2^(n/2) m={m}", G, Join(p12, p34, [0, 0, w, w], G), 1 << m, log, check=(m <= 20))


def small_lists(log):
    """4 lists of 2^l with l < n/2: predicted total ~ 4*2^l + 2*2^(m+n-2l) + 2^m."""
    G = Group(6, ["add", "xor", "add", "xor"])       # n = 24
    for l, a in ((10, 8), (11, 10), (9, 6)):
        L = [Leaf(G, i, l) for i in range(4)]
        A1 = [6, a - 6, 0, 0]
        p12, p34 = Join(L[0], L[1], A1, G), Join(L[2], L[3], A1, G)
        m = 4 * l - 24
        run(f"smalllists l={l} a={a} all targets", G, Join(p12, p34, [0, 6 - (a - 6), 6, 6], G), 1 << m, log)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    with open("kmerge_results.txt", "a") as log:
        log.write(f"=== run {time.ctime()} which={which}\n")
        if which in ("all", "attack"):
            for w in (6, 7, 8, 9):
                sel = ["c4k4", "c4k8", "c3k4", "c3k6", "c2k4", "c2k2"]
                if w <= 7:
                    sel += ["c4k2", "c3k2"]
                for cfg in configs(w, sel):
                    run(*cfg, log)
        if which in ("all", "claim2"):
            claim2(12, [6, 12, 18, 24], log)
            claim2(16, [8, 16, 20, 24], log)
        if which in ("all", "small"):
            small_lists(log)
