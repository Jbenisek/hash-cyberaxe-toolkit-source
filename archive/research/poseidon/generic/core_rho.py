# ================================================================ 2 the target hash (Orchard Poseidon, ConstantLength<2>, 8 full + 56 partial rounds)
CAPACITY = 1 << 65
FULL_FIRST, TOTAL = 4, 64          # rounds 0-3 full, 4-59 partial (56 of them), 60-63 full


def digest(m0, m1):
    """Digest of the Orchard hash of the two canonical field elements (m0, m1): initial state [m0, m1, 2^65], 64 rounds, output state[0]."""
    a, b, c = m0, m1, CAPACITY
    for i in range(TOTAL):
        k = ROUND_CONSTANTS[i]
        a = (a + k[0]) % P
        b = (b + k[1]) % P
        c = (c + k[2]) % P
        a2 = a * a % P
        a = a2 * a2 % P * a % P
        if i < FULL_FIRST or i >= TOTAL - FULL_FIRST:
            b2 = b * b % P
            b = b2 * b2 % P * b % P
            c2 = c * c % P
            c = c2 * c2 % P * c % P
        a, b, c = ((MDS[0][0] * a + MDS[0][1] * b + MDS[0][2] * c) % P,
                   (MDS[1][0] * a + MDS[1][1] * b + MDS[1][2] * c) % P,
                   (MDS[2][0] * a + MDS[2][1] * b + MDS[2][2] * c) % P)
    return a


def enc(x):
    """Canonical 32-byte little-endian encoding (x < P)."""
    assert 0 <= x < P
    return x.to_bytes(32, "little")


# ================================================================ 3 the search: one trail, distinguished points, one table, recovery
def search(F, is_dp, x0, steps, mcap, gmax):
    """Single-trail collision search on the map F: x_0 = x0, x_i = F(x_{i-1}).  Every value x_i, i >= 1, with is_dp(x_i) is stored with its index.
    Halts (failure) after `steps` evaluations, when more than `mcap` distinguished points would be stored, or when the recovery needs a gap
    longer than gmax.  When a distinguished value repeats (x_b = x_a, a < b) the trail is periodic from a with period L = b - a; the recovery
    finds the least i with x_i = x_{i+L} and returns the pair (x_{i-1}, x_{i+L-1}) with x_{i-1} != x_{i+L-1} and F equal on both.
    Returns (pair or None, status, evaluations)."""
    ev = 0
    pts = [(0, x0)]                       # stored points in increasing index order; pts[0] is the start
    first = {}                            # distinguished value -> its position in pts
    x, i = x0, 0
    k = None
    while i < steps:
        x = F(x)
        i += 1
        ev += 1
        if is_dp(x):
            k = first.get(x)
            if k is not None:
                break
            if len(pts) > mcap:
                return None, "table", ev
            first[x] = len(pts)
            pts.append((i, x))
    if k is None:
        return None, "steps", ev
    a = pts[k][0]
    L = i - a                             # x_i = x_a with i = b
    s, A = pts[k - 1]                     # last stored point before a (index s < mu <= a, or the start)
    q = s + L
    lo, hi = 0, len(pts) - 1              # nearest stored point at or before q (q < b), then walk to x_q
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if pts[mid][0] <= q:
            lo = mid
        else:
            hi = mid - 1
    idx, B = pts[lo]
    if q - idx > gmax:
        return None, "gap", ev
    for _ in range(q - idx):
        B = F(B)
        ev += 1
    if A == B:
        return None, "start-on-cycle", ev
    for _ in range(gmax):                 # lockstep: the first index where the two walkers meet
        nA, nB = F(A), F(B)
        ev += 2
        if nA == nB:
            return (A, B), "found", ev
        A, B = nA, nB
    return None, "gap", ev


