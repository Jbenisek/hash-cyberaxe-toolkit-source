# ---------------------------------------------------------------- 3 plan and ledger
U_UNROLL = 16                      # batches per loop body (one group); loop control is 3 operations per body, plus 1 register move
KAPPA = 12                         # trail age cap in units of L = 1/theta
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165; the proof spends about 3e-4 of the 1.65e-3 above 0.39
INFLIGHT = 28                      # points of the 7 unfinished trails at the halt, in units of L (proof, Lemma 2)
CUTLOSS = Fraction(15, 100000)     # points on trails cut at the age cap, as a fraction of Q (proof, Lemma 2)
DP_EVENT_OPS = 700                 # one finished trail: lane extraction, fingerprint, restart (upper bound)
STAGE2_OPS = 300                   # the batch event itself when a lane of the filter word is zero (upper bound)
REPLAY_OPS = 200                   # per group replay besides its batches: 8 restores + 16 * (4 filter + 2 call/return + 3 loop) = 152, rounded up
RECOVER_EXTRA = 64                 # per recovery batch: 8 shr + 8 xor + 7 or + 1 and + compare + branch = 26, loop add + compare + branch = 3, 29 needed (proof 3.3)
ENTRY = 25                         # table entry bytes: key 8, trail number 2, length 15
RECOVERY_CODE, HANDLER_CODE, REPLAY_CODE = 640, 170, 40    # instructions besides the main body (proof 7)
INSTR_BYTES = 36                   # opcode, registers and an inline 256-bit immediate
COUNTERS, REGFILE = 2048, 2048     # bytes: counters and ages; 64 registers of 32 bytes, counted as memory as well
MEM_LIMIT = 1 << 20
TAIL_LOG2 = -40                    # table-capacity abort probability at most 2^-40
# Mixed distinguished points: x ends a trail iff its low s1 bits are zero and F = (x >> s1) mod 2^W is below Tp;
# density theta = Tp / 2^(s1 + W) and L = 1 / theta.  The key is the kb bits above the window followed by the fb low bits of F.
CFG = {256: dict(s1=32, W=90), 40: dict(s1=12, W=0, Tp=1), 32: dict(s1=8, W=0, Tp=1), 22: dict(s1=4, W=4, Tp=12, U=2)}


def body_ops(U, s1):
    """Operations of one loop body (U batches): batches, grouped filter, loop control and one move (proof 3.3)."""
    group = U * (1 + (1 if s1 < 32 else 0)) + (U - 1) + 3     # U adds [and U ands if s1 < 32], U-1 ands, 1 and, compare, branch
    return U * PH + group + 3 + 1


