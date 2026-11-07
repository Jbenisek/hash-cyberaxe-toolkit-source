# -------- 5 plan and ledger
LAMBDA = Fraction(497, 1000)       # n = 18 plan: 1 - exp(-LAMBDA) = 0.39165
CUTLOSS = Fraction(15, 100000)     # n = 18 plan: allowance for cut-trail points, as a fraction of Q
P_MIN = 0.390000001                # plan target; Appendix A proves P_F >= 0.39 exactly
GRAIN = 10 ** 24                   # B is a multiple of GRAIN
CMAX = 1                           # halt when more than CMAX trails are cut
STAGE1_PLANES, SC = 32, 13         # stage-1 planes; the OR of the first SC planes is tested first (proof 3.3)
# machine charges (proof 3.3)
LOOP_OPS = 3                       # batch counter increment, compare with the slice limit, branch
HIT_OPS = 2800                     # a stage-1 hit lane
EVENT_OPS = 3800                   # a finished trail, besides the table walk
SLOT_OPS = 64                      # table walk per finished trail and per slot (a lookup visits <= 3 S slots at 12, an insertion moves <= S at 24)
CUT_OPS = 4200                     # a cut trail
SLICE_OPS = 1300                   # slice check: 256 ages
KR, KCHK = Fraction(62, 5), 8192   # recovery: pass-1 cap c_r = ceil(12.4 L) steps; at most 8192 checkpoints per trail
REC1_OPS, REC2_OPS = 36, 39        # per recovery batch beyond the packed circuit: pass 1 (33 + checkpoint counter 3), pass 2 (39)
CHK_OPS, PROBE_OPS, REC_FIXED = 80, 100, 600   # a stored checkpoint pair; a bisection probe besides its walk; call and setup
INSTR_BYTES = 36                   # other instructions: opcode, registers and an inline 256-bit immediate
GATE_BYTES = 5                     # one register-only gate (^ & |): 8-bit opcode + three 10-bit register numbers (800 registers < 1024)
GEN_CODE = 2000                    # wasm instructions of GEN_C (clang -Os), 36 bytes each
GEN_CONST = 512                    # constant tables of GEN_C (IV, PERM, GC, KEY, COLLIB), bytes
HANDLER_CODE, SETUP_CODE, RECOVERY_CODE = 1100, 160, 150   # instructions: handlers with the table walk; setup, cut, slice; recovery besides its circuit
STAGE1_CODE = 4                    # the two compares with the all-ones immediate and the two branches of the stage-1 test (its 31 ORs are gates)
REGISTERS = 800                    # declared register file of 256-bit words, counted as memory
REGFILE = REGISTERS * 32
COUNTERS = 16384                   # trail numbers, ages, counters (8 KiB) and the plane copy of the handlers (8 KiB)
ENTRY, TBITS, META = 7, 17, 3      # table slot, 56 bits: key remainder, 17-bit trail number, 3 quotient-filter bits (proof 7)
MEM_LIMIT = 1048576                # bytes: 2^20
SPARE = 64                         # bytes under the limit outside tmax slots (the table's extra slot is taken from them)
ADVICE = 32                        # nonuniform advice: the prefix KEY
KEY_OPS = 0                        # offline choice of KEY, charged (python3 bsrho.py --choose-key, proof 3.7)
TAIL_LOG2 = -40
KAPPA_256 = 20
GEN_FACTOR = 200                   # word operations charged per generator primitive call and per emitted line
GEN_STATE = 2400                   # generator state words (v 2,048, tmp and mw 128 each, free-register bitmap 96)
GEN_STACK = 2048                   # shadow stack of the generator
GEN_INFO = 68                      # result record of the generator
SETUP_FIXED = 256 * 3100 + 20000   # 256 starts inserted in memory, reloaded, random word, counters
CFG = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 20: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}


def stage1_ops(s1):
    """(operations of every batch, extra operations of a passing batch): k = min(SC, s1) planes ORed (k - 1), compared with all ones and
    a branch; a passing batch ORs the other s1 - k planes, compares and branches.  The complement of the hit mask is in the hit handler."""
    k = min(SC, s1)
    return k - 1 + 2, s1 - k + 2


def stage1(planes, p, cnt):
    """Mask of the lanes whose s1 low bits are zero (upright planes).  A batch whose first k planes OR to all ones stops there; a passing
    batch is counted against the budget pmax (a halt) and ORs the rest."""
    k, acc = min(SC, p["s1"]), 0
    for j in range(k):
        acc |= planes[j]
    if acc == ALL:
        return 0
    cnt["passing"] += 1
    if cnt["passing"] > p["pmax"]:
        raise Halt("stage-1 checkpoint budget")
    for j in range(k, p["s1"]):
        acc |= planes[j]
    return ALL ^ acc


