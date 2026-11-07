"""Builds bsrho.py of B3R7b from the b7 file (bsrho_b7.py): rolled program (rounds 1-2 straight, rounds 3-7 as a loop of one generic round).
usage: python3 -B patch_b8.py > bsrho_b8.py  (GEN_C is embedded separately by embed_gen.py)"""
import re, sys
s = open("bsrho_b7.py", encoding="utf-8", newline="").read()

NEW = r'''def _rounds(g, v, m, k):
    """k rounds on the signal words v (16 words of 32 planes) with the message words m (16 words); returns v and the permuted m."""
    for _ in range(k):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
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


# -------- 4 the rolled program and its register allocation
# Registers (256-bit planes): x planes 0..n-1 (input and output of the chain step), state words 256..767, message slots 768..1279, temporaries of the loop body 1312...
# Program: rounds 1 and 2 straight line (constants folded), complement of the planes stored inverted, message slots of round 3, then LOOPS = 5 times one generic round
# (every message slot is a real operand: no zero word is folded), the permutation of the message slots by plane copies between iterations, the 256 output XORs.
XB, SB, WB, TB, KPRE = 0, 256, 768, 1312, 2
LOOPS = ROUNDS - KPRE
NONE = -1


def _segment(g, outs, pins, inreg, base):
    """Straight-line code of the network g: gate nodes in creation order, input node 1 + j in register inreg[j], output signal k in register pins[k] (a plane stored
    inverted gets one complement), temporaries from register base (a register is freed at the last use of its value, the lowest free register is taken)."""
    import heapq
    nodes = g.nodes
    seen = set(t[0] for t in outs if t[0])
    for k in range(len(nodes) - 1, 0, -1):
        if k in seen and nodes[k][0] in "xao":
            seen.add(nodes[k][1])
            seen.add(nodes[k][2])
    order = [k for k in range(1, len(nodes)) if k in seen and nodes[k][0] in "xao"]
    last, pinned, reg = {}, {}, {1 + j: r for j, r in enumerate(inreg)}
    for t, k in enumerate(order):
        last[nodes[k][1]] = last[nodes[k][2]] = t
    for t, r in zip(outs, pins):
        if t[0]:
            pinned[t[0]] = r
    inat = {r: 1 + j for j, r in enumerate(inreg)}
    free, nxt, top, code = [], base, base, []
    for t, k in enumerate(order):
        op, a, b = nodes[k]
        ra, rb = reg[a], reg[b]
        for u in {a, b}:
            if last[u] == t and reg[u] >= base:
                heapq.heappush(free, reg[u])
        if k in pinned:
            d = pinned[k]
            if d in inat and last.get(inat[d], -1) > t:
                raise ValueError("input plane in register %d still needed" % d)
        elif free:
            d = heapq.heappop(free)
        else:
            d = nxt
            nxt += 1
        top = max(top, d + 1)
        reg[k] = d
        code.append(({"x": "^", "a": "&", "o": "|"}[op], d, ra, rb))
    for t, r in zip(outs, pins):
        if t[0] == 0:
            code.append(("o" if t[1] else "z", r, NONE, NONE))
        elif t[1]:
            code.append(("~", r, r, NONE))
    return code, top, len(nodes) - 1 - len(inreg) - len(order), g.hits, g.calls


def listing(n=256):
    """The program for the low n input planes: dict with the code blocks A (rounds 1, 2, complements, message slots of round 3), B (loop body: one round), M (message
    permutation), F (output XORs), the flat listing (A, I, B, D, C, Z, M, J, F), registers used, dead gates, shared gates, generator calls (one pass)."""
    g = Gen(n)
    zero = _constw(0)
    m = [zero] * 8 + [[g.inputs[32 * i + b] if 32 * i + b < n else ZERO for b in range(32)] for i in range(8)]
    v = [_constw(w) for w in IV] + [_constw(w) for w in IV[:4]] + [zero, zero, _constw(64), _constw(FLAGS)]
    v, m = _rounds(g, v, m, KPRE)
    A, top1, dead1, hits1, c1 = _segment(g, [t for w in v for t in w], [SB + i for i in range(512)], [XB + j for j in range(n)], WB)
    for s in range(16):
        for b in range(32):
            t = m[s][b]
            A.append(("z", WB + 32 * s + b, NONE, NONE) if t[0] == 0 else ("=", WB + 32 * s + b, XB + t[0] - 1, NONE))
    g2 = Gen(1024)
    v2 = [[g2.inputs[32 * w + b] for b in range(32)] for w in range(16)]
    m2 = [[g2.inputs[512 + 32 * w + b] for b in range(32)] for w in range(16)]
    v2, _ = _rounds(g2, v2, m2, 1)
    Bc, top2, dead2, hits2, c2 = _segment(g2, [t for w in v2 for t in w], [SB + i for i in range(512)], [SB + j for j in range(1024)], TB)
    assert all(c[0] in "^&|" for c in Bc)
    M, seen = [], set()
    for s0 in range(16):                                      # slot s takes slot PERM[s]; one temporary word (registers TB..) per cycle
        if s0 in seen:
            continue
        cyc = [s0]
        while PERM[cyc[-1]] != s0:
            cyc.append(PERM[cyc[-1]])
        seen.update(cyc)
        M += [("=", TB + b, WB + 32 * s0 + b, NONE) for b in range(32)]
        for i, c in enumerate(cyc):
            M += [("=", WB + 32 * c + b, WB + 32 * cyc[i + 1] + b if i + 1 < len(cyc) else TB + b, NONE) for b in range(32)]
    F = [("^", j, SB + j, SB + 256 + j) for j in range(n)]
    ctl = lambda o: (o, NONE, NONE, NONE)
    flat = A + [ctl("I")] + Bc + [ctl("D"), ctl("C"), ctl("Z")] + M + [ctl("J")] + F
    ops = len(A) + 1 + LOOPS * (len(Bc) + 3) + (LOOPS - 1) * (len(M) + 1) + len(F)       # operations executed by one step (I once; D, C, Z per iteration; J 4 times)
    return dict(A=A, B=Bc, M=M, F=F, flat=flat, regs=max(top1, top2, TB + 32), dead=dead1 + dead2, hits=hits1 + hits2, calls=c1 + c2, ops=ops, instr=len(flat),
                nodes=max(len(g.nodes), len(g2.nodes)))


def run_listing(flat, planes, n, regs):
    """Interpreter of the flat listing on a register file (the loop: I sets the counter, D decrements, C compares, Z leaves the loop, J jumps back)."""
    R = [0] * (regs + 1)
    R[:n] = planes
    pc, cnt, flag, top = 0, 0, False, 0
    jend = max(i for i, c in enumerate(flat) if c[0] == "J")
    while pc < len(flat):
        op, d, a, b = flat[pc]
        pc += 1
        if op == "^":
            R[d] = R[a] ^ R[b]
        elif op == "&":
            R[d] = R[a] & R[b]
        elif op == "|":
            R[d] = R[a] | R[b]
        elif op == "=":
            R[d] = R[a]
        elif op == "~":
            R[d] = R[a] ^ ALL
        elif op == "z":
            R[d] = 0
        elif op == "o":
            R[d] = ALL
        elif op == "I":
            cnt, top = LOOPS, pc
        elif op == "D":
            cnt -= 1
        elif op == "C":
            flag = cnt == 0
        elif op == "Z" and flag:
            pc = jend + 1
        elif op == "J":
            pc = top
    return R[:n]


def _compile(code, K=2000):
    """Python functions f(R) executing the code on the register list R, in chunks of K lines (a single huge function needs 100 MB to compile)."""
    fns = []
    for s0 in range(0, len(code), K):
        ch, rd, wr, body = code[s0:s0 + K], [], set(), []
        for op, d, a, b in ch:
            for r in (a, b):
                if r >= 0 and r not in wr and r not in rd:
                    rd.append(r)
            body.append("r%d=" % d + {"^": "r%d^r%d" % (a, b), "&": "r%d&r%d" % (a, b), "|": "r%d|r%d" % (a, b), "=": "r%d" % a, "~": "r%d^ALL" % a, "z": "0", "o": "ALL"}[op])
            wr.add(d)
        src = "def c(R):\n" + ("    %s=%s\n" % (",".join("r%d" % r for r in rd), ",".join("R[%d]" % r for r in rd)) if rd else "")
        src += "".join("    %s\n" % x for x in body) + "".join("    R[%d]=r%d\n" % (r, r) for r in sorted(wr))
        ns = {"ALL": ALL}
        exec(compile(src, "<rolled-step>", "exec"), ns)
        fns.append(ns["c"])
    return fns


class Step:
    """The chain step for width n (256 lanes).  step(*planes) takes the n input planes (upright) and returns the n output planes: the digest planes upright (q = 0), so
    the chain is x -> g(x) = f(x) (low n bits).  ops = operations executed by one step, instr = instructions of its code, regs = registers used."""

    def __init__(self, n=256):
        L = listing(n)
        self.n, self.pin, self.qint, self.qwords = n, [0] * n, 0, [0] * 8
        self.L, self.ops, self.instr, self.regs = L, L["ops"], L["instr"], L["regs"]
        self.hits, self.dead, self.gen_calls, self.flat = L["hits"], L["dead"], L["calls"], L["flat"]
        self.fa, self.fb, self.fm, self.ff = _compile(L["A"]), _compile(L["B"]), _compile(L["M"]), _compile(L["F"])

    def step(self, *x):
        R = [0] * self.regs
        R[:self.n] = x
        for f in self.fa:
            f(R)
        for i in range(LOOPS):
            for f in self.fb:
                f(R)
            if i < LOOPS - 1:
                for f in self.fm:
                    f(R)
        for f in self.ff:
            f(R)
        return tuple(R[:self.n])


'''
i = s.index("def trace(n):")
j = s.index("# -------- lane transposition, packing, extraction")
s = s[:i] + NEW + s[j:]
# Gen section header / numbering
s = s.replace("# -------- 3 bit-sliced generator", "# -------- 3 bit-sliced generator")
open("bsrho_b8_stage1.py", "w", encoding="utf-8", newline="").write(s)
print("stage1", len(s))


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:60], s.count(old))
    s = s.replace(old, new)


