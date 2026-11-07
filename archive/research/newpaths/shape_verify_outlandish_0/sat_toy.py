"""Independent SAT cross-check of the lemma on BLAKE3-shaped toy systems small enough for kissat to decide.

Toy systems: ONE round of BLAKE3 (calls K0..K3, D0..D3, words = 16 message + 64 intermediate) with a subset of
out_i = v_i ^ v_{i+8} held.  For each, cores.py predicts the exact minimum check count c by the lemma; this script
writes the layered-propagation CNF (same idea as ../gd_sat.py, own code) for  guesses <= F + c - 1  (lemma: UNSAT)
and  guesses <= F + c  (lemma: SAT).  Depth T = number of equations (exact: propagation never needs more layers).
Usage: python sat_toy.py   -> writes toy_*.cnf and toy_list.txt
"""
from build import system
from cores import incid, plain_core, min_deletions


def encode(eqs, const, k):
    E, occ = incid(eqs, const)
    words = sorted(occ)
    T = len(eqs)
    n = [0]
    cl = []

    def new():
        n[0] += 1
        return n[0]

    g = {v: new() for v in words}
    K = [{v: new() for v in words} for _ in range(T + 1)]
    for v in words:
        cl.append([-K[0][v], g[v]])
    for t in range(T):
        for v in words:
            big = [-K[t + 1][v], K[t][v]]
            for i in occ[v]:
                others = [u for u in E[i] if u != v]
                if not others:
                    big = None
                    break
                s = new()
                big.append(s)
                for u in others:
                    cl.append([-s, K[t][u]])
            if big:
                cl.append(big)
    for v in words:
        cl.append([K[T][v]])
    xs = [g[v] for v in words]
    if k <= 0:
        cl += [[-x] for x in xs]
    else:
        S = [[new() for _ in range(k)] for _ in xs]
        cl.append([-xs[0], S[0][0]])
        cl += [[-S[0][j]] for j in range(1, k)]
        for i in range(1, len(xs)):
            cl.append([-xs[i], S[i][0]])
            cl.append([-S[i - 1][0], S[i][0]])
            for j in range(1, k):
                cl.append([-xs[i], -S[i - 1][j - 1], S[i][j]])
                cl.append([-S[i - 1][j], S[i][j]])
            cl.append([-xs[i], -S[i - 1][k - 1]])
    return n[0], cl


def main():
    cases = [("out0",), ("out2",), ("out0", "out2", "out5"), ("out0", "out1", "out2", "out3")]
    with open("toy_list.txt", "w") as fh:
        for held in cases:
            eqs, const, _ = system(held=held, rounds=1)
            E, occ = incid(eqs, const)
            F = len(occ) - len(eqs)
            core = plain_core(E, occ, set(range(len(eqs))))
            c, D = min_deletions(E, occ, set(range(len(eqs))), len(held))
            for k, expect in ((F + c - 1, "UNSAT"), (F + c, "SAT")):
                nv, cl = encode(eqs, const, k)
                fn = f"toy_r1_{'_'.join(held)}_k{k}.cnf"
                with open(fn, "w") as f:
                    f.write(f"p cnf {nv} {len(cl)}\n")
                    for c_ in cl:
                        f.write(" ".join(map(str, c_)) + " 0\n")
                line = (f"{fn} words {len(occ)} eqs {len(eqs)} F {F} core_eqs {len(core)} lemma_c {c} "
                        f"guesses<= {k} lemma_says {expect}")
                print(line)
                fh.write(line + "\n")


def real(held=("out0",)):
    """The 2-round instance itself (same question as ../shape_odd/sat_sphere.py, own encoder)."""
    eqs, const, _ = system(held=held)
    E, occ = incid(eqs, const)
    F = len(occ) - len(eqs)
    for k in (F, F + 1):
        nv, cl = encode(eqs, const, k)
        fn = f"real_{'_'.join(held)}_k{k}.cnf"
        with open(fn, "w") as f:
            f.write(f"p cnf {nv} {len(cl)}\n")
            for c_ in cl:
                f.write(" ".join(map(str, c_)) + " 0\n")
        print(fn, nv, len(cl), "F", F)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "real":
        real()
    else:
        main()