def keybits(tmax):
    """Key bits of an entry: the 36 stored remainder bits plus the l = floor(log2(tmax + 1)) quotient bits the slot implies."""
    return 8 * ENTRY - TBITS - META + (tmax + 1).bit_length() - 1


INFLIGHT = 350                     # n = 18 plan only (sum of 256 exponential ages, units of L)


def _plan(n, Tp, kappa, tmax, Sb):
    c = CFG[n]
    s1, W = c["s1"], c["W"]
    N, D = 1 << n, s1 + W
    L = Fraction(1 << D, Tp)
    if n == 256:
        assert LANES + tmax + CMAX < 1 << TBITS and KCHK * 64 <= ENTRY * (tmax + 1)   # trail numbers fit; checkpoints fit in the table region
        B = _b256(Tp, tmax, kappa, Sb)
    else:                                                     # reduced widths: the plan of the 18-bit experiment
        ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
        num, den = ureq + INFLIGHT * L + 1, CUTLOSS.denominator
        q = -(-(num * den) // (den - CUTLOSS.numerator))
        B = -(-q // LANES)
    cc = -(-kappa * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    pk = 1 - Fraction((1 << SC) - 1, 1 << SC) ** LANES           # P(a batch passes the first SC planes), 256 uniform lanes
    big = n == 256
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(keybits(tmax) - fb, n - D), L=L, N=N, Q=B * LANES, B=B, kappa=kappa, Sb=Sb,
                c=cc, capr=cc + Sb, cr=-(-(KR * L.numerator) // L.denominator) if big else cc + Sb, tmax=tmax,
                e2max=2 * B * LANES // (1 << s1) + 64, pmax=-(-(2 * B * pk.numerator) // pk.denominator) + 64 if big else 10 ** 9,
                cmax=CMAX if big else 10 ** 9)


def tail_log2(mean, k):
    """log2 of the Chernoff bound exp(-mean) (e mean / k)^k on P(count >= k), k > mean."""
    return (-mean + k * (1 + log(mean / k))) / log(2)


_STEP256 = {}


def step256():
    if 256 not in _STEP256:
        _STEP256[256] = Step(256)
    return _STEP256[256]


def machine_constants(st=None, R=REGISTERS):
    """(PH, per-batch stage 1, passing extra, BODY, code bytes, tmax) of the n = 256 program with R registers (spills added to the body)."""
    st = st or step256()
    ph = st.ops
    per, rest = stage1_ops(STAGE1_PLANES)
    body = ph + (st.spill_ops(R) if R < REGISTERS else 0) + per + LOOP_OPS
    code = (ph + STAGE1_PLANES - 1 + packed_circuit(st.qwords)[1]) * GATE_BYTES + (
        body - ph - per + STAGE1_CODE + HANDLER_CODE + SETUP_CODE + RECOVERY_CODE) * INSTR_BYTES
    tmax = (MEM_LIMIT - SPARE - code - R * 32 - COUNTERS - ADVICE) // ENTRY
    return ph, per, rest, body, code, tmax


def gen_scratch(nodes=None):
    """Scratch bytes of GEN_C: 8-bit use counts (one byte per node of the n = 256 network), state, constants, shadow stack, result record."""
    nodes = nodes or len(trace(256)[0].nodes)
    uses = nodes + 1
    return uses + GEN_STATE + GEN_CONST + GEN_STACK + GEN_INFO, uses, nodes


def phase_bytes(code, tmax):
    """(setup phase, search phase) resident bytes.  Setup: code, advice, counters, the generator's image and scratch.  Search: code, advice,
    counters, register file and the table of tmax + 1 slots; the generator's image and scratch are overwritten by the table and registers."""
    return code + ADVICE + COUNTERS + GEN_CODE * INSTR_BYTES + gen_scratch()[0], code + ADVICE + COUNTERS + REGFILE + ENTRY * (tmax + 1)


def plan(n, kappa=None, Tp=None, R=REGISTERS):
    if n != 256:
        c = CFG[n]
        p = _plan(n, c["Tp"], c["kappa"], 0, c["Sb"])
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    kappa = kappa or KAPPA_256
    tmax = machine_constants(None, R)[5]
    if Tp:
        return _plan(256, Tp, kappa, tmax, CFG[256]["Sb"])
    lo, hi = 1.0, float(tmax + 1)                        # largest mean number of trails the table holds (tail 2^-40)
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= TAIL_LOG2 else (lo, mid)
    ok = lambda t: _lossq(t, lo, tmax, kappa, CFG[256]["Sb"])["P_lower"] >= P_MIN
    a, b = 1000, 4095                                    # bisection for the largest Tp (monotone); a passes, a + 1 fails
    if not ok(a):
        return None
    while b - a > 1:
        mm = (a + b) // 2
        a, b = (mm, b) if ok(mm) else (a, mm)
    assert ok(a) and not ok(a + 1)
    return _plan(256, a, kappa, tmax, CFG[256]["Sb"])


def rec_ops(p, pk):
    """Recovery bound: pass 1 at most c_r batches; the checkpoint pairs; pass 2 at most 17 D batches (16 single-lane walks of at most
    D - 1 steps and one joint walk of at most D) and 16 probes; call and setup."""
    D = -(-p["cr"] // KCHK)
    return p["cr"] * (pk + REC1_OPS) + KCHK * CHK_OPS + 17 * D * (pk + REC2_OPS) + 16 * PROBE_OPS + REC_FIXED


def ledger(p=None, st=None, R=REGISTERS):
    """Operation budget in word operations (exact); time is operations / UNIT."""
    p = p or plan(256, None, None, R)
    st = st or step256()
    ph, per, rest, body, code, _ = machine_constants(st, R)
    gen = GEN_FACTOR * (2 * st.gen_calls + st.ops)           # the generator builds the network twice (use counts, then emission)
    parts = dict(main=body * p["B"], stage1_rest=p["pmax"] * rest, slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS, events=p["tmax"] * (EVENT_OPS + SLOT_OPS * (p["tmax"] + 1)),
                 cuts=p["cmax"] * CUT_OPS, recovery=rec_ops(p, packed_circuit(st.qwords)[1]), setup=SETUP_FIXED + gen, key_choice=KEY_OPS)
    return dict(parts=parts, total=sum(parts.values()), plan=p, body=body, gen=gen)


def _lossq(Tp, q, tmax, kappa, Sb, rate=1.0, fine=20000, coarse=2000):
    """Lemma 2 of proof Section 4 for q = Q / L trails; `rate` scales the collision hazard (H1 (d) sensitivity)."""
    L = Fraction(1 << 122, Tp)
    c = -(-kappa * L.numerator // L.denominator)
    th, Lf, cf, kr = Tp / 2.0 ** 122, float(L), float(c), float(KR) * float(L)
    Q, B, Np = q * Lf, q * Lf / LANES, 2.0 ** 256 / rate         # Q evaluations, B batches, N' (theta N is below float resolution)
    k = int(q) + 1
    while tail_log2(q, k) > -40:                                   # N1 ~ Binomial(Q, theta) <= k - 1 except with probability 2^-40
        k += 1
    n2, shift = k + LANES + 1, 1 / (1 - k * Q / Np)
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))                    # Pi_m <= this; the collision term uses Pi_(Q-k+1) <= Pi_Q shift
    split = max(1.0, Q - 120 * LANES * Lf)                         # the detection penalty lives on the last 120 L batches: fine bins there
    edges = [split * i / coarse for i in range(coarse + 1)] + [split + (Q - split) * i / fine for i in range(1, fine + 1)]
    delay, pa = 0.0, 1.0
    for b in edges[1:]:
        pb = pi(b)
        delay += (pa - pb) * exp(-th * max(0.0, B - b / LANES))   # sum of (Pi_a - Pi_b) (1 - theta)^(B - ceil(b / 256)) over the bins (a, b]
        pa = pb
    p, ql, hq = exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np)
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** TBITS * Q) / Np
    t = dict(collision=pi(Q) * shift, delay=delay * shift, own_trail=ql, long_partner=(cf + Sb) * Q * p * (q + LANES) / ((1 - p) * Np), age_cap=hq * p2,
             rec_cap=2 * hq * exp(-(kr - 1) * th) * (1 + (kr - 1) * th / (1 - th)),
             disturbance=hq * Lf * (Q + 2.0 ** TBITS) / Np, finished_count=2.0 ** -40,
             cut_halt=-expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa),
             key_false_match=tmax * (tmax - 1) / 2 * 2.0 ** -(min(keybits(tmax) - (Tp - 1).bit_length(), 134) + log(Tp, 2)),
             table_capacity=2.0 ** tail_log2(q, tmax - 59),
             tiny=Q * 2.0 ** TBITS / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** -90)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - t["sum"]
    t.update(trails=q, k=k, n2=n2, p=p, p2=p2, ql=ql, hq=hq, hh=hh, shift=shift)
    return t


