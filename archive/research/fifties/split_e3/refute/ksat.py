'''Exact word-level tests on the own model (wmodel.py), by SAT (kissat in WSL), over ALL guess sets (basis-free):
  min  : least guess-set size K whose propagation closure is every word; k = K - DOF.
  mitm : two-list meet in the middle. Fixed set A, side words P and Q; closure(A+P) and closure(A+Q) must together cover
         every core word (all k conditions are then side filters or matches).  |A|+|P|+|Q| = DOF+k, |P|,|Q| >= k.
         Per root it costs about 2^(32k+1)/N list entries with N <= 2^(32 min(|P|,|Q|)); this beats the bar only if such
         a cover exists for k = 1 (|P|,|Q| >= 1) or k = 2 (|P|,|Q| >= 2).
The model is first pruned to its core: a relation holding a word that appears nowhere else only defines that word
(an output computed after the solve) and is removed with it; DOF is unchanged.
usage: python ksat.py <counter> min <K>   |   python ksat.py <counter> mitm <k>'''
import sys, subprocess, os, itertools
from wmodel import build
def core(R):
    R = [set(r[1]) for r in R]
    while True:
        deg = {}
        for r in R:
            for w in r: deg[w] = deg.get(w, 0) + 1
        drop = [i for i, r in enumerate(R) if any(deg[w] == 1 for w in r) or not r]
        if not drop: return R
        R = [r for i, r in enumerate(R) if i not in set(drop)]
class CNF:
    def __init__(s): s.n = 0; s.cl = []
    def var(s): s.n += 1; return s.n
    def add(s, *c): s.cl.append(list(c))
    def atmost(s, xs, K):
        '''sequential counter: sum xs <= K'''
        if K >= len(xs): return
        if K == 0:
            for x in xs: s.add(-x)
            return
        r = [[s.var() for _ in range(K)] for _ in xs]
        for i, x in enumerate(xs):
            s.add(-x, r[i][0])
            if i > 0:
                for j in range(K): s.add(-r[i - 1][j], r[i][j])
                for j in range(1, K): s.add(-x, -r[i - 1][j - 1], r[i][j])
                s.add(-x, -r[i - 1][K - 1])
    def atleast(s, xs, K):
        if K <= 0: return
        s.atmost([-x for x in xs], len(xs) - K)
    def closure(s, R, W, init, T):
        '''kn[w][t]: w known at step t (only the soundness direction is needed); kn[w][0] -> init[w].'''
        kn = {w: [s.var() for _ in range(T + 1)] for w in W}
        for w in W: s.add(-kn[w][0], init[w])
        for t in range(T):
            for w in W:
                ds = []
                for r in R:
                    if w not in r: continue
                    d = s.var(); ds.append(d)
                    for u in r:
                        if u != w: s.add(-d, kn[u][t])
                s.add(-kn[w][t + 1], kn[w][t], *ds)
        return kn
    def solve(s, tag):
        fn = 'cnf_%s.cnf' % tag
        with open(fn, 'w', newline='\n') as f:
            f.write('p cnf %d %d\n' % (s.n, len(s.cl)))
            for c in s.cl: f.write(' '.join(map(str, c)) + ' 0\n')
        here = os.path.abspath('.').replace('\\', '/'); wsl = '/mnt/' + here[0].lower() + here[2:]
        out = subprocess.run(['wsl', '-e', 'bash', '-c', 'cd "%s" && kissat --time=1300 -q %s' % (wsl, fn)],
                             capture_output=True, text=True).stdout
        st = 'SAT' if '\ns SATISFIABLE' in '\n' + out else ('UNSAT' if 'UNSATISFIABLE' in out else 'UNKNOWN')
        model = set()
        for line in out.splitlines():
            if line.startswith('v '): model |= {int(x) for x in line[2:].split() if int(x) > 0}
        return st, model
def propagate(R, known):
    known = set(known); ch = True
    while ch:
        ch = False
        for r in R:
            u = [w for w in r if w not in known]
            if len(u) == 1: known.add(u[0]); ch = True
    return known
if __name__ == '__main__':
    counter, mode, k = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    R0, W0 = build(counter); DOF = len(W0) - len(R0)
    R = core(R0); W = sorted(set().union(*R))
    assert len(W) - len(R) == DOF
    T = len(W)                      # safe depth: every useful step adds a word
    print('counter %d: full %d words / %d rels, core %d words / %d rels, DOF %d, depth %d' % (counter, len(W0), len(R0), len(W), len(R), DOF, T))
    c = CNF()
    if mode == 'min':
        K = k; g = {w: c.var() for w in W}
        kn = c.closure(R, W, g, T)
        for w in W: c.add(kn[w][T])
        c.atmost([g[w] for w in W], K)
        st, mod = c.solve('c%d_min_%d' % (counter, K))
        print('min: guess set of size <= %d (k <= %d) closing every word: %s' % (K, K - DOF, st))
        if st == 'SAT':
            S = sorted(w for w in W if g[w] in mod)
            print('   guesses', S, ' propagate check:', propagate(R, S) >= set(W))
    else:
        K = DOF + k
        a = {w: c.var() for w in W}; p = {w: c.var() for w in W}; q = {w: c.var() for w in W}
        for w in W: c.add(-a[w], -p[w]); c.add(-a[w], -q[w]); c.add(-p[w], -q[w])
        i1 = {}; i2 = {}
        for w in W:
            i1[w] = c.var(); c.add(-i1[w], a[w], p[w]); i2[w] = c.var(); c.add(-i2[w], a[w], q[w])
        k1 = c.closure(R, W, i1, T); k2 = c.closure(R, W, i2, T)
        for w in W: c.add(k1[w][T], k2[w][T])
        c.atmost([a[w] for w in W] + [p[w] for w in W] + [q[w] for w in W], K)
        c.atleast([p[w] for w in W], k); c.atleast([q[w] for w in W], k)
        st, mod = c.solve('c%d_mitm_%d' % (counter, k))
        print('mitm k=%d: |A|+|P|+|Q| <= %d, |P|,|Q| >= %d, two closures cover the core: %s' % (k, K, k, st))
        if st == 'SAT':
            A = sorted(w for w in W if a[w] in mod); P = sorted(w for w in W if p[w] in mod); Q = sorted(w for w in W if q[w] in mod)
            c1 = propagate(R, A + P); c2 = propagate(R, A + Q)
            print('   A', A, 'P', P, 'Q', Q, ' cover check:', (c1 | c2) >= set(W))
