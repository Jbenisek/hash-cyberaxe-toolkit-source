#!/usr/bin/env python3
"""e3sat.py [REPS]   (research/newpaths/untried/ctr_alg; research only)

GAPS.md section 2, row 3 ("ctr x alg"): does an off-the-shelf SAT solver solve the per-passing-step E3 systems of the
counter path (record X2) with less work than the E3-first DFS of counter_next/stack (e3solve.py, e3solve2.py)?

Systems (built with the stack code, imported read-only; no bytecode is written there):
  rec11  : the 120 passing outer steps of e3solve2.py's record run (seed 11; same draw order, so the same steps).
           Its first 20 steps are the MAIN sample (per-instance lines, timing repeated REPS times, CNF files kept).
  rec7   : the 150 passing outer steps of e3solve.py's record run (seed 7, after replaying the 300 plants' draws).
  rplant : 5 random real pairs, target = the pair's own differences (as e3solve.py (a)); solvable by construction.
  bplant : 7 outer steps that HAVE a solution for a beta* outcome (one per tau), made by gen_plant(): kissat solves E3
           with y (class member), q, w8 and h1 all free and 24/16/8/0 random q/w8 bits fixed; the point is re-checked
           forward and must pass the exact outer filter.  It is then solved as an ordinary per-step system (y, q, w8
           fixed, h1 unknown) by every config and both DFS's.  (bplant() below, the algebraic plant, was too slow:
           test_bplant.py, diag_plant.py.)
Each system: unknown h1 (32 bits), E3 on both messages (h1' = h1 ^ eta), constraints dg1 = G, de2 = eps, dg2 = tau.
Encodings: CNF (Tseitin, constants folded) for kissat and CaDiCaL; the same circuit with every XOR gate as an XOR clause
for CryptoMiniSat (XNF).  Every solver enumerates ALL solutions (blocking clause on h1, re-run until UNSAT); its work is
the sum over its runs.  Every model is re-checked forward with e3solve.e3; solution sets are compared with both DFS's.
Solver configs: kissat (--check=0: this Ubuntu build checks every derived clause by default, which only adds time),
kissat-nc (also --congruence=false), cadical (default), cms (default, XOR clauses).
Work measures per system (summed over the enumeration runs):
  LB   = literal occurrences of the formula(s) read + propagations; 1 word op each (a lower bound: every solver reads
         its formula, every propagation is at least one op; decisions, conflict analysis, learning, congruence closure,
         Gauss-Jordan and probing other than propagations are charged 0).
  TIME = child CPU time (getrusage) minus the median CPU time of the same config on a 1-clause formula, x 4.7e9
         cycles/s (Ryzen 9 7900X, /proc/cpuinfo 4699.9 MHz), 1 word op per cycle.  Includes parsing and set-up.
DFS work: e3solve.solve_step (simple) and e3solve2.joint (joint), with the op weights written in that code.
At most one solver process runs at a time (plus this driver).  Writes cnf/ (main sample and plants), systems.json (every
system, DFS counts, per-config counters; full solver statistics for the main sample); prints the summary.
"""
import json, os, random, re, resource, statistics, subprocess, sys, time
from math import log2
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
STACK = os.path.abspath(os.path.join(HERE, '..', '..', 'counter_next', 'stack'))
sys.path.insert(0, STACK)
import e3solve as S          # noqa: E402  (team code, read-only)
import e3solve2 as J         # noqa: E402

M, ETA, EPS, Y3, Y3B, DY3 = S.M, S.ETA, S.EPS, S.Y3, S.Y3B, S.DY3
ror, rol = S.ror, S.rol
TL = 300                     # seconds per solver run (kissat --time, cadical -t, cms --maxtime); runs take ms
CLOCK = 4.7e9
CNFDIR = os.path.join(HERE, 'cnf')
DH2 = ror(ETA ^ EPS, 8)      # XOR difference of h2 once (1) and (2) hold
TARGETS = [(S.G(t), EPS, t) for t in S.TAUS]


# ---------------------------------------------------------------- circuit -> CNF / XNF -------------------------------
def neg(b):
    return (not b) if isinstance(b, bool) else -b


