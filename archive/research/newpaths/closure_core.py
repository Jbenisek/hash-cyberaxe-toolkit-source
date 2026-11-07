"""For each possible 1-word core: the largest closure of core + 2 words; a 4-side split with a 1-word core needs
4 sides whose closures (each from core + its own 2 words) together cover all words."""
import itertools, sys
from gd_order import build
from gd_promote import macros_for
from closure_bound import closure

variant = sys.argv[1] if len(sys.argv) > 1 else "fixed"
eqs, const, vars_ = build(variant, "len64")
ev = [vs for _, vs in eqs]
mac = macros_for(eqs, set(const))
best_core = []
for core in vars_:
    base = closure(ev, mac, const, [core])
    rest = [v for v in vars_ if v not in base]
    sizes = sorted((len(closure(ev, mac, const, (core,) + p)) for p in itertools.combinations(rest, 2)), reverse=True)
    best_core.append((sizes[0], sum(sizes[:4]), core))
best_core.sort(reverse=True)
print(f"{variant}: best 1-word cores by largest core+2 closure (max single, sum of top 4 pairs, core):")
for r in best_core[:5]:
    print("  ", r)
print(f"a 4-side split needs the 4 side closures to cover {len(vars_)} words")
