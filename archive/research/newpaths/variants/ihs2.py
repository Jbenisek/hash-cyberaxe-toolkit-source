"""Implicit hitting set with C closures (libgd.so).  Exact minimum guess set, or a proven lower bound.
usage: python3 ihs2.py <model> <kstart> <kmax> <seconds> <tag> [grow_per_iter]"""
import ctypes, os, random, subprocess, sys, time
mdl, kstart, kmax, secs, tag = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
G = int(sys.argv[6]) if len(sys.argv) > 6 else 12
here = os.path.dirname(os.path.abspath(__file__))
lib = ctypes.CDLL(os.path.join(here, "libgd.so"))
U = ctypes.c_ulonglong
lib.clos.argtypes = [U, U, ctypes.POINTER(U)]
lib.grow.argtypes = [U, U, U, ctypes.POINTER(U)]
n = lib.load(mdl.encode())
buf = (U * 2)()
M64 = (1 << 64) - 1
def clos(m):
    r = lib.clos(m & M64, m >> 64, buf); return r, buf[0] | (buf[1] << 64)
seedc = [0]
def grow(m):
    seedc[0] += 1
    lib.grow(m & M64, m >> 64, seedc[0], buf); return buf[0] | (buf[1] << 64)
_, BASE = clos(0)
cons = set()
for v in range(n):
    if not (BASE >> v) & 1:
        for _ in range(3):
            cons.add(grow(1 << v))
rng = random.Random(3)
free = [v for v in range(n) if not (BASE >> v) & 1]
for _ in range(2000):
    a, b = rng.sample(free, 2)
    ok, c = clos((1 << a) | (1 << b))
    if not ok:
        cons.add(grow((1 << a) | (1 << b)))
def hs(k):
    xs = list(range(1, n + 1)); nv = n; clauses = []
    for D in cons:
        clauses.append([xs[v] for v in range(n) if (D >> v) & 1])
    S = []
    for i in range(n):
        S.append(list(range(nv + 1, nv + k + 1))); nv += k
    clauses.append([-xs[0], S[0][0]])
    for j in range(1, k): clauses.append([-S[0][j]])
    for i in range(1, n):
        clauses.append([-xs[i], S[i][0]]); clauses.append([-S[i - 1][0], S[i][0]])
        for j in range(1, k):
            clauses.append([-xs[i], -S[i - 1][j - 1], S[i][j]]); clauses.append([-S[i - 1][j], S[i][j]])
        clauses.append([-xs[i], -S[i - 1][k - 1]])
    fn = os.path.join(here, f"ihs_{tag}.cnf")
    with open(fn, "w") as fh:
        fh.write(f"p cnf {nv} {len(clauses)}\n")
        for c in clauses: fh.write(" ".join(map(str, c)) + " 0\n")
    r = subprocess.run(["kissat", "-q", fn], capture_output=True, text=True)
    if r.returncode == 20: return None
    true = set()
    for line in r.stdout.split("\n"):
        if line.startswith("v "): true.update(int(x) for x in line[2:].split() if int(x) > 0)
    return [v for v in range(n) if (v + 1) in true]
t0 = time.time(); k = kstart; it = 0
log = open(os.path.join(here, f"res/ihs_{tag}.log"), "a")
print(f"start {mdl} n={n} seed constraints={len(cons)} grow/iter={G}", file=log, flush=True)
while k <= kmax and time.time() - t0 < secs:
    H = hs(k); it += 1
    if H is None:
        print(f"PROVEN: no guess set of size <= {k} (constraints {len(cons)}, iter {it}, {time.time()-t0:.0f}s)", file=log, flush=True)
        k += 1; continue
    m = sum(1 << v for v in H)
    ok, _ = clos(m)
    if ok:
        print(f"OPTIMUM k={len(H)} guesses {H} (constraints {len(cons)}, iter {it}, {time.time()-t0:.0f}s)", file=log, flush=True)
        break
    for _ in range(G): cons.add(grow(m))
    # also grow from H minus one element (often the binding constraints)
    for h in H:
        cons.add(grow(m & ~(1 << h)))
    if it % 100 == 0:
        print(f"  iter {it} k={k} constraints {len(cons)} {time.time()-t0:.0f}s", file=log, flush=True)
else:
    print(f"STOP at k={k} ({time.time()-t0:.0f}s, constraints {len(cons)}): lower bound k_min >= {k}", file=log, flush=True)