class Enc:
    """bits are Python bools (constants) or nonzero int literals; constants are folded."""
    def __init__(self, xmode):
        self.n = 0; self.cls = []; self.xcl = []; self.xmode = xmode; self.unsat = False

    def new(self):
        self.n += 1
        return self.n

    def xor(self, bits):
        par = False; vs = {}
        for b in bits:
            if isinstance(b, bool):
                par ^= b; continue
            if b < 0:
                par ^= True
            v = abs(b)
            if v in vs: del vs[v]
            else: vs[v] = 1
        vs = list(vs)
        if not vs: return par
        if len(vs) == 1: return -vs[0] if par else vs[0]
        z = self.new()                       # z = XOR(vs) ^ par
        if self.xmode:
            self.xcl.append(([z] + vs, par))  # z ^ v1 ^ ... ^ vk == par
        else:
            for a in range(1 << len(vs)):
                p = (bin(a).count('1') & 1) ^ par
                cl = [(-v if a >> j & 1 else v) for j, v in enumerate(vs)]
                cl.append(z if p else -z)
                self.cls.append(cl)
        return z

    def and_(self, a, b):
        if isinstance(a, bool): return b if a else False
        if isinstance(b, bool): return a if b else False
        if a == b: return a
        if a == -b: return False
        z = self.new()
        self.cls += [[-z, a], [-z, b], [z, -a, -b]]
        return z

    def or_(self, a, b):
        return neg(self.and_(neg(a), neg(b)))

    def maj(self, a, b, c):
        cs = [x for x in (a, b, c) if isinstance(x, bool)]
        ls = [x for x in (a, b, c) if not isinstance(x, bool)]
        if len(cs) == 3: return sum(cs) >= 2
        if len(cs) == 2: return cs[0] if cs[0] == cs[1] else ls[0]
        if len(cs) == 1: return self.or_(*ls) if cs[0] else self.and_(*ls)
        a, b, c = ls
        if a == b or a == c: return a
        if b == c: return b
        if a == -b: return c
        if a == -c: return b
        if b == -c: return a
        m = self.new()
        self.cls += [[-a, -b, m], [-a, -c, m], [-b, -c, m], [a, b, -m], [a, c, -m], [b, c, -m]]
        return m

    def add(self, x, y):
        out = []; c = False
        for i in range(32):
            out.append(self.xor([x[i], y[i], c]))
            if i < 31: c = self.maj(x[i], y[i], c)
        return out

    def assert_bit(self, x, val):
        if isinstance(x, bool):
            if x != val: self.unsat = True
            return
        self.cls.append([x if val else -x])

    def assert_xor2(self, a, b, d):          # a ^ b == d
        if isinstance(a, bool): return self.assert_bit(b, a ^ d)
        if isinstance(b, bool): return self.assert_bit(a, b ^ d)
        if a == b or a == -b:
            if (a == -b) != d: self.unsat = True
            return
        self.cls += ([[a, b], [-a, -b]] if d else [[a, -b], [-a, b]])

    def body(self):
        """DIMACS body (no header), clause count, literal occurrences."""
        lines = [' '.join(map(str, c)) + ' 0' for c in self.cls]
        lits = sum(len(c) for c in self.cls)
        for vs, par in self.xcl:              # CMS: 'x a b c 0' means a ^ b ^ c == 1
            ls = list(vs)
            if not par: ls[0] = -ls[0]
            lines.append('x' + ' '.join(map(str, ls)) + ' 0'); lits += len(ls)
        if self.unsat:
            v = self.new(); lines += [f'{v} 0', f'{-v} 0']; lits += 2
        return '\n'.join(lines) + '\n', len(lines), lits


def cw(x): return [bool(x >> i & 1) for i in range(32)]
def xc(w, c): return [neg(b) if c >> i & 1 else b for i, b in enumerate(w)]
def rw(w, r): return [w[(j + r) % 32] for j in range(32)]          # ror by r