_B = {}


def _b256(Tp, tmax, kappa, Sb):
    """The least B (multiple of GRAIN) with P_lower >= P_MIN."""
    if (Tp, tmax, kappa) not in _B:
        L = Fraction(1 << 122, Tp)
        lo, hi = 1.0, float(tmax + 1)
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if _lossq(Tp, mid, tmax, kappa, Sb)["P_lower"] >= P_MIN else (mid, hi)
        B = -(-int(hi * L / LANES) // GRAIN) * GRAIN
        while _lossq(Tp, float(B * LANES / L), tmax, kappa, Sb)["P_lower"] < P_MIN:
            B += GRAIN
        _B[(Tp, tmax, kappa)] = B
    return _B[(Tp, tmax, kappa)]


def loss(p, rate=1.0):
    """The probability losses of proof Section 4 (floats): the terms, their sum and the lower bound on the success probability."""
    return _lossq(p["Tp"], float(p["Q"] / p["L"]), p["tmax"], p["kappa"], p["Sb"], rate)


# -------- 6 search, table and recovery
class Halt(Exception):
    pass


class Engine:
    """The chain function g = f XOR q in two forms: step(planes) for 256 lanes and f2(xs) for the recovery (packed circuit with the XOR of q)."""

    def __init__(self, n):
        self.n = n
        st = Step(n)
        self.st, self.pin, self.step = st, st.pin, st.step

    def f2(self, xs):
        return packed_f(xs, self.n, self.st.qwords)

    def g_scalar(self, x):
        return f_scalar(x, self.n) ^ self.st.qint


class IdealEngine:
    """An ideal function of the same width (keyed blake2b) used as the control of test T3."""

    def __init__(self, n, key):
        self.n, self.key, self.pin = n, key, [0] * n
        self.nb = (n + 7) // 8

    def g(self, v):
        h = hashlib.blake2b(v.to_bytes(self.nb, "little"), key=self.key, digest_size=self.nb).digest()
        return int.from_bytes(h, "little") & ((1 << self.n) - 1)

    def step(self, *planes):
        vals = lanes_of(planes, self.n, self.pin)
        return pack_lanes([self.g(v) for v in vals], self.n, self.pin)

    def f2(self, xs):
        return [self.g(x) for x in xs]


def is_dp(x, p):
    """Mixed distinguished point: low s1 bits zero and the window above them below Tp."""
    return x & ((1 << p["s1"]) - 1) == 0 and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]


