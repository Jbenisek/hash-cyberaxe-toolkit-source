"""Root-split SAT for the general lower bound (ksplit NOTES section 3).

Asks: are there two PROPER closed regions A, B (A != W, B != W, closed under propagation and table macros) with
    delta(A) <= DA, delta(B) <= DB, delta(A u B) <= DU, and cl(A u B) = W ?
For a tree to cost < 2^96 (generic model) the lowest node whose closure is W needs such children with
DA = DB = DU = 4 (NOTES 3).  UNSAT => no tree / k-list structure below 2^96 in this model.
Usage: python rootsat.py <sysfile> <DA> <DB> <DU> <T layers> <out.cnf>
       python rootsat.py --decode <sysfile> <solver output>     (variables 1..N = A, N+1..2N = B)
"""
import sys

from regsat import CNF, load


def load_macros(fn):
    with open(fn) as f:
        tok = f.read().split()
    N, E, NM, F = map(int, tok[:4])
    p = 4 + N
    for _ in range(E):
        k = int(tok[p + 1])
        p += 2 + k
    mac = []
    for _ in range(NM):
        t = int(tok[p])
        trig = list(map(int, tok[p + 1:p + 1 + t]))
        tgt = int(tok[p + 1 + t])
        p += 2 + t
        mac.append((trig, tgt))
    return mac


def encode(fn, DA, DB, DU, T):
    N, E, F, names, eqs = load(fn)
    mac = load_macros(fn)
    c = CNF()
    a = [c.new() for _ in range(N)]
    b = [c.new() for _ in range(N)]
    u = [c.new() for _ in range(N)]
    for X in (a, b):
        for _, ws in eqs:                      # closedness
            for w in ws:
                c.cl.append([-X[v] for v in ws if v != w] + [X[w]])
        for trig, tgt in mac:
            c.cl.append([-X[v] for v in trig] + [X[tgt]])
        c.cl.append([-X[w] for w in range(N)])  # proper: some word outside
    for w in range(N):
        c.cl.append([-a[w], u[w]])
        c.cl.append([-b[w], u[w]])
        c.cl.append([-u[w], a[w], b[w]])

    def delta_le(X, D):
        ev = [c.new() for _ in range(E)]
        for j, (_, ws) in enumerate(eqs):
            for w in ws:
                c.cl.append([-ev[j], X[w]])
        c.atmost(X + [-x for x in ev], D + E)

    delta_le(a, DA)
    delta_le(b, DB)
    delta_le(u, DU)
    # cl(U) = W : layered derivation
    K = [u]
    for t in range(T):
        nxt = [c.new() for _ in range(N)]
        for w in range(N):
            big = [-nxt[w], K[-1][w]]
            for _, ws in eqs:
                if w not in ws:
                    continue
                others = [v for v in ws if v != w]
                s = c.new()
                big.append(s)
                for v in others:
                    c.cl.append([-s, K[-1][v]])
            for trig, tgt in mac:
                if tgt != w:
                    continue
                s = c.new()
                big.append(s)
                for v in trig:
                    c.cl.append([-s, K[-1][v]])
            c.cl.append(big)
        K.append(nxt)
    for w in range(N):
        c.cl.append([K[-1][w]])
    return c


def main():
    if sys.argv[1] == "--decode":
        fn, out = sys.argv[2], sys.argv[3]
        N, E, F, names, eqs = load(fn)
        true = set()
        for line in open(out):
            if line.startswith("v "):
                true.update(int(x) for x in line[2:].split() if int(x) > 0)
        A = {i for i in range(N) if (i + 1) in true}
        B = {i for i in range(N) if (N + i + 1) in true}
        U = A | B

        def dl(S):
            return len(S) - sum(1 for _, ws in eqs if all(w in S for w in ws))
        print(f"|A|={len(A)} d={dl(A)}  |B|={len(B)} d={dl(B)}  |AuB|={len(U)} d={dl(U)}")
        print("A:", " ".join(names[i] for i in sorted(A)))
        print("B:", " ".join(names[i] for i in sorted(B)))
        return
    fn, DA, DB, DU, T, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    c = encode(fn, DA, DB, DU, T)
    with open(out, "w") as f:
        f.write(f"p cnf {c.n} {len(c.cl)}\n")
        for cl in c.cl:
            f.write(" ".join(map(str, cl)) + " 0\n")
    print(out, c.n, len(c.cl))


if __name__ == "__main__":
    main()
