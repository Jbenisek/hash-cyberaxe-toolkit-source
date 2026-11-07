"""dev reference: rolled program listing (prefix R1,R2 straight; rounds 3..7 as a loop of one generic round body)."""
import sys, heapq
sys.path.insert(0, '.')
import bsrho_b7 as B
from bsrho_b7 import Gen, _constw, _ror_planes, GCALLS, PERM, IV, FLAGS, M32
XB, SB, WB, TB = 0, 256, 768, 1312      # x planes, state planes, message planes, first temporary register
KPRE, LOOPS = 2, 5

def rounds_on(g, v, m, k):
    for _ in range(k):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2*j], m[2*j+1]
            v[a] = g.add(g.add(v[a], v[b]), x)
            v[d] = _ror_planes(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = _ror_planes(g.xorw(v[b], v[c]), 12)
            v[a] = g.add(g.add(v[a], v[b]), y)
            v[d] = _ror_planes(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = _ror_planes(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    return v, m

def segment(g, outs, pins, inreg, base):
    nodes = g.nodes
    seen = set(s[0] for s in outs if s[0])
    for k in range(len(nodes) - 1, 0, -1):
        if k in seen and nodes[k][0] in "xao":
            seen.add(nodes[k][1]); seen.add(nodes[k][2])
    order = [k for k in range(1, len(nodes)) if k in seen and nodes[k][0] in "xao"]
    dead = len(nodes) - 1 - len(inreg) - len(order)
    last = {}
    for t, k in enumerate(order):
        last[nodes[k][1]] = t; last[nodes[k][2]] = t
    pinned = {}
    for s, r in zip(outs, pins):
        if s[0]:
            assert s[0] not in pinned
            pinned[s[0]] = r
    reg = {1 + j: r for j, r in enumerate(inreg)}
    inat = {r: 1 + j for j, r in enumerate(inreg)}
    free, nxt, top, code = [], base, base, []
    for t, k in enumerate(order):
        op, a, b = nodes[k]
        ra, rb = reg[a], reg[b]
        for v in {a, b}:
            if last[v] == t and reg[v] >= base:
                heapq.heappush(free, reg[v])
        if k in pinned:
            d = pinned[k]
            if d in inat:
                assert last.get(inat[d], -1) <= t, "input %d live" % d
        elif free:
            d = heapq.heappop(free)
        else:
            d = nxt; nxt += 1
        top = max(top, d + 1)
        reg[k] = d
        code.append(({"x": "^", "a": "&", "o": "|"}[op], d, ra, rb))
    for s, r in zip(outs, pins):
        if s[0] == 0:
            code.append(("o" if s[1] else "z", r, -1, -1))
        elif s[1]:
            code.append(("~", r, r, -1))
    return code, top, dead, g.hits

def listing(n=256):
    g = Gen(n)
    zero = _constw(0)
    m = [zero] * 8 + [[g.inputs[32*i+b] if 32*i+b < n else (0, 0) for b in range(32)] for i in range(8)]
    v = [_constw(w) for w in IV] + [_constw(w) for w in IV[:4]] + [zero, zero, _constw(64), _constw(FLAGS)]
    v, m = rounds_on(g, v, m, KPRE)
    outs = [s for w in v for s in w]
    A, top1, dead1, hits1 = segment(g, outs, [SB + i for i in range(512)], [XB + j for j in range(n)], WB)
    inreg = {1 + j: XB + j for j in range(n)}
    for s_i in range(16):
        for b in range(32):
            s = m[s_i][b]
            d = WB + 32*s_i + b
            A.append(("z", d, -1, -1) if s[0] == 0 else ("=", d, inreg[s[0]], -1))
    g2 = Gen(1024)
    v2 = [[g2.inputs[32*w+b] for b in range(32)] for w in range(16)]
    m2 = [[g2.inputs[512+32*w+b] for b in range(32)] for w in range(16)]
    v2, _ = rounds_on(g2, v2, m2, 1)
    outs2 = [s for w in v2 for s in w]
    Bc, top2, dead2, hits2 = segment(g2, outs2, [SB + i for i in range(512)], [SB + j for j in range(1024)], TB)
    M, seen = [], set()
    for s0 in range(16):
        if s0 in seen: continue
        cyc = [s0]
        while PERM[cyc[-1]] != s0: cyc.append(PERM[cyc[-1]])
        seen.update(cyc)
        for b in range(32): M.append(("=", TB + b, WB + 32*cyc[0] + b, -1))
        for i in range(len(cyc)):
            src = cyc[i+1] if i + 1 < len(cyc) else None
            for b in range(32):
                M.append(("=", WB + 32*cyc[i] + b, WB + 32*src + b if src is not None else TB + b, -1))
    F = [("^", j, SB + j, SB + 256 + j) for j in range(n)]
    flat = A + [('I', -1, -1, -1)] + Bc + [('D', -1, -1, -1), ('C', -1, -1, -1), ('Z', -1, -1, -1)] + M + [('J', -1, -1, -1)] + F
    return dict(flat=flat, nodes=max(len(g.nodes), len(g2.nodes)), A=A, B=Bc, M=M, F=F, regs=max(top1, top2, TB + 32), tops=(top1, top2), dead=(dead1, dead2), hits=(hits1, hits2), g=(g.calls, g2.calls))

ALL = (1 << 256) - 1
def interp(L, planes, n=256):
    R = [0] * (L["regs"] + 1)
    R[:n] = planes
    def ex(code):
        for op, d, a, b in code:
            if op == "^": R[d] = R[a] ^ R[b]
            elif op == "&": R[d] = R[a] & R[b]
            elif op == "|": R[d] = R[a] | R[b]
            elif op == "=": R[d] = R[a]
            elif op == "~": R[d] = R[a] ^ ALL
            elif op == "z": R[d] = 0
            elif op == "o": R[d] = ALL
    ex(L["A"])
    for it in range(LOOPS):
        ex(L["B"])
        if it < LOOPS - 1: ex(L["M"])
    ex(L["F"])
    return R[:n]

if __name__ == "__main__":
    import random, time
    t = time.time()
    L = listing(256)
    print("time", time.time() - t)
    print({k: (len(v) if isinstance(v, list) else v) for k, v in L.items()})
    nz = sum(1 for x in L["A"] if x[0] == "~"); print("NOT", nz, "z/=", sum(1 for x in L["A"] if x[0] in "z="))
    ops = len(L["A"]) + 1 + LOOPS * (len(L["B"]) + 3) + (LOOPS - 1) * (len(L["M"]) + 1) + len(L["F"])
    print("executed ops", ops, "static", len(L["A"]) + len(L["B"]) + len(L["M"]) + len(L["F"]) + 5)
    rnd = random.Random(1)
    xs = [rnd.getrandbits(256) for _ in range(256)]
    pl = B.pack_lanes(xs, 256, [0]*256)
    out = interp(L, pl)
    lanes = B.lanes_of(out, 256, [0]*256)
    print("ok", all(lanes[l] == B.f_scalar(xs[l], 256) for l in range(256)))