def build(y, q, w8, tgt, xmode):
    g, eps, tau = tgt
    enc = Enc(xmode)
    h1 = [enc.new() for _ in range(32)]       # variables 1..32 = h1 bits 0..31

    def msg(hw, a):                           # mirrors e3solve.e3(a, y, q, h1, w8)
        g1 = enc.add(cw(q), hw)
        f1 = rw(xc(g1, y), 12)
        e2 = enc.add(cw((a + y + w8) & M), f1)
        h2 = rw([enc.xor([u, v]) for u, v in zip(hw, e2)], 8)
        g2 = enc.add(g1, h2)
        return g1, e2, g2
    A = msg(h1, Y3)
    B = msg(xc(h1, ETA), Y3B)
    for i in range(32):
        enc.assert_xor2(A[0][i], B[0][i], bool(g >> i & 1))
        enc.assert_xor2(A[1][i], B[1][i], bool(eps >> i & 1))
        enc.assert_xor2(A[2][i], B[2][i], bool(tau >> i & 1))
    return enc


# ---------------------------------------------------------------- solvers --------------------------------------------
CONFIGS = {
    'kissat': ('cnf', lambda p: ['kissat', f'--time={TL}', '--check=0', '-s', p]),
    'kissat-nc': ('cnf', lambda p: ['kissat', f'--time={TL}', '--check=0', '--congruence=false', '-s', p]),
    'cadical': ('cnf', lambda p: ['cadical', '-t', str(TL), '--stats=1', p]),
    'cms': ('xnf', lambda p: ['cryptominisat5', '--maxtime', str(TL), '--verb', '1', p]),
}
STAT_RE = re.compile(r'^c\s+([A-Za-z][\w\- ()]*?)\s*:\s+(\d+(?:\.\d+)?)')


def child_cpu():
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


def run_solver(cfg, path):
    c0 = child_cpu(); t0 = time.perf_counter()
    r = subprocess.run(CONFIGS[cfg][1](path), capture_output=True, text=True)
    wall = time.perf_counter() - t0; cpu = child_cpu() - c0
    status, model, stats = 'NONE', {}, {}
    for line in r.stdout.splitlines():
        if line.startswith('s '):
            status = line[2:].strip()
        elif line.startswith('v '):
            for t in line[2:].split():
                v = int(t)
                if v: model[abs(v)] = v > 0
        else:
            m = STAT_RE.match(line)
            if m: stats[m.group(1).strip()] = float(m.group(2))     # last occurrence wins
    h1 = sum(1 << i for i in range(32) if model.get(i + 1)) if status == 'SATISFIABLE' else None
    return dict(status=status, h1=h1, wall=wall, cpu=cpu, rc=r.returncode,
                props=stats.get('propagations', 0.0), confl=stats.get('conflicts', 0.0),
                dec=stats.get('decisions', 0.0), stats={k: v for k, v in stats.items() if v})


def enum_all(cfg, body, n, m, lits):
    """all solutions by blocking clauses; returns (sorted solutions, runs, literal occurrences read)."""
    ext = CONFIGS[cfg][0]
    p = os.path.join(CNFDIR, f'_run_{cfg}.{ext}')
    blocks, runs, read = [], [], 0
    while True:
        with open(p, 'w') as f:
            f.write(f'p cnf {n} {m + len(blocks)}\n'); f.write(body)
            for h in blocks:
                f.write(' '.join(str(-(i + 1)) if h >> i & 1 else str(i + 1) for i in range(32)) + ' 0\n')
        read += lits + 32 * len(blocks)
        res = run_solver(cfg, p)
        runs.append(res)
        if res['status'] != 'SATISFIABLE' or len(blocks) >= 64:
            break
        blocks.append(res['h1'])
    os.remove(p)
    return sorted(blocks), runs, read


BASE = {}


def baselines(k=15):
    for cfg, (ext, _) in CONFIGS.items():
        p = os.path.join(CNFDIR, f'_trivial.{ext}')
        with open(p, 'w') as f:
            f.write('p cnf 1 1\n1 0\n')
        BASE[cfg] = statistics.median(run_solver(cfg, p)['cpu'] for _ in range(k))
        os.remove(p)


# ---------------------------------------------------------------- DFS on the same system -----------------------------
def full_ok(y, q, w8, h, tgt):
    A = S.e3(Y3, y, q, h, w8); B = S.e3(Y3B, y, q, h ^ ETA, w8)
    return (A[0] ^ B[0], A[2] ^ B[2], A[4] ^ B[4]) == tuple(tgt)


