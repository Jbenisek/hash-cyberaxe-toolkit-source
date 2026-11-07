"""verify.py - runs the emitted program (emit_rest.build) in the interpreter and compares it with frontline.py:
  solver   steps 2 and 3 through the entry stubs on random, planted and mutated banks: the roots in order, the meter's debit,
           the live words restored, the certified root, and the executed instructions of every block against its charge
  context  the 39 context lines (and S2, w5, w12) against co_full
  routine  the rebuild, step CT, the messages A and B and the two compressions against step_ct and compress2
usage: verify.py NRAND NPLANT SEED NCTX NROUT"""
import json, random, sys, time
import frontline as F
import emit_b3z7 as X
E = X
Machine = X.Machine

CREDIT0 = 1 << 60
ENVELOPES = (0x04, 0x01, 0x18, 0x52)
ALLOWED = sorted({m for e in ENVELOPES for m in range(1, 128) if m & ~e == 0})
NAMES = ("Y9", "Y4", "omega", "e1", "C2_a1", "C2_b1", "C2_c1", "C2_d1", "Y1", "Y12", "w5", "w12", "K0_d1")
M = F.M
COVALL = set()


def base_mem():
    mem = {}
    for base, arr in ((E.FORCED, F.FORCED), (E.DUAL, F.DUAL), (E.SELECTED, F.SELECTED)):
        for k, v in enumerate(arr):
            mem[base + k] = v
    return mem


def norm(bk):
    bk = dict(bk)
    bk["Y4"] = (bk["e1"] - F.Y3) & M
    return bk


def mkbank(rnd):
    ow = [rnd.getrandbits(32) for _ in range(7)]
    e1, y = F.member(rnd.randrange(1 << 19))
    v = F.rebuild(ow, y, e1)
    return norm({n: v[n] for n in NAMES})


def planted(rnd, tau):
    r = F.plant(tau, F.Rng(rnd.getrandbits(32).to_bytes(4, "little")))
    if r is None:
        return None
    bk, h = r
    ow = [rnd.getrandbits(32) for _ in range(7)]
    e1, y = F.member(rnd.randrange(1 << 19))
    v = F.rebuild(ow, y, e1)
    full = {n: v[n] for n in NAMES}
    full.update(bk)
    return norm(full), h


def mutate(rnd, bk):
    bk = dict(bk)
    for _ in range(rnd.randrange(1, 4)):
        bk[rnd.choice(("Y9", "omega", "C2_c1", "C2_b1", "Y1", "Y12", "w12", "e1"))] ^= 1 << rnd.randrange(32)
    return norm(bk)


def pack_lane(rnd, L, val):
    w = 0
    for i in range(7):
        w |= (val if i == L else rnd.getrandbits(32)) << 36 * i
        w |= rnd.getrandbits(4) << (36 * i + 32) if i != L else 0
    return w


class Ctx:
    def __init__(self, tag):
        self.tag = tag
        self.cov = set()
        self.st = {}

    def add(self, k, v=1):
        self.st[k] = self.st.get(k, 0) + v


def run_solver(code, labels, probes, mem, bk, T, rnd, cov, L=None):
    L = rnd.randrange(7) if L is None else L
    for n in ("w5", "w12", "K0_d1"):
        mem[E.BK[n]] = bk[n]
    m = Machine(code, mem)
    m.cov = cov
    live0 = [rnd.getrandbits(32) for _ in range(E.NLIVE)]
    m.r[:E.NLIVE] = live0
    m.r[0], m.r[1], m.r[2] = pack_lane(rnd, L, bk["Y9"]), pack_lane(rnd, L, bk["Y1"]), pack_lane(rnd, L, bk["Y12"])
    m.r[3], m.r[4], m.r[5], m.r[6], m.r[7], m.r[8] = (bk["e1"], bk["omega"], bk["C2_a1"], bk["C2_b1"], bk["C2_c1"],
                                                       bk["C2_d1"])
    live0 = list(m.r[:E.NLIVE])
    m.r[62], m.r[61], m.r[63] = T, E.a_of_T(T), CREDIT0
    got = []
    pr = {labels[l]: (lambda mm, tau=tau, n=n: got.append((mm.r[n], tau))) for l, (tau, n) in probes.items()}
    res = m.run(labels["ENTRY%d" % L], pr)
    live_ok = res == "ret" and m.r[:E.NLIVE] == live0
    return res, got, CREDIT0 - m.r[63], m, live_ok


