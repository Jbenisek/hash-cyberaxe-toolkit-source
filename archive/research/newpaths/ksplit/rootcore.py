"""Root-split necessary condition without layered closure (ksplit NOTES section 3):
two proper closed regions A, B with delta(A) <= D, delta(B) <= D, delta(A u B) <= D, and A u B containing the peeling core of the
system (every word that cannot be derived as a dangling word after the join).  UNSAT => no tree below 2^(32(D+1)-64).
Usage: python rootcore.py <sysfile> <D> <out.cnf>"""
import sys
from regsat import CNF, load
from rootsat import load_macros


def core(N, eqs):
    alive_w, alive_e = set(range(N)), set(range(len(eqs)))
    ch = True
    while ch:
        ch = False
        deg, last = {w: 0 for w in alive_w}, {}
        for j in alive_e:
            for w in eqs[j][1]:
                if w in alive_w:
                    deg[w] += 1
                    last[w] = j
        for w in list(alive_w):
            if deg[w] <= 1:
                alive_w.discard(w)
                if deg[w] == 1:
                    alive_e.discard(last[w])
                ch = True
                break
    return alive_w


def main():
    fn, D, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    N, E, F, names, eqs = load(fn)
    mac = load_macros(fn)
    cw = core(N, eqs)
    c = CNF()
    a = [c.new() for _ in range(N)]
    b = [c.new() for _ in range(N)]
    for X in (a, b):
        for _, ws in eqs:
            for w in ws:
                c.cl.append([-X[v] for v in ws if v != w] + [X[w]])
        for trig, tgt in mac:
            c.cl.append([-X[v] for v in trig] + [X[tgt]])
        c.cl.append([-X[w] for w in range(N)])
        ev = [c.new() for _ in range(E)]
        for j, (_, ws) in enumerate(eqs):
            for w in ws:
                c.cl.append([-ev[j], X[w]])
        c.atmost(X + [-x for x in ev], D + E)
    for w in cw:
        c.cl.append([a[w], b[w]])
    # delta(A u B) <= D as well
    u = [c.new() for _ in range(N)]
    for w in range(N):
        c.cl.append([-a[w], u[w]])
        c.cl.append([-b[w], u[w]])
        c.cl.append([-u[w], a[w], b[w]])
    eu = [c.new() for _ in range(E)]
    for j, (_, ws) in enumerate(eqs):
        for w in ws:
            c.cl.append([-eu[j], u[w]])
    c.atmost(u + [-x for x in eu], D + E)
    # symmetry: |A| >= |B| is not needed; break by forcing the first core word into A
    c.cl.append([a[min(cw)]])
    with open(out, "w") as f:
        f.write(f"p cnf {c.n} {len(c.cl)}\n")
        for cl in c.cl:
            f.write(" ".join(map(str, cl)) + " 0\n")
    print(out, "core", len(cw), "vars", c.n, "clauses", len(c.cl))


if __name__ == "__main__":
    main()
