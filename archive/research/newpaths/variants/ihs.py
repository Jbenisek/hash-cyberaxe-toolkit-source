"""Exact minimum guess set by implicit hitting sets (runs in WSL; kissat for the hitting-set step).
A set S of guesses determines everything iff it is contained in no proper closed set, i.e. iff it hits the complement
of every maximal proper closed set.  Loop: minimum hitting set H of the complements collected so far (kissat, at most
k by a sequential counter); if cl(H) = ALL then k is optimal; else grow cl(H) to a maximal proper closed set (random
order, several times) and add the complements.
usage: python3 ihs.py <model.mdl> <kstart> <kmax> <seconds> <tag>"""
import os
import random
import subprocess
import sys
import time

mdl, kstart, kmax, secs, tag = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
here = os.path.dirname(os.path.abspath(__file__))
lines = open(mdl).read().split("\n")
n, R = map(int, lines[0].split())
eqm, mac = [], []
occ = [[] for _ in range(n)]
for i in range(R):
    p = list(map(int, lines[1 + i].split()))
    t, vs = p[0], p[2:]
    m = 0
    for v in vs:
        m |= 1 << v
    if t == 0:
        eqm.append(m)
    else:
        trig = 0
        for v in vs[:-1]:
            trig |= 1 << v
        mac.append((trig, 1 << vs[-1]))
ALL = (1 << n) - 1


def cl(K):
    while True:
        old = K
        for m in eqm:
            u = m & ~K
            if u and not (u & (u - 1)):
                K |= u
        for trig, tgt in mac:
            if not (trig & ~K):
                K |= tgt
        if K == old:
            return K


BASE = cl(sum(1 << i for i, m in enumerate([]) ) | 0)
for m in eqm:
    if not (m & (m - 1)):
        BASE |= m
BASE = cl(BASE)
rng = random.Random(7)


def grow(C):
    outs = [v for v in range(n) if not (C >> v) & 1]
    rng.shuffle(outs)
    for v in outs:
        if (C >> v) & 1:
            continue
        C2 = cl(C | (1 << v))
        if C2 != ALL:
            C = C2
    return C


cons = set()


def add_from(C, tries=3):
    for _ in range(tries):
        M = grow(C)
        cons.add(ALL & ~M)


def hs(k):
    """Minimum-size question: is there a hitting set of size <= k?  Returns list of vars or None."""
    xs = list(range(1, n + 1))
    cl_ = [[xs[v] for v in range(n) if (D >> v) & 1] for D in cons]
    nv = n
    S = []
    clauses = list(cl_)
    for i in range(n):
        S.append(list(range(nv + 1, nv + k + 1)))
        nv += k
    clauses.append([-xs[0], S[0][0]])
    for j in range(1, k):
        clauses.append([-S[0][j]])
    for i in range(1, n):
        clauses.append([-xs[i], S[i][0]])
        clauses.append([-S[i - 1][0], S[i][0]])
        for j in range(1, k):
            clauses.append([-xs[i], -S[i - 1][j - 1], S[i][j]])
            clauses.append([-S[i - 1][j], S[i][j]])
        clauses.append([-xs[i], -S[i - 1][k - 1]])
    fn = os.path.join(here, f"ihs_{tag}.cnf")
    with open(fn, "w") as fh:
        fh.write(f"p cnf {nv} {len(clauses)}\n")
        for c in clauses:
            fh.write(" ".join(map(str, c)) + " 0\n")
    r = subprocess.run(["kissat", "-q", fn], capture_output=True, text=True)
    if r.returncode == 20:
        return None
    true = set()
    for line in r.stdout.split("\n"):
        if line.startswith("v "):
            true.update(int(x) for x in line[2:].split() if int(x) > 0)
    return [v for v in range(n) if (v + 1) in true]


t0 = time.time()
# seeds
for v in range(n):
    if not (BASE >> v) & 1:
        add_from(cl(BASE | (1 << v)), 1)
k = kstart
it = 0
log = open(os.path.join(here, f"res/ihs_{tag}.log"), "a")
print(f"start {mdl} n={n} seeds={len(cons)}", file=log, flush=True)
while k <= kmax and time.time() - t0 < secs:
    H = hs(k)
    it += 1
    if H is None:
        print(f"k={k}: no hitting set of size <= {k} (constraints {len(cons)}, iter {it}, {time.time()-t0:.0f}s)"
              f" -> minimum > {k}", file=log, flush=True)
        k += 1
        continue
    C = cl(BASE | sum(1 << v for v in H))
    if C == ALL:
        print(f"OPTIMUM k={len(H)} guesses {H} (constraints {len(cons)}, iter {it}, {time.time()-t0:.0f}s)",
              file=log, flush=True)
        break
    add_from(C, 3)
    # also try local improvements: random subsets of H extended
    if it % 50 == 0:
        print(f"  iter {it} k={k} constraints {len(cons)} {time.time()-t0:.0f}s", file=log, flush=True)
else:
    print(f"stopped at k={k} after {time.time()-t0:.0f}s, constraints {len(cons)}", file=log, flush=True)