def _plan(n, Tp, tmax):
    c = CFG[n]
    s1, W, U = c["s1"], c["W"], c.get("U", U_UNROLL)
    N, D = 1 << n, c["s1"] + c["W"]
    L = Fraction(1 << D, Tp)
    ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
    num, den = ureq + INFLIGHT * L + 1, CUTLOSS.denominator
    q = -(-(num * den * 1) // (den - CUTLOSS.numerator))
    q = -(-q.numerator // q.denominator) if isinstance(q, Fraction) else q
    b = -(-q // LANES)
    b = -(-b // U) * U                                        # whole groups
    sb = (1 << 48) if n == 256 else 4 * U_UNROLL
    cc = -(-KAPPA * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(64 - fb, n - D), L=L, N=N, U=U, Q=b * LANES, B=b, Sb=sb, c=cc,
                capr=cc + sb, tmax=tmax, e2max=2 * b * LANES // (1 << s1) + 64)


def code_bytes(n=256):
    return (body_ops(CFG[n].get("U", U_UNROLL), CFG[n]["s1"]) + RECOVERY_CODE + HANDLER_CODE + REPLAY_CODE) * INSTR_BYTES


def tail_log2(mean, k):
    """log2 of the Chernoff bound exp(-mean) * (e * mean / k)^k on P(count >= k) for a count that is binomial or Poisson, k > mean."""
    from math import log
    return (-mean + k * (1 + log(mean / k))) / log(2)


def plan(n):
    if n != 256:
        p = _plan(n, CFG[n]["Tp"], 0)
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    tmax = (MEM_LIMIT - code_bytes() - COUNTERS - REGFILE) // ENTRY
    best = None
    for Tp in range(1, 513):                                  # the largest Tp whose table-capacity tail is within 2^TAIL_LOG2
        p = _plan(256, Tp, tmax)
        if tail_log2(float(p["Q"] / p["L"]), tmax + 1) <= TAIL_LOG2:
            best = p
    return best


def ledger(n=256, spill=0, spill_body=0):
    """Operation budget in word operations (exact Fractions); units are operations / 638 (C of blake3-r3).
    spill / spill_body: loads and stores added per batch circuit / per loop body on a machine with a small register file (proof 3.1)."""
    p = plan(n)
    ph = PH + spill
    per_body = body_ops(p["U"], p["s1"]) + p["U"] * spill + spill_body
    main = Fraction(per_body, p["U"]) * p["B"]
    parts = dict(main=main,
                 slices=-(-p["B"] // p["Sb"]) * 100,
                 stage2=p["e2max"] * (STAGE2_OPS + p["U"] * ph + REPLAY_OPS),
                 events=p["tmax"] * (DP_EVENT_OPS + 3 * p["tmax"]),
                 recovery=p["capr"] * (ph + RECOVER_EXTRA) + 600,
                 init=2000)                                    # setup: 1 random word, 7 starts <= 287, counters <= 25, folded constants <= 336 (proof 3.3)
    return dict(parts=parts, total=sum(parts.values()), plan=p, per_body=per_body)


def loss(p):
    """The probability losses of proof Section 4 (floats): the terms, their sum and the lower bound on the success probability."""
    from math import exp, factorial, log
    N, Q, L = p["N"], p["Q"], p["L"]
    x = float(LAMBDA)
    trails = float(Q / L)
    f1 = float(p["c"] / Q)                                 # one cut trail, as a fraction of Q
    mu = trails * exp(-KAPPA)
    pk = [exp(-mu) * mu ** j / factorial(j) for j in range(3)]
    slope = 2 * x * exp(-x)                                # dP = slope * dU / U
    cut = sum(pk[j] * max(0.0, j * f1 - float(CUTLOSS)) * slope for j in (1, 2)) + (1 - sum(pk)) * (1 - exp(-x))
    infl = exp(-INFLIGHT) * sum(INFLIGHT ** j / factorial(j) for j in range(7))
    inside = float(Q * L / N)
    keys = 2.0 ** -(p["kb"] + log(p["Tp"], 2))
    t = dict(unfinished=infl, cut_deficit=cut, inside_trail=inside, key_false_match=p["tmax"] * (p["tmax"] - 1) / 2 * keys,
             table_capacity=2.0 ** tail_log2(trails, p["tmax"] + 1), recovery_no_pair=2.0 ** -100)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - exp(-x) - t["sum"]
    t["mean_cut_trails"], t["trails"], t["cut_one_trail"] = mu, trails, f1
    return t


# ---------------------------------------------------------------- 4 search and recovery
def feed(z, n):
    """Next inputs i8..i15 from the 8 digest words (n < 256 keeps the low n bits)."""
    out = []
    for i in range(8):
        lo = 32 * i
        if lo >= n:
            out.append(0)
        elif n - lo >= 32:
            out.append(z[i])
        else:
            out.append(z[i] & (REP * ((1 << (n - lo)) - 1)))
    return out


class Halt(Exception):
    pass


def is_dp(x, p):
    """Mixed distinguished point: low s1 bits zero and the window above them below Tp."""
    return x & ((1 << p["s1"]) - 1) == 0 and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]


def dp_key(x, p):
    """The kb bits above the window, then the fb low bits of the window value (which determine it): the end of a trail."""
    return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))


def pack_entry(key, t, length):
    """One table entry of ENTRY = 25 bytes: key 8 (64 bits), trail number 2 (16 bits), length 15 (120 bits)."""
    assert key < 1 << 64 and t < 1 << 16 and length < 1 << 120
    return key | (t << 64) | (length << 80)


def unpack_entry(e):
    return e & ((1 << 64) - 1), (e >> 64) & 0xFFFF, e >> 80


def recover(p, r, a, b):
    """a, b = (t, length) of two finished trails with the same end.  Returns (x, y), x != y, f(x) = f(y)."""
    n, mask = p["n"], p["N"] - 1
    if a[1] < b[1]:
        a, b = b, a                                    # a is the longer trail
    xs = [(r + a[0]) & mask, (r + b[0]) & mask]
    for _ in range(a[1] - b[1]):                       # only the longer trail moves
        xs[0] = lane_x(batch(*pack_x([xs[0]])), 0) & mask
    if xs[0] == xs[1]:
        return None
    for _ in range(b[1] + 1):
        z = batch(*pack_x(xs))
        ya, yb = lane_x(z, 0) & mask, lane_x(z, 1) & mask
        if ya == yb:
            return xs[0], xs[1]
        xs = [ya, yb]
    return None


def set_lane(z, l, x):
    out = list(z)
    for i in range(8):
        out[i] = (out[i] & ~(M32 << (PITCH * l))) | (((x >> (32 * i)) & M32) << (PITCH * l))
    return tuple(out)


def search(p, r, U=None):
    """One attempt with the fresh random word r: (pair or None, counters).  Raises Halt at a budget.
    A group is U batches run with only the grouped filter (one add and one and per batch).  If some batch of the group had a lane
    whose tested bits are zero, the group is replayed from its saved inputs, batch by batch, with the full bookkeeping.
    U = 1 is the per-batch search (every flagged batch is replayed at once)."""
    n, mask = p["n"], p["N"] - 1
    U = p["U"] if U is None else U
    bit32, s1mask, rep_ff = REP << 32, REP * ((1 << p["s1"]) - 1), REP * M32
    table, births, ts = {}, [0] * LANES, list(range(LANES))
    nxt = LANES
    cnt = dict(batches=0, stage2=0, finished=0, cut=0, replays=0)
    inp = pack_x([(r + t) & mask for t in ts])
    while cnt["batches"] < p["B"]:
        acc, zz = bit32, inp
        for _ in range(U):
            z = batch(*zz)
            acc &= (z[0] & s1mask) + rep_ff
            zz = feed(z, n)
        if acc & bit32 == bit32:                               # no lane of the group has its tested bits zero
            cnt["batches"] += U
            inp = zz
        else:
            cnt["replays"] += 1
            for _ in range(U):
                z = batch(*inp)
                cnt["batches"] += 1
                if ((z[0] & s1mask) + rep_ff) & bit32 != bit32:
                    cnt["stage2"] += 1
                    if cnt["stage2"] > p["e2max"]:
                        raise Halt("stage-2 budget")
                    for l in range(LANES):
                        x = lane_x(z, l) & mask
                        if is_dp(x, p):
                            key, length = dp_key(x, p), cnt["batches"] - births[l]
                            cnt["finished"] += 1
                            if key in table:
                                _, t0, l0 = unpack_entry(table[key])
                                res = recover(p, r, (t0, l0), (ts[l], length))
                                if res is None:
                                    raise Halt("recovery found no pair")
                                return res, cnt
                            if len(table) >= p["tmax"]:
                                raise Halt("table full")
                            table[key] = pack_entry(key, ts[l], length)
                            ts[l], nxt, births[l] = nxt, nxt + 1, cnt["batches"]
                            z = set_lane(z, l, (r + ts[l]) & mask)
                inp = feed(z, n)
        if cnt["batches"] % p["Sb"] == 0:
            for l in range(LANES):
                if cnt["batches"] - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    ts[l], nxt, births[l] = nxt, nxt + 1, cnt["batches"]
                    inp = set_lane(inp, l, (r + ts[l]) & mask)
    return None, cnt