def dfs(y, q, w8, tgt):
    st = [0, 0, 0]
    sols = sorted(h for h, _ in S.solve_step(y, q, w8, [tgt], st))
    ops_s = st[0] * 6 + st[1] * 12 + st[2] * 40 + 32 * 8 * 4          # weights of e3solve.py
    nodes = [0]
    s12 = J.joint(y, q, (Y3 + y + w8) & M, tgt[0], tgt[1], nodes)
    solsj = sorted(h for h in s12 if full_ok(y, q, w8, h, tgt))
    ops_j = nodes[0] * 10 + 2 * 32 * 8 * 3 + len(s12) * 40              # weights of e3solve2.py
    return dict(sols=sols, sols_joint=solsj, s_nodes=st[0], s_f1=st[1], s_surv=st[2], ops_simple=ops_s,
                j_nodes=nodes[0], j_s12=len(s12), ops_joint=ops_j)


# ---------------------------------------------------------------- instances ------------------------------------------
def passing_steps(rng, steps):
    out, tried = [], 0
    while len(out) < steps:
        tried += 1
        y, q, w8 = S.member(rng), rng.getrandbits(32), rng.getrandbits(32)
        E = (Y3 + y + w8) & M
        ok = [S.solvable1(q, g) and S.solvable2(E, ror(g, 12), e) for g, e, t in TARGETS]
        if any(ok):
            out.append((y, q, w8, [k for k in range(7) if ok[k]]))
    return out, tried


def count_add_xor(x0, x1, dz, out):
    cnt = {(0, 0): 1}
    for i in range(32):
        a, b, d, o = x0 >> i & 1, x1 >> i & 1, dz >> i & 1, out >> i & 1
        nxt = {}
        for (c, cb), n in cnt.items():
            for v in (0, 1):
                t = S.trans(a, b, d, o, c, cb, v)
                if t is not None: nxt[t] = nxt.get(t, 0) + n
        cnt = nxt
    return sum(cnt.values())


ZM = ~EPS & 0x7FFFFFFF
def k_ok(K): return (K ^ EPS) & 1 == 0 and ((K >> 1) ^ K ^ (EPS >> 1)) & ZM == 0


def bplant(rng, k, budget_s=180.0):
    """outer step (y, q, w8) and h1 such that beta* outcome k holds; None if not found within budget_s."""
    g, eps, tau = TARGETS[k]
    t0 = time.perf_counter(); qh = ys = 0
    while time.perf_counter() - t0 < budget_s:
        q = rng.getrandbits(32)
        for _ in range(1 << 18):
            h1 = rng.getrandbits(32)
            if ((q + h1) & M) ^ ((q + (h1 ^ ETA)) & M) == g: break
        else:
            continue
        qh += 1
        g1 = (q + h1) & M; g1b = g1 ^ g
        if count_add_xor(g1, g1b, DH2, tau) == 0:
            continue
        s3e = [rol(h2, 8) ^ h1 for h2 in S.solutions_add_xor(g1, g1b, DH2, tau, [0, 0, 0])]
        for _ in range(1 << 17):
            y = S.member(rng); ys += 1
            f1 = ror(y ^ g1, 12); f1b = ror(y ^ g1b, 12)
            K = (DY3 + f1b - f1) & M
            if not k_ok(K):
                continue
            for e2 in s3e:
                if e2 ^ ((e2 + K) & M) == eps:
                    w8 = (((e2 - f1) & M) - Y3 - y) & M
                    if not full_ok(y, q, w8, h1, TARGETS[k]):
                        raise SystemExit('plant algebra error')
                    return y, q, w8, h1, qh, ys
    return None