rep("REGISTERS = 800                    # declared register file of 256-bit words, counted as memory (the generated line needs 771)",
    "REGISTERS = 1856                   # declared register file of 256-bit words, counted as memory (the program uses 1,827, 29 spare)")
rep("MEM_LIMIT = 1912336                   # bytes; 2^20 is not binding at 7 rounds (the program alone exceeds it); the claim pays log2(memory / 2^20), proof 3.8",
    "MEM_LIMIT = 1048576                   # bytes: 2^20")
rep("GEN_CODE = 1437                    # wasm instructions of GEN_C compiled with clang -Os, 36 bytes each",
    "GEN_CODE = 2249                    # wasm instructions of GEN_C compiled with clang -Os, 36 bytes each")
rep("GEN_STATE = 2400                   # generator state words (v 2,048, tmp and mw 128 each, free-register bitmap 96)",
    "GEN_STATE = 2432                   # generator state words (v 2,048, tmp, mw and the free-register bitmap 128 each)")
rep('''def other_code(st=None):
    """Instructions besides the main body: handlers 1,000, recovery (the packed circuit with the 8 XORs of q, plus 47), setup, cut and slice 160."""''',
    '''def other_code(st=None):
    """Instructions besides the main body: handlers 1,000, recovery (the packed circuit, plus 47), setup, cut and slice 160."""''')