def dp_key(x, p):
    """The kb bits above the window, then the fb low bits of the window value (which determine it)."""
    return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))


class QF:
    """The table: a quotient filter of S slots (Bender et al., VLDB 2012).  A key of kb bits = quotient (top l bits, l = floor(log2 S):
    the home slot) and remainder (kb - l bits, stored with the trail number and the bits occupied, continuation, shifted).  The entries of
    one quotient form a run; runs lie in quotient order, shifted right (cyclically) past used slots.  The program never stores S keys, so
    a slot stays empty and every walk ends."""

    def __init__(self, S, kb):
        self.S, self.l = S, min(kb, S.bit_length() - 1)
        self.rb, self.n = kb - self.l, 0
        self.occ, self.cont, self.shf, self.rem, self.tr = ([0] * S for _ in range(5))

    def _start(self, h):
        """First slot of the run of home slot h (occ[h] set): back to the start of the cluster, then forward one run per occupied slot."""
        S, b = self.S, h
        while self.shf[b]:
            b = (b - 1) % S
        x = b
        while b != h:
            x = (x + 1) % S
            while self.cont[x]:
                x = (x + 1) % S
            b = (b + 1) % S
            while not self.occ[b]:
                b = (b + 1) % S
        return x

    def find(self, key):
        """(trail number, None) if key is stored; else (None, (h, x, c)): the slot x where key goes (the end of its run, c = 1, or the
        place of a new run, c = 0)."""
        h, r = key >> self.rb, key & ((1 << self.rb) - 1)
        if not self.occ[h]:
            self.occ[h] = 1
            x = self._start(h)
            self.occ[h] = 0
            return None, (h, x, 0)
        x = self._start(h)
        while True:
            if self.rem[x] == r:
                return self.tr[x], None
            x = (x + 1) % self.S
            if not self.cont[x]:
                return None, (h, x, 1)

    def put(self, key, t, at):
        """Store (remainder, t) at slot x; the entries from x up to the first empty slot move one slot right (shifted set)."""
        h, x, c = at
        r = key & ((1 << self.rb) - 1)
        assert t < 1 << TBITS and self.n < self.S - 1
        self.occ[h], e = 1, (r, t, c, int(x != h))
        while self.cont[x] or self.shf[x] or (self.occ[x] and (x != h or c)):
            e, (self.rem[x], self.tr[x], self.cont[x], self.shf[x]) = (self.rem[x], self.tr[x], self.cont[x], 1), e
            x = (x + 1) % self.S
        self.rem[x], self.tr[x], self.cont[x], self.shf[x] = e
        self.n += 1


