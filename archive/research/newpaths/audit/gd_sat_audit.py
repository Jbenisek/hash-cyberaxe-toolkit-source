"""Copy of gd_sat.encode (same clauses, same sequential counter) taking its derivation rules from rulesets.py,
so the SAT model can be run with rule set plain / orig (== gd_sat --tables) / gen / pair.  No bug was found in
gd_sat.py; this file exists to cross-check the rule semantics against bf.c and to run the 2^64-table relaxation.
Usage: python gd_sat_audit.py <variant> <set> <k> <T> [--func]          -> audit_<variant>_<set>[F]_k<k>_T<T>.cnf
       python gd_sat_audit.py --decode <variant> <set> <k> <T> <solver output>   (decodes and re-checks the cover)
"""
import sys

sys.dont_write_bytecode = True
HERE = __file__.rsplit("\\", 1)[0]
sys.path.insert(0, HERE + "\\orig")
from rulesets import get, closure_r  # noqa: E402


FUNC = False   # --func: add the converse clauses so K is a function of the guesses (canonical parallel closure):
#               g -> K0, K[t] -> K[t+1], (all other words of a source known at t) -> K[t+1].  Same solutions in g.


def encode(variant, rset, k, T, length="len64"):
    eqs, const, vars_, ncq, rules = get(variant, length, rset)
    n_ = [0]

    def new():
        n_[0] += 1
        return n_[0]

    clauses = []
    g = {v: new() for v in vars_}
    K = [{v: new() for v in vars_} for _ in range(T + 1)]
    for v in vars_:
        clauses.append([-K[0][v], g[v]])
    occ = {v: [] for v in vars_}
    for _, vs in ncq:
        for v in vs:
            occ[v].append(vs)
    byt = {v: [] for v in vars_}
    for t, tg in rules:
        byt[tg].append(t)
    for t in range(T):
        for v in vars_:
            big = [-K[t + 1][v], K[t][v]]
            free = False
            for vs in occ[v] + byt[v]:
                others = [u for u in vs if u != v]
                if not others:
                    free = True
                    break
                s = new()
                big.append(s)
                for u in others:
                    clauses.append([-s, K[t][u]])
                if FUNC:
                    clauses.append([K[t + 1][v]] + [-K[t][u] for u in others])
            if not free:
                clauses.append(big)
            elif FUNC:
                clauses.append([K[t + 1][v]])
            if FUNC:
                clauses.append([-K[t][v], K[t + 1][v]])
    if FUNC:
        for v in vars_:
            clauses.append([-g[v], K[0][v]])
    for v in vars_:
        clauses.append([K[T][v]])
    def atmost(xs, k):
        n = len(xs)
        if k <= 0:
            clauses.extend([[-x] for x in xs])
            return
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

    atmost([g[v] for v in vars_], k)
    if PCAP and variant == "outhalf":
        # implied constraint (DERIVED): G restricted to the fixed variant's unknowns P is a cover of the fixed system
        # (P words occur only in round-0/C-call equations; S known there), and the fixed minimum is 8 (bf.c, plain and
        # orig rules), so at most k-8 guesses lie in S + E0/E2 internals.
        _, _, pv = build_fixed()
        atmost([g[v] for v in vars_ if v not in set(pv)], k - 8)
    return clauses, n_[0], g, vars_, ncq, rules


PCAP = False


def build_fixed():
    from gd_order import build
    return build("fixed", "len64")


def main():
    if sys.argv[1] == "--decode":
        variant, rset, k, T, out = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
        _, _, g, vars_, ncq, rules = encode(variant, rset, k, T)
        true = set()
        for line in open(out):
            if line.startswith("v "):
                true.update(int(x) for x in line[2:].split() if int(x) > 0)
        guess = [v for v in vars_ if g[v] in true]
        cov = closure_r(ncq, rules, set(guess))
        print(f"guessed ({len(guess)}): {guess}; closure under '{rset}' rules covers {len(cov)}/{len(vars_)}")
        return
    global FUNC, PCAP
    if "--func" in sys.argv:
        FUNC = True
        sys.argv.remove("--func")
    if "--pcap" in sys.argv:
        PCAP = True
        sys.argv.remove("--pcap")
    variant, rset, k, T = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    clauses, nv, _, _, _, _ = encode(variant, rset, k, T)
    fn = f"audit_{variant}_{rset}{'F' if FUNC else ''}{'P' if PCAP else ''}_k{k}_T{T}.cnf"
    with open(HERE + "\\" + fn, "w") as fh:
        fh.write(f"p cnf {nv} {len(clauses)}\n")
        for c in clauses:
            fh.write(" ".join(map(str, c)) + " 0\n")
    print(fn, nv, len(clauses))


if __name__ == "__main__":
    main()