def gen_plant(k, seed, nfix=24, tl=120):
    """beta* plant by SAT: y (class member), q, w8, h1 all free, E3 conditions for outcome k, nfix random bits of
    q/w8 fixed for diversity; kissat finds a point; returned values are re-checked forward (None if none found)."""
    g, eps, tau = TARGETS[k]
    enc = Enc(False)
    h1, y, q, w8 = ([enc.new() for _ in range(32)] for _ in range(4))     # vars 1-32, 33-64, 65-96, 97-128
    y4 = enc.add(y, cw(Y3))
    for i in range(32):
        if S.SUB_M >> i & 1:
            enc.assert_bit(y4[i], bool(S.SUB_V >> i & 1))

    def msg(hw, a):
        g1 = enc.add(q, hw)
        f1 = rw([enc.xor([u, v]) for u, v in zip(y, g1)], 12)
        e2 = enc.add(enc.add(enc.add(cw(a), y), w8), f1)
        h2 = rw([enc.xor([u, v]) for u, v in zip(hw, e2)], 8)
        return g1, e2, enc.add(g1, h2)
    A = msg(h1, Y3)
    B = msg(xc(h1, ETA), Y3B)
    for i in range(32):
        enc.assert_xor2(A[0][i], B[0][i], bool(g >> i & 1))
        enc.assert_xor2(A[1][i], B[1][i], bool(eps >> i & 1))
        enc.assert_xor2(A[2][i], B[2][i], bool(tau >> i & 1))
    rng = random.Random(seed)
    for v in rng.sample(q + w8, nfix):
        enc.cls.append([v if rng.random() < 0.5 else -v])
    body, m, _ = enc.body()
    p = os.path.join(CNFDIR, f'_gen_t{k}.cnf')
    with open(p, 'w') as f:
        f.write(f'p cnf {enc.n} {m}\n'); f.write(body)
    t0 = time.perf_counter()
    out = subprocess.run(['kissat', f'--time={tl}', '--check=0', f'--seed={seed}', '-q', p],
                         capture_output=True, text=True).stdout
    os.remove(p)
    model = {}
    for line in out.splitlines():
        if line.startswith('v '):
            for t in line[2:].split():
                v = int(t)
                if v: model[abs(v)] = v > 0
    if 's SATISFIABLE' not in out:
        return 'UNSAT' if 's UNSATISFIABLE' in out else 'UNKNOWN'
    word = lambda base: sum(1 << i for i in range(32) if model.get(base + i + 1))
    H, Yv, Qv, Wv = word(0), word(32), word(64), word(96)
    if not (full_ok(Yv, Qv, Wv, H, TARGETS[k]) and ((Yv + Y3) & S.SUB_M) == S.SUB_V):
        raise SystemExit('generator model fails the forward check')
    return Yv, Qv, Wv, H, time.perf_counter() - t0


# ---------------------------------------------------------------- ledger (stack_calc.py, V4 = X2) --------------------
R_SUB, P_SUB, LAM, MARGIN, UNIT, ONE = 67_698_688, 2 ** -9.8132, 0.5, 2.0, 430, 0.02


def T(c):
    m = 2 ** 32 * R_SUB * 2 ** -128
    return log2(LAM / (m / MARGIN) * c / UNIT) + ONE


def l2(x): return log2(x) if x > 0 else float('-inf')


