import sys, itertools, random
from export_model import model
from gd_var import closure
mdl, solfile, half, mode, L, t, nsol = sys.argv[1:8]
eqs, const, vars_, macros = model(half, mode, int(L), int(t))
sols = [list(map(int, l.split()[1:])) for l in open(solfile) if l.startswith("SOL")]
random.seed(1)
pick = random.sample(sols, min(int(nsol), len(sols)))
mx = {}
for sol in pick:
    g = [vars_[i] for i in sol]
    for r in range(len(g)):
        for T in itertools.combinations(g, r):
            s = len(closure(eqs, set(const) | set(T), macros) - const)
            mx[r] = max(mx.get(r, 0), s)
print(f"{len(pick)} sampled solutions of {len(sols)}: max closure size (of {len(vars_)} words) by subset size:", mx)