def walk(xs, k, f2):
    for _ in range(k):
        xs = f2(xs)
    return xs


def recover(p, r, t0, t1, f2, kchk=KCHK):
    """Two trails t0, t1 with the same key.  Pass 1 walks both from their starts together (two lanes of one packed batch per step) until
    each is at a DP, at most c_r steps (else a halt), keeping every D-th point of each (D = ceil(c_r / kchk)).  Pass 2: A = the longer
    trail, d = l1 - l2, P(j): A_(j + d) = B_j is false, then true.  Unequal ends (P(l2) false) or P(0) true (B starts on A): no pair.
    Bisection over the checkpoints: P(lo D) false, P(min(hi D, l2)) true (a probe walks A d mod D steps from a checkpoint); then both
    walk together to the first equal outputs.  Returns (x, y), x != y, g(x) = g(y), or None."""
    mask, cr = p["N"] - 1, p["cr"]
    D = -(-cr // kchk)
    xs, ls, ends = [(r + t0) & mask, (r + t1) & mask], [None, None], [None, None]
    ck = [[xs[0]], [xs[1]]]
    for k in range(1, cr + 1):
        xs = f2(xs)
        for i in (0, 1):
            if ls[i] is None:
                if k % D == 0:
                    ck[i].append(xs[i])
                if is_dp(xs[i], p):
                    ls[i], ends[i] = k, xs[i]
        if None not in ls:
            break
    else:
        raise Halt("recovery length")
    a = 0 if ls[0] >= ls[1] else 1
    lb, (qd, rd) = ls[1 - a], divmod(abs(ls[0] - ls[1]), D)
    A = lambda i: walk([ck[a][i + qd]], rd, f2)[0]              # A_(i D + d)
    if ends[0] != ends[1] or A(0) == ck[1 - a][0]:
        return None
    lo, hi = 0, lb // D + 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if A(mid) == ck[1 - a][mid] else (mid, hi)
    x, y = A(lo), ck[1 - a][lo]
    for _ in range(min(hi * D, lb) - lo * D):
        fx, fy = f2([x, y])
        if fx == fy:
            return x, y
        x, y = fx, fy
    return None


def search(eng, p, r, cnt):
    """One attempt with the fresh random word r: the pair (x, y) or None.  Raises Halt at a budget.  Budgets: B batches, pmax passing
    batches, e2max stage-1 hits, tmax table keys, cmax cut trails, a recovery of at most c_r pass-1 batches."""
    n, mask, pin = p["n"], p["N"] - 1, eng.pin
    assert not any(pin)
    table, births, ts, nxt = QF(p["tmax"] + 1, p["kb"] + p["fb"]), [0] * LANES, list(range(LANES)), LANES
    planes = pack_lanes([(r + t) & mask for t in ts], n, pin)
    cnt["inserts"] += LANES
    batches = 0
    while batches < p["B"]:
        planes = list(eng.step(*planes))
        batches += 1
        cnt["batches"] += 1
        hit = stage1(planes, p, cnt)
        while hit:
            cnt["stage1_hits"] += 1
            if cnt["stage1_hits"] > p["e2max"]:
                raise Halt("stage-1 budget")
            l = (hit & -hit).bit_length() - 1
            hit &= hit - 1
            x = lane_value(planes, l, pin, n)
            if is_dp(x, p):
                key = dp_key(x, p)
                cnt["finished"] += 1
                t0, at = table.find(key)
                if t0 is not None:
                    cnt["recoveries"] += 1
                    res = recover(p, r, t0, ts[l], eng.f2)
                    if res is None:
                        raise Halt("recovery found no pair")
                    return res
                if table.n >= p["tmax"]:
                    raise Halt("table full")
                table.put(key, ts[l], at)
                ts[l], nxt, births[l] = nxt, nxt + 1, batches
                planes = set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                cnt["inserts"] += 1
        if batches % p["Sb"] == 0:
            for l in range(LANES):
                if batches - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    if cnt["cut"] > p["cmax"]:
                        raise Halt("cut budget")
                    ts[l], nxt, births[l] = nxt, nxt + 1, batches
                    planes = set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                    cnt["inserts"] += 1
    return None