# ================================================================ 4 the claim's parameters and ledger (plan)
THETA_NUM, THETA_DEN_BITS = 27554, 128   # a value x is a distinguished point iff (x mod 2^128) < 27554: density theta = 27554 / 2^128
MCAP = 1 << 14                           # table capacity in distinguished points
C_UNIT = 1392                            # C(56) = 216 + 21*56
W_STEP = 7                               # other operations per trail step (section 5 of proof.md)
W_REC = 8                                # other operations per evaluation in the recovery
KD, H = 8, 18                            # detection window d = KD/theta, gap cap gmax = H/theta
OTHER_FIXED = 10 ** 8                    # bound on all table, setup and bookkeeping operations (proof.md section 5)


def plan():
    theta = THETA_NUM / 2.0 ** THETA_DEN_BITS
    d = KD / theta
    gmax = H / theta
    n = 0.994 * sqrt(P)
    for _ in range(60):
        eps = exp(-KD) + n * d / P + (n + d) * theta * exp(-H) + exp(-H) + exp(-100.0)
        n = sqrt(2 * P * (-log(0.61 - n / P - eps)))
    n = ceil(n / 2.0 ** 100) * 2.0 ** 100
    steps = n + d
    T = steps * (1 + W_STEP / C_UNIT) + 3 * gmax * (1 + W_REC / C_UNIT) + OTHER_FIXED / C_UNIT
    mean = steps * theta
    # Chernoff upper tail for the number of stored points: P(X >= MCAP) <= exp(-mu) * (e*mu/MCAP)^MCAP, in logs
    lchern = -mean + MCAP * (1 + log(mean / MCAP))
    return {"theta": theta, "theta_log2": log2(theta), "n": n, "d": d, "gmax": gmax, "eps_total": eps, "steps": steps,
            "T_units": T, "time_log2": log2(T), "mean_stored": mean, "ln_P_table_overflow": lchern, "n_log2": log2(n),
            "success_lower_bound": 1 - exp(-n * (n + 1) / (2 * P)) - n / P - eps}


# ================================================================ 5 organizer experiments (reduced width) and command line
NB = 14                                  # walk width of experiment rho-n14: the low 14 bits of the real 56-round digest of (v, 0)
_cache = {}


def F_n(v):
    r = _cache.get(v)
    if r is None:
        r = _cache[v] = digest(v, 0) & ((1 << NB) - 1)
    return r


def is_dp_n(x):
    return x < (1 << (NB - 4))           # density 1/16


def run_rho(seed):
    x0 = int(seed, 16) % (1 << NB)
    pair, status, ev = search(F_n, is_dp_n, x0, 256, 64, 160)
    if pair is None:
        return None, None, {"status": status, "evals": ev}
    a, b = pair
    assert a != b and F_n(a) == F_n(b)
    return enc(a) + bytes(32), enc(b) + bytes(32), {"status": status, "evals": ev}


def run_proj(seed):
    """Full-width walk g(x) = digest(x, 0) on field elements: 64 points of the real map from a seed start; a pair when the low 10 bits of two digests agree."""
    x = int(seed, 16) >> 2               # a 254-bit start, below P
    seen = {}
    for j in range(64):
        y = digest(x, 0)
        key = y & 1023
        if key in seen and seen[key] != x:
            return enc(seen[key]) + bytes(32), enc(x) + bytes(32), {"status": "pair", "j": j}
        seen.setdefault(key, x)
        x = y
    return None, None, {"status": "none"}


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--plan":
            print(json.dumps(plan(), indent=1))
        elif sys.argv[1] == "--selftest":
            ok = 0
            for t in range(40):
                ma, mb, ob = run_rho(hashlib.sha256(b"t%d" % t).hexdigest())
                if ma is not None:
                    ok += 1
            print("rho-n14 pairs:", ok, "of 40")
        return
    req = json.load(sys.stdin)
    run = run_rho if req["experiment_id"] == "rho-n14" else run_proj
    out = []
    for tr in req["trials"]:
        ma, mb, ob = run(tr["seed"])
        out.append({"trial": tr["trial"], "message_a_hex": None if ma is None else ma.hex(),
                    "message_b_hex": None if mb is None else mb.hex(), "observations": ob})
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": out}))


if __name__ == "__main__":
    main()