def ref_case(bk, T):
    rows = F.rows_of(T)
    cnt, notes = [0] * 8, []
    roots = F.solve(bk, rows, True, cnt, notes)
    found = None
    for h, tau in roots:
        okc, c, t = F.predicate(bk, h, tau)
        if okc:
            found = (h, tau, c, t)
            break
    return roots, E.a_of_T(T) + cnt[7], notes, cnt, found


def check_solver(built, args):
    nrand, nplant, seed = args
    rnd = random.Random(seed)
    code, labels, probes, g = built
    mem = base_mem()
    cov = set()
    st = dict(cases=0, identical=0, different=0, roots=0, leaves=0, notes=0, over_budget=0, found=0, kind={})
    bad = []
    cases = [("rand", mkbank(rnd), rnd.choice(ALLOWED)) for _ in range(nrand)]
    for _ in range(nplant):
        tau = rnd.choice(F.S_ROWS)
        r = planted(rnd, tau)
        if r is None:
            continue
        bk, h = r
        extra = [mm for mm in ALLOWED if mm & (1 << F.TAUS.index(tau))]
        cases.append(("plant", bk, rnd.choice(extra)))
        for _ in range(3):
            cases.append(("mut", mutate(rnd, bk), rnd.choice(extra)))
    worst = {}
    for kind, bk, T in cases:
        res, got, debit, m, live_ok = run_solver(code, labels, probes, mem, bk, T, rnd, cov)
        roots, units, notes, cnt, found = ref_case(bk, T)
        st["cases"] += 1
        st["leaves"] += cnt[6]
        st["roots"] += len(roots)
        st["notes"] += bool(notes)
        st["kind"][kind] = st["kind"].get(kind, 0) + 1
        if res == 1:
            st["found"] += 1
            same = found is not None and got and got[-1] == (found[0], found[1]) and m.r[60] == found[2]
        else:
            same = res == "ret" and live_ok and got == roots and debit == units and found is None
        # executed instructions of every block against its charge (Section 11)
        bt = m.bytag
        fam = F.families(F.rows_of(T))
        nr = len(F.rows_of(T))
        lim = dict(forced=F.U_FORCED * cnt[0] + F.U_SELECTED * cnt[1] + F.U_G15 * cnt[2], free=F.U_FREE * cnt[4],
                   leaf=F.U_LEAF * cnt[6], root=F.U_ROOT * len(roots), found=10 ** 9, context=0)
        over = [k for k, v in bt.items() if k in lim and v > lim[k]]
        if sum(v for k, v in bt.items() if k in ("glob", "setup", "desc")) > E.a_of_T(T):
            over.append("A(T)")
        if m.count > units and res != 1:
            over.append("total")
        for k, v in bt.items():
            worst[k] = max(worst.get(k, 0), v)
        if over:
            st["over_budget"] += 1
            bad.append(("OVER", kind, T, over, dict(bt), units))
        if same:
            st["identical"] += 1
        else:
            st["different"] += 1
            if len(bad) < 8:
                bad.append((kind, T, res, got[:2], roots[:2], debit, units, found, notes))
    st["code_instructions_covered"] = len(cov)
    st["code_instructions_total"] = len(code)
    st["worst_executed_by_block_in_one_call"] = worst
    return st, bad, cov


def check_context(code, labels, n, rnd):
    ok = bad = 0
    names = [nm for nm in X.CTX if nm in F.DEF]
    for _ in range(n):
        ow = [rnd.getrandbits(32) for _ in range(7)]
        mem = {X.FRESH: sum(w << 32 * k for k, w in enumerate(ow))}
        m = Machine(code, mem)
        m.cov = COVALL
        r = m.run(labels["CONTEXT"])
        v = F.co_full(*ow, 0, F.FLAGS)
        good = r == "ret" and all(mem[X.CTX[nm]] == v[F.nm(nm)] for nm in CTXN) and all(
            mem[E.BK["OW%d" % k]] == ow[k] for k in range(7))
        ok += good
        bad += not good
    return dict(cases=n, identical=ok, different=bad, stored_names=len(CTXN), instructions=None)


