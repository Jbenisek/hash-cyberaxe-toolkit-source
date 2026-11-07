"""Counting bound for a 4-side split: largest closure of any 2-word (and 1-word) guess set, plain and with tables."""
import itertools, sys
from gd_order import build
from gd_promote import macros_for

def closure(eqs_vars, macros, const, extra):
    known = set(const) | set(extra)
    changed = True
    while changed:
        changed = False
        for vs in eqs_vars:
            unk = [v for v in vs if v not in known]
            if len(unk) == 1:
                known.add(unk[0]); changed = True
        for trig, t in macros:
            if t not in known and all(w in known for w in trig):
                known.add(t); changed = True
    return known - set(const)

if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "fixed"
    eqs, const, vars_ = build(variant, "len64")
    ev = [vs for _, vs in eqs]
    for label, mac in (("plain", []), ("tables", macros_for(eqs, set(const)))):
        one = max(len(closure(ev, mac, const, [v])) for v in vars_)
        best, arg = 0, None
        for p in itertools.combinations(vars_, 2):
            n = len(closure(ev, mac, const, p))
            if n > best:
                best, arg = n, p
        print(f"{variant} {label}: {len(vars_)} words; max closure 1 guess = {one}; 2 guesses = {best} {arg}; "
              f"4 sides x 2 guesses cover at most {4*best} of {len(vars_)}")
