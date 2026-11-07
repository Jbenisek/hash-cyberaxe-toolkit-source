import sys, itertools
from export_model import model
from gd_var import closure
mdl, solfile, half, mode, L, t = sys.argv[1:7]
eqs, const, vars_, macros = model(half, mode, int(L), int(t))
names = open(mdl + ".vars").read().split()
assert names == vars_
sols = [list(map(int, l.split()[1:])) for l in open(solfile) if l.startswith("SOL")]
def dim(S):
    return len(S - const) - sum(1 for _, vs in eqs if all(v in S for v in vs))
for sol in sols[:int(sys.argv[7]) if len(sys.argv) > 7 else 3]:
    g = [vars_[i] for i in sol]
    full = closure(eqs, set(const) | set(g), macros)
    print("guesses:", g, "closure all:", len(full - const) == len(vars_), "dim", dim(full))
    prof = {}
    for r in range(len(g) + 1):
        for T in itertools.combinations(g, r):
            cl = closure(eqs, set(const) | set(T), macros)
            c = len(T) - dim(cl)
            prof.setdefault(r, {}).setdefault(c, 0)
            prof[r][c] += 1
    print(" subset size -> {checks inside closure: count}:", prof)
