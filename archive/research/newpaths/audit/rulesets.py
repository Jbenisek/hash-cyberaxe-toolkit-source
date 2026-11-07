"""Rule sets for the exhaustive search (bf.c) and the SAT re-encoding (gd_sat_audit.py).
  plain : one-unknown propagation only (gd_order)
  orig  : plain + gd_sat.table_macros (2^32 tables, family-constant parameters)
  gen   : plain + all single-z 2^32 rules (rules.py)                    -- shown to add nothing over orig
  pair  : gen + 2^64-table rules: one per-instance parameter p (memory is free, 2^64 preprocessing is below 2^88):
          for unknown z and parameter p, A = plain closure(const + {z, p}); every w in A that depends on z
          (w not in closure(const + {p})) gives rule {p, w} -> z, and every equation with >= 2 words in A,
          >= 1 of them depending on z, and the rest outside A gives rule {p} + rest -> z.
Writes rules_<variant>_<length>_<set>.txt: line 1 'nvars neqs nrules', then var names, eqs, rules (indices).
"""
import sys

sys.dont_write_bytecode = True
HERE = __file__.rsplit("\\", 1)[0]
sys.path.insert(0, HERE + "\\orig")
from gd_order import build  # noqa: E402
from gd_sat import table_macros  # noqa: E402
from rules import gen_rules, nc_eqs, closure  # noqa: E402


def closure_r(ncq, rules, known):
    known = set(known)
    ch = True
    while ch:
        ch = False
        for _, vs in ncq:
            u = [v for v in vs if v not in known]
            if len(u) == 1:
                known.add(u[0])
                ch = True
        for t, g in rules:
            if g not in known and all(x in known for x in t):
                known.add(g)
                ch = True
    return known


def pair_rules(eqs, const, vars_, base):
    ncq = nc_eqs(eqs, const)
    out = []
    single = {v: closure(ncq, {v}) for v in vars_}
    for z in vars_:
        for p in vars_:
            if p == z or z in single[p]:
                continue
            A = closure(ncq, {z, p})
            dep = A - single[p]          # words of A that depend on z
            for w in sorted(dep - {z}):
                out.append(((p, w), z))
            for n, vs in ncq:
                ina = [v for v in vs if v in A]
                rest = [v for v in vs if v not in A]
                if len(ina) >= 2 and rest and any(v in dep for v in ina):
                    out.append((tuple(sorted(set(rest) | {p})), z))
    # drop rules already implied by base rules + plain propagation
    seen, keep = set(), []
    for t, g in out:
        key = (frozenset(t), g)
        if key in seen:
            continue
        seen.add(key)
        if g not in closure_r(ncq, base, set(t)):
            keep.append((t, g))
    return keep


def get(variant, length, rset):
    eqs, const, vars_ = build(variant, length)
    ncq = nc_eqs(eqs, const)
    rules = []
    if rset in ("orig", "gen", "pair"):
        rules = [(tuple(u for u in t if u not in const), g) for t, g in table_macros(eqs, const) if g not in t]
    if rset in ("gen", "pair"):
        rules += [(t, g) for t, g, _ in gen_rules(eqs, const, vars_)]
    if rset == "pair":
        rules += pair_rules(eqs, const, vars_, rules)
    return eqs, const, vars_, ncq, rules


def write(variant, length, rset):
    eqs, const, vars_, ncq, rules = get(variant, length, rset)
    ix = {v: i for i, v in enumerate(vars_)}
    fn = HERE + f"\\rules_{variant}_{length}_{rset}.txt"
    with open(fn, "w") as fh:
        fh.write(f"{len(vars_)} {len(ncq)} {len(rules)}\n")
        fh.write(" ".join(vars_) + "\n")
        for _, vs in ncq:
            fh.write(" ".join(str(ix[v]) for v in vs) + "\n")
        for t, g in rules:
            fh.write(f"{ix[g]} " + " ".join(str(ix[v]) for v in t) + "\n")
    return fn, len(rules)


def main():
    variant = sys.argv[1]
    length = sys.argv[2] if len(sys.argv) > 2 else "len64"
    sets = sys.argv[3:] or ["plain", "orig", "gen", "pair"]
    eqs, const, vars_, ncq, orig = get(variant, length, "orig")
    gen = [(t, g) for t, g, _ in gen_rules(eqs, const, vars_)]
    notimpl = [(t, g) for t, g in gen if g not in closure_r(ncq, orig, set(t))]
    print(f"{variant} {length}: gen rules not implied by orig+plain: {len(notimpl)} {notimpl[:5]}")
    for s in sets:
        fn, n = write(variant, length, s)
        print(f"  {s}: {n} rules -> {fn.rsplit(chr(92), 1)[1]}")


if __name__ == "__main__":
    main()
