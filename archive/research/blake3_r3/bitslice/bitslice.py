"""256-lane bit-sliced 3-round BLAKE3 chain step (blake3-r3-prefix-v1), run-time generator in the style of rho.py's Tracer.

A plane is a 256-bit integer: bit l of plane j is bit j of the chain value of lane l.  A 32-bit word is 32 planes, so
rotations are renaming (no operation), XOR/AND/OR are one operation each, an add is a ripple of full adders.
The chain input is the 256 digest planes of the previous step (low n planes; planes >= n are the constant 0), so the chain
feed is renaming too.  Signals carry a polarity bit (stored plane = true plane xor all-ones if neg); the input polarity
vector is iterated to a fixed point so that the step needs no NOT operations: the stored output plane j has the same
polarity as the stored input plane j.

Sections: 1 gate generator and straight-line emitter, 2 analysis (op count, peak live, spill_ops(R)), 3 lane packing,
4 validation against the scalar chain (rho.py).  Run: python bitslice.py [--validate] [--analyse]
"""
import os
import sys
import random

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "b3r3s", "pkg", "blake3", "experiments"))
import rho                                   # the filed scalar chain and packed 595-op circuit (read only)

M32 = 0xFFFFFFFF
LANES = 256
ALL = (1 << LANES) - 1
IV, PERM, GCALLS = rho.IV, rho.PERM, rho.GCALLS
ZERO, ONE = (0, 0), (0, 1)                   # node 0 is the constant 0; (0, 1) is constant 1


# ---------------------------------------------------------------- 1 generator
class Gen:
    """Hash-consed gate network over signals (node, neg).  Node kinds: ('v', j) input plane j, (op, a, b) with op in x, a, o."""

    def __init__(self, n, pin):
        self.n, self.nodes, self.memo = n, [("c",)], {}
        self.inputs = []
        for j in range(n):
            self.nodes.append(("v", j))
            self.inputs.append((len(self.nodes) - 1, pin[j]))

    def mk(self, op, a, b):
        if a > b:
            a, b = b, a
        k = (op, a, b)
        if k not in self.memo:
            self.nodes.append(k)
            self.memo[k] = len(self.nodes) - 1
        return self.memo[k]

    def XOR(self, x, y):
        if x[0] == 0:
            return (y[0], y[1] ^ x[1])
        if y[0] == 0:
            return (x[0], x[1] ^ y[1])
        if x[0] == y[0]:
            return (0, x[1] ^ y[1])
        return (self.mk("x", x[0], y[0]), x[1] ^ y[1])

    def AND(self, x, y):
        if x[0] == 0:
            return ZERO if x[1] == 0 else y
        if y[0] == 0:
            return ZERO if y[1] == 0 else x
        if x[0] == y[0]:
            return x if x[1] == y[1] else ZERO
        if x[1] == 0 and y[1] == 0:
            return (self.mk("a", x[0], y[0]), 0)
        if x[1] == 1 and y[1] == 1:
            return (self.mk("o", x[0], y[0]), 1)           # !a & !b = !(a | b)
        p, q = (x, y) if x[1] == 0 else (y, x)               # p positive, q negative: p & !qn = p ^ (p & qn)
        return self.XOR(p, (self.mk("a", p[0], q[0]), 0))

    def add(self, A, B):
        """Ripple add of two 32-plane words (carry out of bit 31 dropped)."""
        s, c = [], ZERO
        for i in range(32):
            a, b = A[i], B[i]
            if c == ZERO:
                s.append(self.XOR(a, b))
                c = self.AND(a, b)
            else:
                x, y = self.XOR(a, c), self.XOR(b, c)
                s.append(self.XOR(x, b))
                if i < 31:
                    c = self.XOR(self.AND(x, y), c)
        return s

    def xorw(self, A, B):
        return [self.XOR(a, b) for a, b in zip(A, B)]


def ror(A, r):
    return [A[(i + r) % 32] for i in range(32)]


def constw(v):
    return [ONE if (v >> i) & 1 else ZERO for i in range(32)]


