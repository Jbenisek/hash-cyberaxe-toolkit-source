"""Same query as lbsat6.py (relative window, promotions limited by slack S, cost <= T) as SMT-LIB2 with native
pseudo-Boolean constraints for the z3 binary (shape_any agent).
Usage: python lbz3.py <sys> <T> <S> <out.smt2> [letters]
"""
import sys
from lbsat4 import load


def main():
    fn, T, S, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    letters = sys.argv[5] if len(sys.argv) > 5 else None
    N, E, eqs, names = load(fn)
    wt = [1 if letters is None or nm[0] in letters else 0 for nm in names]
    occ = [[] for _ in range(N)]
    for e, vs in enumerate(eqs):
        for v in vs:
            occ[v].append(e)
    L = ["(set-option :produce-models true)", "(set-logic QF_UF)" if False else ""]
    decl = []
    for e in range(E):
        decl += [f"x{e}", f"c{e}", f"r{e}", f"ce{e}"]
    for v in range(N):
        decl += [f"y{v}", f"p{v}", f"cv{v}"]
    for d in decl:
        L.append(f"(declare-const {d} Bool)")
    A = L.append
    for v in range(N):
        A(f"(assert (not (and y{v} p{v})))")
        A(f"(assert (=> y{v} (or {' '.join(f'x{e}' for e in occ[v])} false)))")
    for e, vs in enumerate(eqs):
        u = " ".join(f"(or y{v} p{v})" for v in vs)
        A(f"(assert (= c{e} (and x{e} r{e} {u})))")
        A(f"(assert (= r{e} (or {' '.join(f'(not p{v})' for v in vs)})))")
        for v in vs:
            A(f"(assert (or p{v} ce{e} cv{v}))")
    for v in range(N):
        for e in occ[v]:
            for g in occ[v]:
                if e != g:
                    A(f"(assert (=> (and x{e} (not x{g})) (or y{v} p{v})))")
    # cost: sum y - sum c <= T   ->  sum y + sum (not c) <= T + E
    lits = [f"y{v}" for v in range(N)] + [f"(not c{e})" for e in range(E)]
    A(f"(assert ((_ at-most {T + E}) {' '.join(lits)}))")
    # slack: |P| + |cover| <= S + E
    lits = [f"p{v}" for v in range(N)] + [f"ce{e}" for e in range(E)] + [f"cv{v}" for v in range(N)]
    A(f"(assert ((_ at-most {S + E}) {' '.join(lits)}))")
    # window: 3 Z >= R and 3 Z <= 2 R - 1, Z = sum (x and r) over weighted, R = sum r over weighted
    W = [e for e in range(E) if wt[e]]
    zs = " ".join(f"(and x{e} r{e})" for e in W)
    rs = " ".join(f"r{e}" for e in W)
    # 3Z - R >= 0 : pbge with coefficients 3 on z terms and -1 on r terms is not allowed (negatives); use not r:
    # 3Z + sum(not r) >= |W|      and    2R - 3Z >= 1  ->  2 sum r + 3 sum (not z) >= 1 + 3|W|
    coeffs = " ".join(["3"] * len(W) + ["1"] * len(W))
    A(f"(assert ((_ pbge {len(W)} {coeffs}) {zs} {' '.join(f'(not r{e})' for e in W)}))")
    coeffs = " ".join(["2"] * len(W) + ["3"] * len(W))
    A(f"(assert ((_ pbge {1 + 3 * len(W)} {coeffs}) {rs} {' '.join(f'(not (and x{e} r{e}))' for e in W)}))")
    A("(check-sat)")
    A("(get-value (" + " ".join(f"x{e}" for e in range(E)) + " " + " ".join(f"p{v}" for v in range(N)) + "))")
    with open(out, "w") as fh:
        fh.write("\n".join(l for l in L if l) + "\n")
    print(out, len(L))


if __name__ == "__main__":
    main()