rep('''def machine_constants(st=None, R=REGISTERS):
    """(PH, FILT, BODY, code bytes, tmax) of the n = 256 program with R registers (spill loads and stores added to the body)."""
    st = st or step256()
    ph = st.ops
    filt = stage1_ops(st.pin, STAGE1_PLANES)
    body = ph + (st.spill_ops(R) if R < REGISTERS else 0) + filt + LOOP_OPS
    code = (body + other_code(st)) * INSTR_BYTES
    tmax = (MEM_LIMIT - SPARE - code - R * 32 - COUNTERS - ADVICE) // ENTRY
    return ph, filt, body, code, tmax''',
    '''def machine_constants(st=None):
    """(PH, FILT, BODY, code bytes, tmax) of the n = 256 program: PH = operations executed by one step, BODY = PH + filter + loop control (operations per batch),
    code bytes = 36 per instruction of the step, the filter, the batch loop and the other code."""
    st = st or step256()
    assert st.regs <= REGISTERS
    ph = st.ops
    filt = stage1_ops(st.pin, STAGE1_PLANES)
    body = ph + filt + LOOP_OPS
    code = (st.instr + filt + LOOP_OPS + other_code(st)) * INSTR_BYTES
    tmax = (MEM_LIMIT - SPARE - code - REGFILE - COUNTERS - ADVICE) // ENTRY
    return ph, filt, body, code, tmax''')