def trace(n, pin, rounds=3):
    """Build the network for the digest of 0^32 || x (x = low n bits of the input planes, the rest 0)."""
    g = Gen(n, pin)
    zero = constw(0)
    m = [zero] * 8 + [[g.inputs[32 * i + b] if 32 * i + b < n else ZERO for b in range(32)] for i in range(8)]
    v = [constw(w) for w in IV] + [constw(w) for w in IV[:4]] + [zero, zero, constw(64), constw(11)]
    for _ in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            v[a] = g.add(g.add(v[a], v[b]), x)
            v[d] = ror(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = ror(g.xorw(v[b], v[c]), 12)
            v[a] = g.add(g.add(v[a], v[b]), y)
            v[d] = ror(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = ror(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    out = [s for i in range(8) for s in g.xorw(v[i], v[i + 8])]      # output plane 32*i + b
    return g, out


PIN256 = 0x200802a10020080000040000000408400000006002000000020240008000   # input polarity bits found by find_pin(256)


def trace_stats(g, out, n):
    """Operation nodes reachable from the low n output planes, in creation (program) order."""
    seen = set(out[j][0] for j in range(n))
    for k in range(len(g.nodes) - 1, 0, -1):
        if k in seen and g.nodes[k][0] in "xao":
            seen.add(g.nodes[k][1])
            seen.add(g.nodes[k][2])
    return [k for k in range(1, len(g.nodes)) if k in seen and g.nodes[k][0] in "xao"]


def find_pin(n, iters=1500, seed=2, rounds=3):
    """Hill climb on the input polarity vector minimising gates + NOT fixes (output planes whose polarity differs from the
    input plane they feed).  Zero fixes is not reachable (the polarity map does not settle); about 125 remain at n = 256."""
    rnd, pin = random.Random(seed), [0] * n

    def cost(p):
        g, out = trace(n, p, rounds)
        po = [out[j][1] for j in range(n)]
        return len(trace_stats(g, out, n)) + sum(1 for j in range(n) if po[j] != p[j]), po
    cur, po = cost(pin)
    for _ in range(iters):
        mis = [j for j in range(n) if po[j] != pin[j]]
        new = list(pin)
        for j in rnd.sample(mis, min(rnd.choice([1, 1, 2, 3]), len(mis))):
            new[j] ^= 1
        if rnd.random() < 0.2:
            new[rnd.randrange(n)] ^= 1
        c2, p2 = cost(new)
        if c2 <= cur:
            pin, po, cur = new, p2, c2
    return pin


class Step:
    """The straight-line chain step for width n: source, op count by kind, compiled function.  step(*planes) takes the n stored
    input planes (polarity self.pin) and returns the n stored planes of the next input, same polarity (NOT fixes included)."""

    def __init__(self, n=256, rounds=3, pin=None):
        if pin is None:
            pin = [(PIN256 >> j) & 1 for j in range(256)][:n] if n == 256 else find_pin(n, rounds=rounds)
        g, out = trace(n, pin, rounds)
        self.n, self.g, self.out, self.pin = n, g, out, list(pin)
        self.order = trace_stats(g, out, n)
        self.fix = [j for j in range(n) if out[j][1] != pin[j]]          # planes needing xor with all-ones
        self.by = {}
        names, lines, self._lines = {0: "0"}, [], []
        for j, (nid, _) in enumerate(g.inputs):
            names[nid] = "i%d" % j
        sym = {"x": "^", "a": "&", "o": "|"}
        for k in self.order:
            op, a, b = g.nodes[k]
            names[k] = "t%d" % k
            lines.append("%s=%s%s%s" % (names[k], names[a], sym[op], names[b]))
            self._lines.append((names[k], names[a], names[b]))
            self.by[op] = self.by.get(op, 0) + 1
        self.gates = len(self.order)
        outs = []
        for j in range(n):
            nm = names[out[j][0]]
            if j in self.fix:
                lines.append("u%d=%s^%d" % (j, nm, ALL))
                self._lines.append(("u%d" % j, nm, "#"))
                nm = "u%d" % j
            outs.append(nm)
        self.by["not"] = len(self.fix)
        self.ops = self.gates + len(self.fix)
        self.outs = outs
        nl = chr(10)
        self.src = ("def step(%s):" % ",".join("i%d" % j for j in range(n)) + nl
                    + "".join("    %s" % ln + nl for ln in lines) + "    return (%s,)" % ",".join(outs) + nl)
        ns = {}
        exec(compile(self.src, "<bitslice-step-n%d>" % n, "exec"), {}, ns)
        self.step = ns["step"]
        self.pout = self.pin

    # ------------------------------------------------------------ 2 analysis
    def _lastuse(self):
        last = {}
        for k, (_, a, b) in enumerate(self._lines):
            for v in (a, b):
                last[v] = k
        for v in self.outs:
            last[v] = 10 ** 9
        return last

    def peak_live(self):
        """Largest number of live plane registers after one operation (inputs are live at the start, a result may reuse a
        dying operand's register, outputs stay live to the end)."""
        last = self._lastuse()
        live = {"i%d" % j for j in range(self.n)}
        peak = len(live)
        for k, (nm, a, b) in enumerate(self._lines):
            live.add(nm)
            live = {v for v in live if last.get(v, -1) > k or v == nm}
            peak = max(peak, len(live))
        return peak

    def spill_ops(self, R):
        """Loads plus stores one step needs with R plane registers (Belady farthest-next-use; inputs start in registers
        and in memory-free state, outputs must end in registers; the constant 0 is an immediate)."""
        from bisect import bisect_left
        lines, INF = self._lines, 10 ** 10
        uses = {}
        for k, (_, a, b) in enumerate(lines):
            for v in (a, b):
                if v not in ("0", "#"):
                    uses.setdefault(v, []).append(k)
        outs = set(self.outs)

        def nxt(v, k):
            u = uses.get(v)
            if u:
                i = bisect_left(u, k)
                if i < len(u):
                    return u[i]
            return 10 ** 9 if v in outs else INF

        reg, mem, cost = {"i%d" % j for j in range(self.n)}, set(), 0
        if len(reg) > R:                                    # inputs beyond R start in memory: not a free state; spill them
            for v in sorted(reg, key=lambda y: -nxt(y, 0))[:len(reg) - R]:
                reg.discard(v)
                mem.add(v)
        for k, (nm, a, b) in enumerate(lines):
            need = [v for v in {a, b} if v not in ("0", "#")]
            for v in need:
                if v not in reg:
                    cost += 1
                    while len(reg) >= R:
                        w = max((y for y in reg if y not in need), key=lambda y: nxt(y, k))
                        reg.discard(w)
                        if w not in mem and nxt(w, k) < INF:
                            cost += 1
                            mem.add(w)
                    reg.add(v)
            for v in need:
                if nxt(v, k + 1) >= INF:
                    reg.discard(v)
            while len(reg) >= R:
                w = max(reg, key=lambda y: nxt(y, k + 1))
                reg.discard(w)
                if w not in mem and nxt(w, k + 1) < INF:
                    cost += 1
                    mem.add(w)
            reg.add(nm)
        return cost


# ---------------------------------------------------------------- 3 lane packing
def pack_lanes(xs, n, pin):
    """Stored input planes (low n) for up to 256 lane values (n-bit integers); missing lanes are 0."""
    planes = []
    for j in range(n):
        p = 0
        for l, x in enumerate(xs):
            p |= ((x >> j) & 1) << l
        planes.append(p ^ (ALL if pin[j] else 0))
    return planes


def lane_value(planes, l, pol, n):
    """The n-bit chain value of lane l from n stored planes with polarity pol."""
    x = 0
    for j in range(n):
        x |= (((planes[j] >> l) & 1) ^ pol[j]) << j
    return x


def set_lane(planes, l, x, pol, n):
    bit = 1 << l
    return [(planes[j] & ~bit) | ((((x >> j) & 1) ^ pol[j]) << l) for j in range(n)]


# ---------------------------------------------------------------- 4 validation
def digest_int(out_planes, pol, l, n):
    return lane_value(out_planes, l, pol, n)


def validate(st, lanes_total=10240, steps=1, seed=7):
    """Compare the bit-sliced step with the scalar chain f (rho.f_scalar) on lanes_total random lanes; steps > 1 chains
    the steps with the feed by renaming.  Returns (ok, lanes checked, chained steps)."""
    n, rnd = st.n, random.Random(seed)
    ok, done = True, 0
    while done < lanes_total:
        xs = [rnd.getrandbits(n) for _ in range(LANES)]
        planes, cur = pack_lanes(xs, n, st.pin), list(xs)
        for _ in range(steps):
            planes = list(st.step(*planes))
            cur = [rho.f_scalar(x, n) for x in cur]
            for l in range(LANES):
                if lane_value(planes, l, st.pout, n) != cur[l]:
                    ok = False
        done += LANES
    return ok, done, steps


def validate_full_digest(st, lanes_total=10240, seed=11):
    """n = 256 only: all 256 digest bits against rho.digest_words (the 3-round digest of 0^32 || x)."""
    rnd, ok, done = random.Random(seed), True, 0
    while done < lanes_total:
        xs = [rnd.getrandbits(256) for _ in range(LANES)]
        out = st.step(*pack_lanes(xs, 256, st.pin))
        for l in range(LANES):
            w = rho.digest_words([0] * 8 + [(xs[l] >> (32 * i)) & M32 for i in range(8)])
            if lane_value(out, l, st.pout, 256) != sum(w[i] << (32 * i) for i in range(8)):
                ok = False
        done += LANES
    return ok, done


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "--analyse"
    st = Step(256)
    print("n=256 ops", st.ops, "gates", st.gates, st.by, "source bytes", len(st.src))
    if arg == "--analyse":
        print("peak live planes", st.peak_live())
        for R in (1024, 1000, 900, 512, 256, 128, 64):
            print("spill_ops(%d) = %d" % (R, st.spill_ops(R)))
    if arg == "--validate":
        print("full digest", validate_full_digest(st))
        print("chain 1 step", validate(st, 10240, 1))
        print("chain 4 steps", validate(st, 2560, 4))
        s22 = Step(22)
        print("n=22 ops", s22.ops, "gates", s22.gates, "not fixes", len(s22.fix), "peak live", s22.peak_live())
        print("n=22 chain 1 step", validate(s22, 10240, 1), "chain 6 steps", validate(s22, 2560, 6))
