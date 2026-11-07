def selftest():
    import random
    ok = True
    rnd = random.Random(3)
    st = step256()
    print("hash-consing hits", st.hits, "dead gates", st.dead, "(the machine generator keeps no node table: both must be 0)")
    ok &= st.hits == 0 and st.dead == 0
    print("n=256 step: gates", st.gates, st.by, "peak live", st.peak_live(), "q weight", bin(st.qint).count("1"))
    code, regs = allocate(st)
    print("allocation: registers used", regs, "moves 0 (output j in register j)")
    pl0 = [rnd.getrandbits(256) for _ in range(256)]
    good = run_allocated(st, code, pl0) == list(st.step(*pl0))
    print("allocated code on a register file equals the step:", good)
    ok &= good
    good, tot = True, 0                                   # the step against the scalar compression, full 256-bit g = f XOR q
    for _ in range(16):
        xs = [rnd.getrandbits(256) for _ in range(LANES)]
        out = lanes_of(list(st.step(*pack_lanes(xs, 256, st.pin))), 256, st.pin)
        good &= all(out[l] == f_scalar(xs[l], 256) ^ st.qint for l in range(LANES))
        tot += LANES
    print("%d lanes, step vs scalar compression: %s" % (tot, good))
    ok &= good
    good = True
    for _ in range(16):
        cur = [rnd.getrandbits(256) for _ in range(LANES)]
        pl = pack_lanes(cur, 256, st.pin)
        for _ in range(7):
            pl = list(st.step(*pl))
            cur = [f_scalar(x, 256) ^ st.qint for x in cur]
        good &= lanes_of(pl, 256, st.pin) == cur
    print("4,096 lanes chained for 7 steps vs scalar compression:", good)
    ok &= good
    e = Engine(N_T3)
    xs = [rnd.getrandbits(N_T3) for _ in range(LANES)]
    pl = pack_lanes(xs, N_T3, e.pin)
    for _ in range(5):
        pl = list(e.step(*pl))
        xs = [e.g_scalar(x) for x in xs]
    good = lanes_of(pl, N_T3, e.pin)[:LANES] == xs
    print("n=%d chain, 5 steps, 256 lanes:" % N_T3, good)
    ok &= good
    xs = [rnd.getrandbits(256) for _ in range(7)]
    good = packed_f(xs, 256, st.qwords) == [f_scalar(x, 256) ^ st.qint for x in xs]
    print("packed recovery circuit (%d ops, with the XORs of q) vs scalar:" % packed_circuit(st.qwords)[1], good)
    ok &= good
    rows = [rnd.getrandbits(256) for _ in range(256)]
    good = transpose(transpose(rows)) == rows and (transpose(rows)[5] >> 9) & 1 == (rows[9] >> 5) & 1
    print("transpose:", good)
    ok &= good
    good = True                                           # the table against a dictionary, small S with wraparound
    for S, kb in ((37, 12), (64, 9), (101, 20)):
        qf, ref = QF(S, kb), {}
        while qf.n < S - 1:
            k = rnd.getrandbits(kb)
            t0, at = qf.find(k)
            good &= t0 == ref.get(k)
            if t0 is None:
                ref[k] = qf.n
                qf.put(k, qf.n, at)
        good &= all(qf.find(k)[0] == v for k, v in ref.items())
    print("quotient-filter table vs dictionary:", good)
    ok &= good
    p = plan(N_T3)                                        # the recovery with checkpoints (D = 1 and D > 1) on trails with equal ends
    r, ends, pairs = rnd.getrandbits(N_T3), {}, 0
    for t in range(400):
        x, l = (r + t) % p["N"], 0
        while l < p["cr"]:
            x, l = e.f2([x])[0], l + 1
            if is_dp(x, p):
                if x in ends and pairs < 20:
                    a, b = recover(p, r, ends[x], t, e.f2), recover(p, r, ends[x], t, e.f2, 3)
                    good &= a == b and (a is None or (a[0] != a[1] and e.g_scalar(a[0]) == e.g_scalar(a[1])))
                    pairs += a is not None
                ends.setdefault(x, t)
                break
    print("recovery, checkpoints every step and every ceil(c_r / 3) steps agree on %d pairs:" % pairs, good)
    ok &= good and pairs > 0
    found = 0                                             # the search at n = 18 finds recoverable collisions
    for s in range(6):
        res, cnt = attempt(e, p, "selftest/%d" % s, "t")
        if res is not None:
            found += 1
            ok &= res[0] != res[1] and f_scalar(res[0], N_T3) == f_scalar(res[1], N_T3)
    print("search n=%d: %d of 6 attempts returned a verified pair" % (N_T3, found))
    ok &= found > 0
    print("selftest", ok)
    return ok


def choose_key(nb=4):
    """The offline choice of KEY (proof 3.7): coordinate descent from the zero key; word i = 0..7 in order, values v << (32 - nb),
    v = 0 .. 2^nb - 1 in order; a value is kept when the number of gates of the network drops; sweeps until one keeps nothing.
    Prints the key, the evaluations and their charge GEN_FACTOR * (primitive calls + nodes), summed."""
    def ev(k):
        g, out = trace(256, k)
        return len(live(g, out)), GEN_FACTOR * (g.calls + len(g.nodes))
    key = [0] * 8
    best, ops = ev(key)
    evals, imp = 1, True
    while imp:
        imp = False
        for i in range(8):
            for v in range(1 << nb):
                if v << (32 - nb) != key[i]:
                    k2 = key[:i] + [v << (32 - nb)] + key[i + 1:]
                    g, o = ev(k2)
                    evals, ops = evals + 1, ops + o
                    if g < best:
                        best, key, imp = g, k2, True
    print("key", ["%08x" % k for k in key], "gates", best, "evaluations", evals, "charge", ops)


def print_ledger(lg):
    from math import log2
    print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
    print("operations per batch (body)", lg["body"])
    for k, v in lg["parts"].items():
        print(k, v)
    print("N =", lg["total"])
    print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / UNIT) + 5e-6, log2(lg["total"] / UNIT)))