CTXN = []


def check_routine(code, labels, g, n, rnd):
    ok = bad = eq_ok = 0
    mem = {}
    for _ in range(n):
        ow = [rnd.getrandbits(32) for _ in range(7)]
        e1, y = F.member(rnd.randrange(1 << 19))
        c1 = rnd.getrandbits(32)
        v = F.rebuild(ow, y, e1)
        u = F.step_ct(v, c1)
        ca, cb = F.compress2(u["A"], u["t"], F.FLAGS)[1], F.compress2(u["B"], u["t"], F.FLAGS)[1]
        wa = list(__import__("struct").unpack("<16I", u["A"] + bytes(64 - len(u["A"]))))
        wb = list(__import__("struct").unpack("<16I", u["B"] + bytes(64 - len(u["B"]))))
        mem.clear()
        mem[E.BK["Y4"]] = y
        for k in range(7):
            mem[E.BK["OW%d" % k]] = ow[k]
        m = Machine(code, mem)
        m.cov = COVALL
        m.r[60] = c1
        regs = {}
        # force the equal branch on every 4th case (the compare is the only code that differs)
        eqcase = _ % 4 == 3

        def at_cmp(mm):
            ra, rb = g.cmpregs
            regs["ca"], regs["cb"] = [mm.r[i] for i in ra], [mm.r[i] for i in rb]
            if eqcase:
                for i, j in zip(ra, rb):
                    mm.r[j] = mm.r[i]
        res = m.run(labels["FOUND"], {labels["FINALCMP"]: at_cmp})
        good = (regs["ca"] == ca and regs["cb"] == cb and [mem[X.OUT + k] for k in range(16)] == wa
                and [mem[X.OUT + 16 + k] for k in range(16)] == wb and res == (2 if eqcase else (3 if ca != cb else 2)))
        ok += good
        bad += not good
    return dict(cases=n, identical=ok, different=bad)


def solve_z(c, d, s, tau):
    """z with test_c(c, z, tau) and a = d ^ rol(z, 8) meeting test_a(a, s, tau); depth-first over the bits of z."""
    K, c2 = F.ror(tau, 8), (c + F.DY11) & M
    tgt = ((tau - F.BETA + 8 + 2 * s) & M) >> 1
    sys.setrecursionlimit(10000)

    def go(i, z, cu, cv):
        if i == 32:
            return z
        for zi in (0, 1):
            j = (i + 8) % 32
            if tau >> j & 1 and (d >> j & 1) ^ zi != tgt >> j & 1:
                continue
            ci, c2i, ki = c >> i & 1, c2 >> i & 1, K >> i & 1
            ui, vi = ci ^ zi ^ cu, c2i ^ zi ^ ki ^ cv
            if ui ^ vi != F.EPS >> i & 1:
                continue
            r = go(i + 1, z | zi << i, F.maj(ci, zi, cu), F.maj(c2i, zi ^ ki, cv))
            if r is not None:
                return r
        return None
    return go(0, 0, 0, 0)


def make_ok_bank(rnd):
    """a planted bank whose root passes the certificate (Lemma RC): choose Y1, w12, Y12, w5 from the root."""
    while True:
        tau = rnd.choice(F.S_ROWS)
        r = planted(rnd, tau)
        if r is None:
            continue
        bk, h = r
        y14 = F.rol(h, 16) ^ bk["e1"]
        y6 = F.ror(((y14 + bk["C2_c1"]) & M) ^ bk["C2_b1"], 7)
        for _ in range(40):
            c = F.QSTAR_VALUE | rnd.getrandbits(32) & ~F.QSTAR_MASK & M
            d = (c - F.Y11) & M
            b = F.ror(y6 ^ c, 12)
            s = b & F.BETA
            z = solve_z(c, d, s, tau)
            if z is None:
                continue
            a = d ^ F.rol(z, 8)
            a1 = rnd.getrandbits(32)
            bk = dict(bk)
            bk["Y12"] = a1 ^ F.rol(d, 16)
            bk["Y1"] = rnd.getrandbits(32)
            bk["w12"] = (a1 - y6 - bk["Y1"]) & M
            bk["w5"] = (a - a1 - b) & M
            ok, cc, t = F.predicate(bk, h, tau)
            if ok:
                return bk, h, tau, cc
        continue