def solve_system(sy, keep_file, reps):
    y, q, w8, tgt = sy['y'], sy['q'], sy['w8'], tuple(sy['tgt'])
    sy['dfs'] = dfs(y, q, w8, tgt)
    sy['sat'] = {}
    for xmode, ext in ((False, 'cnf'), (True, 'xnf')):
        enc = build(y, q, w8, tgt, xmode)
        body, m, lits = enc.body()
        sy[f'size_{ext}'] = (enc.n, m, lits)
        if keep_file:
            with open(os.path.join(CNFDIR, f"{sy['name']}.{ext}"), 'w') as f:
                f.write(f'p cnf {enc.n} {m}\n'); f.write(body)
        for cfg, (e, _) in CONFIGS.items():
            if e != ext: continue
            cpus = []
            for r in range(reps):
                sols, runs, read = enum_all(cfg, body, enc.n, m, lits)
                cpus.append(sum(max(0.0, x['cpu'] - BASE[cfg]) for x in runs))
                if r == 0:
                    first = (sols, runs, read)
            sols, runs, read = first
            props = sum(x['props'] for x in runs)
            sy['sat'][cfg] = dict(sols=sols, bad=[h for h in sols if not full_ok(y, q, w8, h, tgt)], runs=len(runs),
                                  status=[x['status'] for x in runs], props=props,
                                  confl=sum(x['confl'] for x in runs), dec=sum(x['dec'] for x in runs),
                                  read=read, lb=read + props, cpu=statistics.median(cpus),
                                  time_ops=statistics.median(cpus) * CLOCK,
                                  stats=[x['stats'] for x in runs] if keep_file else None)


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    os.makedirs(CNFDIR, exist_ok=True)
    print(f'e3sat.py: reps {reps} on the main sample and the plants; solver time limit {TL} s; clock {CLOCK:.2e}')
    print('X2 ledger check: T(435 + 2^-9.8132 * 2^18.51) = %.3f (stack_calc V4 70.990)' % T(435 + P_SUB * 2 ** 18.51))
    baselines()
    print('trivial-formula CPU baselines (s): ' + ', '.join(f'{c} {v:.4f}' for c, v in BASE.items()))
    systems = []
    t0 = time.perf_counter()
    st11, tr11 = passing_steps(random.Random(11), 120)
    rng7 = random.Random(7)
    for _ in range(300):                       # replay e3solve.py (a)'s draws
        S.member(rng7); rng7.getrandbits(32); rng7.getrandbits(32); rng7.getrandbits(32)
    st7, tr7 = passing_steps(rng7, 150)
    print(f'rec11: 120 passing in {tr11} tried (e3solve2_rerun.txt: 120 of 127617); rec7: 150 passing in {tr7} tried '
          f'(e3solve_out.txt: 150 of 148371); {time.perf_counter() - t0:.1f} s')
    for tag, sts in (('rec11', st11), ('rec7', st7)):
        for si, (y, q, w8, ks) in enumerate(sts):
            for k in ks:
                systems.append(dict(set=tag, step=si, k=k, y=y, q=q, w8=w8, tgt=list(TARGETS[k]), plant=None,
                                    main=(tag == 'rec11' and si < 20)))
    rng = random.Random(2026)
    for i in range(5):
        y, q, w8, h1 = S.member(rng), rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32)
        A = S.e3(Y3, y, q, h1, w8); B = S.e3(Y3B, y, q, h1 ^ ETA, w8)
        systems.append(dict(set='rplant', step=i, k=-1, y=y, q=q, w8=w8,
                            tgt=[A[0] ^ B[0], A[2] ^ B[2], A[4] ^ B[4]], plant=h1, main=True))
    for k in range(7):
        for seed, nfix in ((100 + k, 24), (200 + k, 16), (300 + k, 8), (400 + k, 0)):
            r = gen_plant(k, seed, nfix)
            if not isinstance(r, str):
                break
        if isinstance(r, str):
            print(f'bplant tau#{k}: generator {r} even with 0 fixed bits')
            continue
        y, q, w8, h1, sec = r
        ok = [S.solvable1(q, g) and S.solvable2((Y3 + y + w8) & M, ror(g, 12), e) for g, e, t in TARGETS]
        print(f'bplant tau#{k}: generated with {nfix} fixed q/w8 bits in {sec:.2f} s; passes the outer filter for '
              f'tau#{k}: {ok[k]} (viable outcomes {sum(ok)})')
        systems.append(dict(set='bplant', step=k, k=k, y=y, q=q, w8=w8, tgt=list(TARGETS[k]), plant=h1, main=True))

    for sid, sy in enumerate(systems):
        sy['id'] = sid
        sy['name'] = f"{sy['set']}_s{sy['step']:03d}_t{sy['k'] if sy['k'] >= 0 else 'x'}"
        solve_system(sy, sy['main'], reps if sy['main'] else 1)
        d = sy['dfs']
        agree = all(s['sols'] == d['sols'] == d['sols_joint'] for s in sy['sat'].values())
        bad = any(s['bad'] for s in sy['sat'].values())
        if sy['main']:
            dmin = min(d['ops_simple'], d['ops_joint'])
            lbmin = min(s['lb'] for s in sy['sat'].values()); tmin = min(s['time_ops'] for s in sy['sat'].values())
            line = (f"{sy['name']:18s} sols {len(d['sols'])}{'' if agree else ' DISAGREE'}{' BAD' if bad else ''}"
                    f" | DFS simple 2^{l2(d['ops_simple']):.2f} joint 2^{l2(d['ops_joint']):.2f}"
                    + ''.join(f" | {c} LB 2^{l2(s['lb']):.2f} T 2^{l2(s['time_ops']):.2f} cf {s['confl']:.0f}"
                              for c, s in sy['sat'].items())
                    + f" | best SAT/best DFS: LB 2^{l2(lbmin) - l2(dmin):+.2f}, TIME 2^{l2(tmin) - l2(dmin):+.2f}")
            if sy['plant'] is not None:
                line += (f" | planted h1 found: DFS {sy['plant'] in d['sols']}, all SAT "
                         f"{all(sy['plant'] in s['sols'] for s in sy['sat'].values())}")
            print(line, flush=True)
        elif not agree or bad:
            print(f"{sy['name']}: DISAGREE/BAD dfs {d['sols']} joint {d['sols_joint']} "
                  + ' '.join(f"{c} {s['sols']}" for c, s in sy['sat'].items()), flush=True)
    with open(os.path.join(HERE, 'systems.json'), 'w') as f:
        json.dump(systems, f)
    print(f'\nall {len(systems)} systems: solution sets agree (DFS simple = DFS joint = every SAT config): '
          f"{sum(all(s['sols'] == x['dfs']['sols'] == x['dfs']['sols_joint'] for s in x['sat'].values()) for x in systems)}"
          f"; unsound SAT models: {sum(bool(s['bad']) for x in systems for s in x['sat'].values())}"
          f"; real systems with an E3 solution: {sum(bool(x['dfs']['sols']) for x in systems if x['plant'] is None)}")

    # ------------------------------------------------ per passing step and ledger ----------------------------------
    def steps_of(tags):
        st = {}
        for x in systems:
            if x['set'] in tags:
                st.setdefault((x['set'], x['step']), []).append(x)
        return list(st.values())

    def summ(vals):
        v = sorted(vals)
        return (f"mean 2^{l2(sum(v) / len(v)):.2f} median 2^{l2(v[len(v) // 2]):.2f} "
                f"p90 2^{l2(v[int(len(v) * 0.9)]):.2f} max 2^{l2(v[-1]):.2f}"), sum(v) / len(v)
    base = T(435 + P_SUB * 2 ** 18.51)
    print(f'\nX2 ledger (V4: c = 400 + 35 + 2^-9.8132 * SOLVE): SOLVE 2^18.51 -> T {base:.3f}; SOLVE 0 -> T {T(435):.3f}'
          f' (ceiling of any solve gain {base - T(435):.3f} bit)')
    for tags in (('rec11',), ('rec7',), ('rec11', 'rec7')):
        sts = steps_of(tags)
        print(f'\n{"+".join(tags)}: {len(sts)} passing steps, {sum(len(s) for s in sts)} systems; per passing step:')
        rows = [('DFS simple', [sum(x['dfs']['ops_simple'] for x in s) for s in sts]),
                ('DFS joint', [sum(x['dfs']['ops_joint'] for x in s) for s in sts])]
        for c in CONFIGS:
            rows.append((f'{c} LB', [sum(x['sat'][c]['lb'] for x in s) for s in sts]))
            rows.append((f'{c} TIME', [sum(x['sat'][c]['time_ops'] for x in s) for s in sts]))
        for name, vals in rows:
            txt, mean = summ(vals)
            t = T(435 + P_SUB * mean)
            print(f'  {name:15s} {txt}  -> T {t:.3f} ({base - t:+.3f} bit vs 70.990)')
        for c in CONFIGS:
            cf = [sum(x['sat'][c]['confl'] for x in s) for s in sts]
            pr = [sum(x['sat'][c]['props'] for x in s) for s in sts]
            print(f'  {c:9s} conflicts mean {sum(cf) / len(cf):,.1f} max {max(cf):,.0f}; propagations mean '
                  f'{sum(pr) / len(pr):,.0f}; zero-conflict steps {sum(1 for v in cf if v == 0)}')


if __name__ == '__main__':
    main()