rep('''def gen_scratch(nodes=None):
    """Scratch bytes of the runtime generator (the C port GEN_C, two passes, no node table): 8-bit use counts (a node is used up to 19 times at 7 rounds), one byte per node, for the nodes of the n = 256 network
    (constant, 256 inputs, one per gate), the signal state, the shadow stack and the result record.  Returns (total, use counts, nodes)."""
    nodes = nodes or len(trace(256)[0].nodes)
    assert nodes < 1 << 16
    uses = nodes + 1
    return uses + GEN_STATE + GEN_STACK + GEN_INFO, uses, nodes''',
    '''def gen_scratch(nodes=None):
    """Scratch bytes of the runtime generator (the C port GEN_C, two passes per segment, no node table): per node of the larger segment an 8-bit use count and a 16-bit output
    register (constant, inputs, one node per gate), the signal state, the shadow stack and the result record.  Returns (total, use counts and pins, nodes)."""
    nodes = nodes or step256().L["nodes"] + 1
    assert nodes < 1 << 16
    uses = 3 * nodes
    return uses + GEN_STATE + GEN_STACK + GEN_INFO, uses, nodes''')
rep('''def plan(n, kappa=None, Tp=None, R=REGISTERS):''', '''def plan(n, kappa=None, Tp=None):''')
rep('''    tmax = machine_constants(None, R)[4]''', '''    tmax = machine_constants()[4]''')
rep('''def ledger(p=None, st=None, R=REGISTERS):''', '''def ledger(p=None, st=None):''')
rep('''    p = p or plan(256, None, None, R)''', '''    p = p or plan(256)''')
rep('''    ph, filt, body, code, _ = machine_constants(st, R)
    gen = GEN_FACTOR * (2 * st.gen_calls + st.ops)           # the generator builds the network twice (use counts, then emission)''',
    '''    ph, filt, body, code, _ = machine_constants(st)
    gen = GEN_FACTOR * (2 * st.gen_calls + st.instr)         # the generator builds each segment twice (use counts, then emission); one line per emitted instruction''')
open("bsrho_b8_stage2.py", "w", encoding="utf-8", newline="").write(s)
print("stage2", len(s))

rep('''    print("n=256 step: ops", st.ops, "gates", st.gates, st.by, "peak live", st.peak_live(), "spill_ops(1024)", st.spill_ops(1024), "q weight", bin(st.qint).count("1"))
    code, regs = allocate(st)
    print("allocation: registers used", regs, "moves 0 (output j in register j)")
    pl0 = [rnd.getrandbits(256) for _ in range(256)]
    good = run_allocated(st, code, pl0) == list(st.step(*pl0))
    print("allocated code on a register file equals the step:", good)
    ok &= good''',
    '''    L = st.L
    print("n=256 program: instructions", st.instr, "(A %d, B %d, M %d, F %d), operations per step %d, registers %d" % (len(L["A"]), len(L["B"]), len(L["M"]), len(L["F"]), st.ops, st.regs))
    pl0 = [rnd.getrandbits(256) for _ in range(256)]
    good = run_listing(st.flat, pl0, 256, st.regs) == list(st.step(*pl0))
    print("flat listing on a register file (interpreter with the loop control) equals the compiled step:", good)
    ok &= good''')
open("bsrho_b8_stage3.py", "w", encoding="utf-8", newline="").write(s)

i = s.index('        for R in (512, 256):')
j = s.index('        st = step256()\n        ph, filt, body, code, tmax = machine_constants(st)')
s = s[:i] + s[j:]
rep('''        print("PH", ph, "filter", filt, "body", body, "code bytes", code, "tmax", tmax, "generator calls", st.gen_calls)''',
    '''        print("PH", ph, "filter", filt, "body", body, "code bytes", code, "tmax", tmax, "generator calls (one pass)", st.gen_calls, "instructions", st.instr, "registers", st.regs)''')
rep('''        print("memory bytes", ENTRY * tmax + code + REGFILE + COUNTERS + ADVICE, "limit", MEM_LIMIT)''',
    '''        print("memory bytes", ENTRY * tmax + code + REGFILE + COUNTERS + ADVICE, "limit", MEM_LIMIT, "main code instructions", st.instr + filt + LOOP_OPS)''')
rep('''        print("other code instructions", other_code(st), "main body", body, "total instructions", body + other_code(st))''',
    '''        print("other code instructions", other_code(st), "step instructions", st.instr, "total instructions", st.instr + filt + LOOP_OPS + other_code(st))''')
open("bsrho_b8_stage3.py", "w", encoding="utf-8", newline="").write(s)
print("stage3", len(s))
