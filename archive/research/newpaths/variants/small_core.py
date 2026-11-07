"""Largest number of checks inside the closure of any set of <= 3 guessed words (class representatives).
A core Z with dim(cl Z) = |Z| - cZ; the split cost bound in README needs cZ >= |Z| - 1 with |Z| = 2 or 3."""
import sys, itertools
from export_model import model
from gd_var import closure
half, mode, L, t, kmax = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
eqs, const, vars_, macros = model(half, mode, L, t)
base = closure(eqs, const, macros)
seen, reps = {}, []
for v in vars_:
    if v in base:
        continue
    key = frozenset(closure(eqs, set(const) | {v}, macros))
    if key not in seen:
        seen[key] = v; reps.append(v)
def dim(S):
    return len(S - const) - sum(1 for _, vs in eqs if all(x in S for x in vs))
best = {}
for r in range(1, kmax + 1):
    for T in itertools.combinations(reps, r):
        c = r - dim(closure(eqs, set(const) | set(T), macros))
        if c > best.get(r, (-1,))[0]:
            best[r] = (c, T)
print(half, mode, L, f"t{t}", "max checks inside closure of r guesses:", {r: best[r][0] for r in best}, "example:", best[kmax][1])
