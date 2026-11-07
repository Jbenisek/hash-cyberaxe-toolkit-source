"""Largest proper closed region with small delta (ksplit NOTES section 3).
Is there a closed region A (closed under propagation and the file's table macros), A != W, with
delta(A) = |A| - Ein(A) <= D and |A| >= S ?   (DIMACS; variables 1..N = membership)
Usage: python bigsat.py <sysfile> <D> <S> <out.cnf>  |  python bigsat.py --decode <sysfile> <solver out>
"""
import sys
from regsat import CNF, load
from rootsat import load_macros


def encode(fn, D, S):
    N, E, F, names, eqs = load(fn)
    mac = load_macros(fn)
    c = CNF()
    a = [c.new() for _ in range(N)]
    for _, ws in eqs:
        for w in ws:
            c.cl.append([-a[v] for v in ws if v != w] + [a[w]])
    for trig, tgt in mac:
        c.cl.append([-a[v] for v in trig] + [a[tgt]])
    c.cl.append([-a[w] for w in range(N)])
    ev = [c.new() for _ in range(E)]
    for j, (_, ws) in enumerate(eqs):
        for w in ws:
            c.cl.append([-ev[j], a[w]])
    c.atmost(a + [-x for x in ev], D + E)
    c.atleast(a, S)
    return c


if __name__ == "__main__":
    if sys.argv[1] == "--decode":
        N, E, F, names, eqs = load(sys.argv[2])
        true = set()
        for line in open(sys.argv[3]):
            if line.startswith("v "):
                true.update(int(x) for x in line[2:].split() if int(x) > 0)
        A = {i for i in range(N) if (i + 1) in true}
        ein = sum(1 for _, ws in eqs if all(w in A for w in ws))
        print(f"|A|={len(A)} Ein={ein} delta={len(A) - ein}")
        print("A:", " ".join(names[i] for i in sorted(A)))
    else:
        c = encode(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
        with open(sys.argv[4], "w") as f:
            f.write(f"p cnf {c.n} {len(c.cl)}\n")
            for cl in c.cl:
                f.write(" ".join(map(str, cl)) + " 0\n")
        print(sys.argv[4], c.n, len(c.cl))
