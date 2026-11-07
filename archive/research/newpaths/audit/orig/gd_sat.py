"""Exact minimum guess basis for the solving-order problem of gd_order.py, by SAT.

known[v][t]: word v is known after t propagation layers.  known[v][0] <-> guessed or constant.
known[v][t+1] -> known[v][t] or (some equation containing v has every other word known at t).
All words known at layer T; at most k guesses (sequential counter).
Writes DIMACS for each k; run a solver on it; decode with --decode <cnf> <solver output>.
Usage: python gd_sat.py <fixed|outhalf> <len64|len55> <k> [T]
"""
import sys

from gd_order import build


TABLES = False


def table_macros(eqs, const):
    """Cycles that a 2^32 table solves because every parameter of the cycle is a family constant."""
    calls = {}
    for name, vs in eqs:
        if ":" in name:
            calls.setdefault(name.split(":")[0], {})[name.split(":")[1]] = vs
    out = []
    for call, e in calls.items():
        a, b, x = e["a1"][1], e["a1"][2], e["a1"][3]
        d, c, y = e["d1"][1], e["c1"][1], e["a2"][3]
        a1, d1, c1, b1 = e["a1"][0], e["d1"][0], e["c1"][0], e["b1"][0]
        a2, d2, c2, b2 = e["a2"][0], e["d2"][0], e["c2"][0], e["b2"][0]
        words = [x, a1, d1, c1, b1, a2, d2, c2, b2]
        if all(u in const for u in (a, b, c, d)):
            if y in const:                      # K0: one free word, any known word gives the call
                for w in words:
                    out.append(((w,), x))
            else:                               # K1..K3: y and a2 known give x
                out.append(((y, a2), x))
        if a2 in const and c2 in const:         # C0, C2: c known gives d1
            out.append(((c,), d1))
        if b2 in const and d2 in const:         # C1, C3: b known gives c1
            out.append(((b,), c1))
    return out


def encode(variant, length, k, T):
    eqs, const, vars_ = build(variant, length)
    macros = table_macros(eqs, const) if TABLES else []
    idx = {}
    clauses = []

    def new():
        idx["_n"] = idx.get("_n", 0) + 1
        return idx["_n"]

    g = {v: new() for v in vars_}
    K = [{v: new() for v in vars_} for _ in range(T + 1)]
    for v in vars_:
        clauses.append([-K[0][v], g[v]])
    occ = {v: [] for v in vars_}
    for name, vs in eqs:
        for v in vs:
            if v in occ:
                occ[v].append(vs)
    for t in range(T):
        for v in vars_:
            big = [-K[t + 1][v], K[t][v]]
            for vs in occ[v]:
                others = [u for u in vs if u != v and u not in const]
                if not others:
                    big.append(None)      # always derivable from constants
                    break
                s = new()
                big.append(s)
                for u in others:
                    clauses.append([-s, K[t][u]])
            for trig, tgt in macros:
                if tgt != v or None in big:
                    continue
                others = [u for u in trig if u not in const]
                if not others:
                    big.append(None)
                    continue
                s = new()
                big.append(s)
                for u in others:
                    clauses.append([-s, K[t][u]])
            if None not in big:
                clauses.append(big)
    for v in vars_:
        clauses.append([K[T][v]])
    # sequential counter: at most k of g true
    xs = [g[v] for v in vars_]
    n = len(xs)
    if k == 0:
        clauses.extend([[-x] for x in xs])
    else:
        S = [[new() for _ in range(k)] for _ in range(n)]
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
    return clauses, idx["_n"], g, vars_


def main():
    if sys.argv[1] == "--decode":
        variant, length, k, T, out = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
        _, _, g, vars_ = encode(variant, length, k, T)
        true = set()
        for line in open(out):
            if line.startswith("v "):
                true.update(int(x) for x in line[2:].split() if int(x) > 0)
        print("guessed:", [v for v in vars_ if g[v] in true])
        return
    global TABLES
    if "--tables" in sys.argv:
        TABLES = True
        sys.argv.remove("--tables")
    variant, length, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
    T = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    clauses, nv, _, _ = encode(variant, length, k, T)
    fn = f"gd_{variant}{'T' if TABLES else ''}_{length}_k{k}_T{T}.cnf"
    with open(fn, "w") as fh:
        fh.write(f"p cnf {nv} {len(clauses)}\n")
        for c in clauses:
            fh.write(" ".join(map(str, c)) + " 0\n")
    print(fn, nv, len(clauses))


if __name__ == "__main__":
    main()
