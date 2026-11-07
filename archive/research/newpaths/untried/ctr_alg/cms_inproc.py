#!/usr/bin/env python3
"""cms_inproc.py [LIMIT]   (research/newpaths/untried/ctr_alg; research only)

CryptoMiniSat 5.11 IN-PROCESS through its C API (the installed libcryptominisat5.so via ctypes; nothing installed or
compiled): the cost of the solve call alone, with no process start and no parsing.  time.perf_counter_ns() is read
around one C call (ctypes adds about 1 us per call, included).  One thread.  Cycles = ns x 4.7 (Ryzen 9 7900X).
(A) fresh solver per system: new solver, clauses and XOR clauses of the XNF added (not timed), cmsat_solve timed, plus
    the blocking re-solves of the enumeration (each timed); solver freed.
(B) ONE incremental template for all systems: y, q, w8, G, eps, tau are variables (the E3 circuit is built once);
    each system is cmsat_solve_with_assumptions with 192 assumption literals (its constants); learned clauses carry
    over between systems; blocking clauses of a plant are guarded by a per-system activation literal.
Systems: systems.json (rec11, rec7, plants) in file order, up to LIMIT.  Answers are checked against the DFS's.
"""
import ctypes, json, os, statistics, sys, time
from math import log2
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e3sat as X  # noqa: E402

LIB = ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libcryptominisat5.so.5.11')


class LBool(ctypes.Structure):
    _fields_ = [('x', ctypes.c_uint8)]          # 0 = true, 1 = false, 2 = undef


class SliceLBool(ctypes.Structure):
    _fields_ = [('vals', ctypes.POINTER(LBool)), ('num_vals', ctypes.c_size_t)]


VP, U32P = ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)
LIB.cmsat_new.restype = VP
LIB.cmsat_free.argtypes = [VP]
LIB.cmsat_set_num_threads.argtypes = [VP, ctypes.c_uint]
LIB.cmsat_new_vars.argtypes = [VP, ctypes.c_size_t]
LIB.cmsat_add_clause.argtypes = [VP, U32P, ctypes.c_size_t]; LIB.cmsat_add_clause.restype = ctypes.c_bool
LIB.cmsat_add_xor_clause.argtypes = [VP, U32P, ctypes.c_size_t, ctypes.c_bool]
LIB.cmsat_add_xor_clause.restype = ctypes.c_bool
LIB.cmsat_solve.argtypes = [VP]; LIB.cmsat_solve.restype = LBool
LIB.cmsat_solve_with_assumptions.argtypes = [VP, U32P, ctypes.c_size_t]
LIB.cmsat_solve_with_assumptions.restype = LBool
LIB.cmsat_get_model.argtypes = [VP]; LIB.cmsat_get_model.restype = SliceLBool


def lit(d):                                     # DIMACS literal -> CMS c_Lit (0-based var, sign bit)
    return ((abs(d) - 1) << 1) | (d < 0)


def arr(xs):
    return (ctypes.c_uint32 * len(xs))(*xs)


class Solver:
    def __init__(self, n):
        self.s = LIB.cmsat_new(); LIB.cmsat_set_num_threads(self.s, 1); self.n = 0; self.grow(n)

    def grow(self, n):
        if n > self.n:
            LIB.cmsat_new_vars(self.s, n - self.n); self.n = n

    def clause(self, c):
        LIB.cmsat_add_clause(self.s, arr([lit(x) for x in c]), len(c))

    def xor(self, vs, par):
        LIB.cmsat_add_xor_clause(self.s, arr([v - 1 for v in vs]), len(vs), bool(par))

    def load(self, enc):
        self.grow(enc.n)
        for c in enc.cls: self.clause(c)
        for vs, par in enc.xcl: self.xor(vs, par)

    def solve(self, assumptions=()):
        a = arr([lit(x) for x in assumptions]) if assumptions else None
        t0 = time.perf_counter_ns()
        r = (LIB.cmsat_solve_with_assumptions(self.s, a, len(assumptions)) if assumptions
             else LIB.cmsat_solve(self.s)).x
        return r, time.perf_counter_ns() - t0

    def h1(self):
        m = LIB.cmsat_get_model(self.s)
        return sum(1 << i for i in range(32) if m.vals[i].x == 0)

    def free(self):
        LIB.cmsat_free(self.s)


