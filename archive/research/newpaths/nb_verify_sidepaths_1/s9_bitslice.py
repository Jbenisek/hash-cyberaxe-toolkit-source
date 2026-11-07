"""S9 check: bitsliced stage A (256 representatives per 256-bit word) on a counted load/store machine.

Builds the bitsliced stage A of proof.md 6.5 (pkg10) as straight-line code over bit slices, checks it against
the real messages (halfsearch.reference) for real contexts, and counts operations, loads and stores with a
register allocator (Belady eviction) for a given register count. Read-only use of the pkg10 program.
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

import random
import sys

sys.dont_write_bytecode = True   # never write a __pycache__ into the pkg10 folder
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/blake3-r2/experiments'))
import halfsearch as H  # noqa: E402

MASK = 0xFFFFFFFF
W256 = (1 << 256) - 1


class Gen:
    """Straight-line bitsliced code. A slice is (name, inv) or (None, bit) for a constant."""

    def __init__(self):
        self.ins = []          # (op, dst, srcs)
        self.n = 0
        self.inputs = []       # memory-resident inputs (table slices, constant masks)

    def inp(self, name):
        self.inputs.append(name)
        return (name, 0)

    def emit(self, op, *srcs):
        d = "t%d" % self.n
        self.n += 1
        self.ins.append((op, d, list(srcs)))
        return d

    def mat(self, x):
        if x[0] is None or not x[1]:
            return x
        return (self.emit("not", x[0]), 0)

    def xor(self, x, y):
        if x[0] is None and y[0] is None:
            return (None, x[1] ^ y[1])
        if x[0] is None:
            return (y[0], y[1] ^ x[1])
        if y[0] is None:
            return (x[0], x[1] ^ y[1])
        return (self.emit("xor", x[0], y[0]), x[1] ^ y[1])

    def and_(self, x, y):
        if x[0] is None:
            return y if x[1] else (None, 0)
        if y[0] is None:
            return x if y[1] else (None, 0)
        if x[1] == y[1] == 0:
            return (self.emit("and", x[0], y[0]), 0)
        if x[1] == y[1] == 1:
            return (self.emit("or", x[0], y[0]), 1)
        return self.and_(self.mat(x), self.mat(y))

    def or_(self, x, y):
        if x[0] is None:
            return (None, 1) if x[1] else y
        if y[0] is None:
            return (None, 1) if y[1] else x
        if x[1] == y[1] == 0:
            return (self.emit("or", x[0], y[0]), 0)
        if x[1] == y[1] == 1:
            return (self.emit("and", x[0], y[0]), 1)
        return self.or_(self.mat(x), self.mat(y))

    def bit_add(self, a, b, c, need_carry):
        consts = [s for s in (a, b, c) if s[0] is None]
        var = [s for s in (a, b, c) if s[0] is not None]
        if len(consts) == 3:
            tot = a[1] + b[1] + c[1]
            return (None, tot & 1), (None, tot >> 1)
        if len(consts) == 2:
            k1, k2 = consts[0][1], consts[1][1]
            s = self.xor(var[0], (None, k1 ^ k2))
            return s, ((None, k1) if k1 == k2 else var[0]) if need_carry else None
        if len(consts) == 1:
            k = consts[0][1]
            p, q = var
            s = self.xor(self.xor(p, q), (None, k))
            if not need_carry:
                return s, None
            return s, (self.or_(p, q) if k else self.and_(p, q))
        # full adder: unify polarity, then maj on raw names (maj is self-dual)
        pol = {s[1] for s in var}
        if len(pol) == 1:
            maj_pol, fixed = pol.pop(), var          # maj(~a,~b,~c) = ~maj(a,b,c): work on raw names
        else:
            maj_pol, fixed = 0, [self.mat(s) for s in var]
        x, y, z = fixed
        t = self.emit("xor", x[0], y[0])
        s = (self.emit("xor", t, z[0]), (x[1] ^ y[1] ^ z[1]))
        if not need_carry:
            return s, None
        u = self.emit("and", x[0], y[0])
        v = self.emit("and", z[0], t)
        w = self.emit("or", u, v)
        return s, (w, maj_pol)

    def add(self, a, b):
        out, c = [], (None, 0)
        for i in range(32):
            s, c = self.bit_add(a[i], b[i], c, i < 31)
            out.append(s)
        return out

    def xorw(self, a, b):
        return [self.xor(a[i], b[i]) for i in range(32)]


def ror_s(x, r):
    return [x[(i + r) % 32] for i in range(32)]


def const_slices(g, name, value, mode):
    """mode 'spec': bits known at code time (polarity, free); mode 'mask': 32 broadcast masks in memory."""
    if mode == "spec":
        return [(None, (value >> i) & 1) for i in range(32)]
    return [g.inp("%s_%d" % (name, i)) for i in range(32)]


def build(modes, ebits):
    """modes: dict constant-name -> 'spec' or 'mask'. ebits = (e27, e28, e29) of the batch (program variant)."""
    g = Gen()
    XA = [g.inp("XA_%d" % i) for i in range(32)]
    X6 = [g.inp("X6_%d" % i) for i in range(32)]
    K = {}
    for nm in ("-w2", "S10+X15", "X2+w7", "X14", "w0"):
        K[nm] = ("K", nm)
    return g, XA, X6


def program(modes, consts, ebits):
    g = Gen()
    XA = [g.inp("XA_%d" % i) for i in range(32)]
    X6 = [g.inp("X6_%d" % i) for i in range(32)]
    k = {nm: const_slices(g, nm, consts[nm], modes[nm]) for nm in ("-w2", "S10+X15", "X2+w7", "X14", "w0")}
    rx15 = [(None, (H.rol(H.X15, 8) >> i) & 1) for i in range(32)]   # program constant, always known
    X0 = g.add(XA, k["-w2"])
    D = g.xorw(X0, rx15)
    X10 = g.add(D, k["S10+X15"])
    A1 = g.add(X6, k["X2+w7"])
    Dd = ror_s(g.xorw(A1, k["X14"]), 16)
    C1 = g.add(X10, Dd)
    B1 = ror_s(g.xorw(X6, C1), 12)
    A2 = g.add(g.add(A1, B1), k["w0"])
    Z = g.xorw(A2, Dd)
    e27, e28, e29 = ebits
    gate = g.and_(g.and_(g.and_((Z[24][0], Z[24][1] ^ 1), Z[25]), Z[8]), Z[9])
    t1 = g.xor(Z[26], Z[2])
    t2 = g.xor(Z[27], Z[3])
    t3 = g.xor(g.xor(Z[27], Z[4]), Z[16])
    t4 = g.xor(g.xor(Z[30], Z[5]), Z[17])
    lits = [(t1[0], t1[1] ^ 1), (t2[0], t2[1] ^ (1 - e27)), (t3[0], t3[1] ^ (1 - e28)), (t4[0], t4[1] ^ e29)]
    ra = gate
    for L in lits:
        ra = g.and_(ra, L)
    gate = g.mat(gate)
    ra = g.mat(ra)
    return g, gate, ra


def dce(g, outs):
    live = set(outs)
    keep = []
    for op, d, srcs in reversed(g.ins):
        if d in live:
            keep.append((op, d, srcs))
            live.update(srcs)
    keep.reverse()
    return keep


def dfs_order(ins, outs):
    """Postorder from the outputs: each value is computed just before its first consumer needs it."""
    by = {d: (op, d, s) for op, d, s in ins}
    done, order = set(), []

    def visit(x):
        stack = [(x, False)]
        while stack:
            y, expanded = stack.pop()
            if y in done or y not in by:
                continue
            if expanded:
                done.add(y)
                order.append(by[y])
            else:
                stack.append((y, True))
                for s in reversed(by[y][2]):
                    if s not in done:
                        stack.append((s, False))
    for o in outs:
        visit(o)
    return order


def greedy_order(ins, outs):
    """List scheduling: among ready instructions pick the one that frees most live values, then the most recent."""
    by = {d: (op, d, s) for op, d, s in ins}
    users = {}
    for op, d, s in ins:
        for x in s:
            users.setdefault(x, set()).add(d)
    remaining_uses = {x: len(u) for x, u in users.items()}
    indeg = {d: sum(1 for x in s if x in by) for op, d, s in ins}
    ready = [d for d in by if indeg[d] == 0]
    pos = {d: i for i, (op, d, s) in enumerate(ins)}
    order, birth = [], {}
    while ready:
        def score(d):
            s = by[d][2]
            frees = sum(1 for x in set(s) if remaining_uses.get(x, 0) == 1)
            recent = max([birth.get(x, -1) for x in s] + [-1])
            return (frees, recent, -pos[d])
        best = max(ready, key=score)
        ready.remove(best)
        birth[best] = len(order)
        order.append(by[best])
        for x in set(by[best][2]):
            remaining_uses[x] -= 1
        for u in users.get(best, ()):
            indeg[u] -= 1
            if indeg[u] == 0:
                ready.append(u)
    return order


def evaluate(ins, env):
    env = dict(env)
    for op, d, s in ins:
        if op == "not":
            env[d] = ~env[s[0]] & W256
        elif op == "xor":
            env[d] = env[s[0]] ^ env[s[1]]
        elif op == "and":
            env[d] = env[s[0]] & env[s[1]]
        elif op == "or":
            env[d] = env[s[0]] | env[s[1]]
    return env


def val(env, sl):
    if sl[0] is None:
        return W256 if sl[1] else 0
    v = env[sl[0]]
    return (~v & W256) if sl[1] else v


def belady(ins, regs, outs_store):
    """Count loads and stores for straight-line code on a machine with `regs` registers.

    Inputs live in memory. A value evicted while still needed is stored once (if not already in memory) and
    loaded again. The destination may reuse the register of a source whose last use is this instruction.
    outs_store: output names that must end in memory (one store each unless already there)."""
    uses = {}
    for idx, (op, d, s) in enumerate(ins):
        for x in s:
            uses.setdefault(x, []).append(idx)
    for x in outs_store:
        uses.setdefault(x, []).append(len(ins))
    ptr = {x: 0 for x in uses}

    def next_use(x, idx):
        lst = uses.get(x, [])
        p = ptr.get(x, 0)
        while p < len(lst) and lst[p] < idx:
            p += 1
        ptr[x] = p
        return lst[p] if p < len(lst) else None

    in_mem = set(x for x in uses if not x.startswith("t"))
    reg = set()
    loads = stores = 0

    def evict(idx, protect):
        nonlocal stores
        cand = [x for x in reg if x not in protect]
        far, victim = -1, None
        for x in cand:
            nu = next_use(x, idx)
            key = float("inf") if nu is None else nu
            if key > far:
                far, victim = key, x
        nu = next_use(victim, idx)
        if nu is not None and victim not in in_mem:
            stores += 1
            in_mem.add(victim)
        reg.discard(victim)

    for idx, (op, d, s) in enumerate(ins):
        protect = set(s)
        for x in s:
            if x not in reg:
                if len(reg) >= regs:
                    evict(idx, protect)
                loads += 1
                reg.add(x)
        # free sources whose last use is this instruction (dst may take their register)
        for x in s:
            if next_use(x, idx + 1) is None:
                reg.discard(x)
        if len(reg) >= regs:
            evict(idx + 1, set())
        reg.add(d)
        # drop dead values
        for x in list(reg):
            if next_use(x, idx + 1) is None:
                reg.discard(x)
    for x in outs_store:
        if x not in in_mem:
            stores += 1
    return loads, stores


def bitslice(vals):
    return [sum(((v >> i) & 1) << lane for lane, v in enumerate(vals)) for i in range(32)]


def check(n_ctx, seed, modes):
    rnd = random.Random(seed)
    lanes_right = lanes_total = 0
    gates = passes = 0
    for case in range(n_ctx):
        free = [rnd.getrandbits(32) for _ in range(7)]
        free[6] &= ~H.X2_FLIPS & MASK            # a representative value of X2
        v = H.context(free)
        b = rnd.randrange(64)                    # batch of 256 representatives of this X2
        ks = [H.representative(256 * b + t) for t in range(256)]
        ys = [H.class_member(k) for k in ks]
        e = [((H.Y3 + y) & MASK) for y in ys]
        eb = {((x >> 27) & 1, (x >> 28) & 1, (x >> 29) & 1) for x in e}
        assert len(eb) == 1, "e27..e29 not constant in a batch"
        ebits = eb.pop()
        consts = {"-w2": (-v["w2"]) & MASK, "S10+X15": (v["S10"] + H.X15) & MASK,
                  "X2+w7": (v["X2"] + v["w7"]) & MASK, "X14": v["X14"], "w0": v["w0"]}
        g, gate, ra = program(modes, consts, ebits)
        ins = dce(g, [gate[0], ra[0]])
        rows = [H.table_row(v, y) for y in ys]
        env = {}
        for i, s in enumerate(bitslice([r["XA"] for r in rows])):
            env["XA_%d" % i] = s
        for i, s in enumerate(bitslice([r["X6"] for r in rows])):
            env["X6_%d" % i] = s
        for nm, c in consts.items():
            for i in range(32):
                env["%s_%d" % (nm, i)] = W256 if (c >> i) & 1 else 0
        out = evaluate(ins, env)
        gm, rm = val(out, gate), val(out, ra)
        for lane in range(256):
            ref = H.reference(v, ys[lane])
            want_g, want_r = int(H.gate(ref["h1"])), int(H.rule_a(ref["h1"]))
            lanes_total += 1
            lanes_right += int(((gm >> lane) & 1) == want_g and ((rm >> lane) & 1) == want_r)
            gates += want_g
            passes += want_r
    return lanes_right, lanes_total, gates, passes


def counts(modes, regs_list, ebits=(0, 0, 0), consts=None, seed=5):
    rnd = random.Random(seed)
    if consts is None:
        consts = {nm: rnd.getrandbits(32) for nm in ("-w2", "S10+X15", "X2+w7", "X14", "w0")}
    g, gate, ra = program(modes, consts, ebits)
    ins = dce(g, [gate[0], ra[0]])
    ops = len(ins)
    res = {"ops": ops}
    orders = {"gen": ins, "dfs": dfs_order(ins, [gate[0], ra[0]]), "greedy": greedy_order(ins, [gate[0], ra[0]])}
    for R in regs_list:
        best = None
        for oname, o in orders.items():
            assert len(o) == ops
            ld, st = belady(o, R, [gate[0]])
            if best is None or ld + st < best[0] + best[1]:
                best = (ld, st, oname)
        res[R] = best
    return res


if __name__ == "__main__":
    MODES = {
        "spec_all": {nm: "spec" for nm in ("-w2", "S10+X15", "X2+w7", "X14", "w0")},
        "mask_all": {nm: "mask" for nm in ("-w2", "S10+X15", "X2+w7", "X14", "w0")},
        "spec_run_outer": {"-w2": "mask", "S10+X15": "spec", "X2+w7": "mask", "X14": "spec", "w0": "mask"},
    }
    what = sys.argv[1] if len(sys.argv) > 1 else "count"
    if what == "check":
        for name, m in MODES.items():
            print(name, check(int(sys.argv[2]) if len(sys.argv) > 2 else 2, 11, m), flush=True)
    else:
        regs = [14, 30, 62, 10 ** 6]
        for name, m in MODES.items():
            for s in range(int(sys.argv[2]) if len(sys.argv) > 2 else 5):
                r = counts(m, regs, seed=s)
                print(name, "seed", s, "ops", r["ops"],
                      " ".join("R%s:L%d/S%d(%s)" % (R if R < 10 ** 6 else "inf", r[R][0], r[R][1], r[R][2])
                               for R in regs),
                      flush=True)