def check_found(code, labels, probes, g, n, rnd):
    mem = base_mem()
    good = bad = 0
    for _ in range(n):
        bk, h, tau, cc = make_ok_bank(rnd)
        ow = [rnd.getrandbits(32) for _ in range(7)]
        for k in range(7):
            mem[E.BK["OW%d" % k]] = ow[k]
        T = 1 << F.TAUS.index(tau)
        T = rnd.choice([mm for mm in ALLOWED if mm & T])
        res, got, debit, m, live_ok = run_solver(code, labels, probes, mem, bk, T, rnd, COVALL)
        roots, units, notes, cnt, found = ref_case(bk, T)
        v = F.rebuild(ow, bk["Y4"], bk["e1"])
        u = F.step_ct(v, cc)
        wa = list(__import__("struct").unpack("<16I", u["A"] + bytes(64 - len(u["A"]))))
        ca, cb = F.compress2(u["A"], u["t"], F.FLAGS)[1], F.compress2(u["B"], u["t"], F.FLAGS)[1]
        same = (found is not None and found[2] == cc and res == (2 if ca == cb else 3) and m.r[60] == cc
                and [mem[X.OUT + k] for k in range(16)] == wa)
        good += bool(same)
        bad += not same
    return dict(cases=n, identical=good, different=bad)


def check_walk(built, path):
    """the real solver calls of the declared program's own walk (frontline.walk), recorded by cap_walk.py"""
    code, labels, probes, g = built
    calls = json.load(open(path))
    mem = base_mem()
    rnd = random.Random(99)
    good = bad = roots = 0
    for ow, y, e1, T, A, bk in calls:
        bk = {k: int(v) for k, v in bk.items()}
        assert bk["Y4"] == (bk["e1"] - F.Y3) & M and A == E.a_of_T(T)
        res, got, debit, m, live_ok = run_solver(code, labels, probes, mem, bk, T, rnd, None)
        r, units, notes, cnt, found = ref_case(bk, T)
        roots += len(r)
        same = res == "ret" and live_ok and got == r and debit == units and found is None and m.count <= units
        good += same
        bad += not same
    return dict(cases=len(calls), identical=good, different=bad, roots=roots)


def main():
    nr, npl, seed, nctx, nrout, nfound = (int(a) for a in sys.argv[1:7])
    walkfile = sys.argv[7] if len(sys.argv) > 7 else None
    t0 = time.time()
    built = X.build()
    code, labels, probes, g = built
    st, bad, cov = check_solver(built, (nr, npl, seed))
    rnd = random.Random(seed + 1)
    CTXN[:] = [nm for nm in X.CTX if nm in F.DEF and nm in X.CONTEXT_NAMES]
    out = dict(walk_calls=check_walk(built, walkfile) if walkfile else None, solver=st, found_path=check_found(code, labels, probes, g, nfound, rnd),
               context=check_context(code, labels, nctx, rnd), routine=check_routine(code, labels, g, nrout, rnd),
               instructions=len(code), registers_peak=g.peak, seconds=round(time.time() - t0, 1))
    from collections import Counter
    out["instructions_by_block"] = dict(Counter(c[4] for c in code))
    cov |= COVALL
    out["covered_by_all_tests"] = len(cov)
    print(json.dumps(out))
    for b in bad[:8]:
        print("BAD", b)
    cov |= COVALL
    out["code_instructions_covered_by_all_tests"] = len(cov)
    json.dump(sorted(set(range(len(code))) - cov), open("uncovered.json", "w"))


if __name__ == "__main__":
    main()