def block(h, act=None):
    c = [-(i + 1) if h >> i & 1 else i + 1 for i in range(32)]
    return c + ([-act] if act else [])


def template():
    enc = X.Enc(True)
    h1, y, q, w8, G, E, Tt = ([enc.new() for _ in range(32)] for _ in range(7))   # vars 1..224

    def msg(hw, a):
        g1 = enc.add(q, hw)
        f1 = X.rw([enc.xor([u, v]) for u, v in zip(y, g1)], 12)
        e2 = enc.add(enc.add(enc.add(X.cw(a), y), w8), f1)
        h2 = X.rw([enc.xor([u, v]) for u, v in zip(hw, e2)], 8)
        return g1, e2, enc.add(g1, h2)
    A = msg(h1, X.Y3)
    B = msg(X.xc(h1, X.ETA), X.Y3B)
    for i in range(32):
        for k, w in ((0, G), (1, E), (2, Tt)):
            enc.assert_bit(enc.xor([A[k][i], B[k][i], w[i]]), False)
    return enc, (y, q, w8, G, E, Tt)


def l2(x): return log2(x) if x > 0 else float('-inf')


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9
    systems = json.load(open(os.path.join(HERE, 'systems.json')))[:limit]
    # (A) fresh solver per system
    fa, bad_a = [], 0
    for sy in systems:
        enc = X.build(sy['y'], sy['q'], sy['w8'], tuple(sy['tgt']), True)
        sv = Solver(enc.n); sv.load(enc)
        tot, sols = 0, []
        while True:
            r, ns = sv.solve(); tot += ns
            if r != 0: break
            h = sv.h1(); sols.append(h); sv.clause(block(h))
        sv.free()
        bad_a += sorted(sols) != sy['dfs']['sols'] or r != 1
        fa.append(tot)
    # (B) one incremental template
    enc, words = template()
    sv = Solver(enc.n); sv.load(enc)
    nxt = enc.n
    fb, bad_b = [], 0
    for sy in systems:
        vals = (sy['y'], sy['q'], sy['w8']) + tuple(sy['tgt'])
        assum = [(w[i] if v >> i & 1 else -w[i]) for w, v in zip(words, vals) for i in range(32)]
        nxt += 1; act = nxt; sv.grow(act)
        tot, sols = 0, []
        while True:
            r, ns = sv.solve(assum + [act]); tot += ns
            if r != 0: break
            h = sv.h1(); sols.append(h); sv.clause(block(h, act))
        sv.clause([-act])
        bad_b += sorted(sols) != sy['dfs']['sols'] or r != 1
        fb.append(tot)
    sv.free()
    json.dump(dict(names=[s['name'] for s in systems], fresh_ns=fa, incr_ns=fb),
              open(os.path.join(HERE, 'cms_inproc.json'), 'w'))
    print(f'systems {len(systems)}; answer mismatches vs DFS: fresh {bad_a}, incremental {bad_b}; template '
          f'{enc.n} vars, {len(enc.cls)} clauses, {len(enc.xcl)} XOR clauses')
    for tag in ('rec11', 'rec7'):
        idx = [i for i, s in enumerate(systems) if s['set'] == tag]
        if not idx: continue
        steps = {}
        for i in idx:
            steps.setdefault(systems[i]['step'], []).append(i)
        for name, v in (('fresh', fa), ('incremental', fb)):
            per = sorted(sum(v[i] for i in ii) * 4.7 for ii in steps.values())
            print(f'  {tag} {name:11s}: per passing step cycles mean 2^{l2(sum(per) / len(per)):.2f} median '
                  f'2^{l2(per[len(per) // 2]):.2f} max 2^{l2(per[-1]):.2f} ({len(per)} steps)')
    half = len(fb) // 2
    print(f'  incremental per system, first half median {statistics.median(fb[:half]) / 1e3:.1f} us, second half '
          f'{statistics.median(fb[half:]) / 1e3:.1f} us; fresh median {statistics.median(fa) / 1e3:.1f} us')
    pl = [i for i, s in enumerate(systems) if s['plant'] is not None]
    if pl:
        print(f'  plants: fresh median {statistics.median([fa[i] for i in pl]) / 1e3:.1f} us, incremental median '
              f'{statistics.median([fb[i] for i in pl]) / 1e3:.1f} us')


if __name__ == '__main__':
    main()
