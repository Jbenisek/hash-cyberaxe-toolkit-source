"""lbsat5.py plus redundant clauses (same solutions up to dominance):  y_v -> some x_e with v in e;  not(p_v and y_v);
q_v <-> y_v (when not promoted);  c_e <- x_e and r_e and every word of e in Y or P.   (shape_any agent)
Usage: python lbsat6.py <sys> <T> <S> <out.cnf> [letters]
"""
import sys
from lbsat4 import CNF, load, promo_part


def main():
    fn, T, S, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    letters = sys.argv[5] if len(sys.argv) > 5 else None
    N, E, eqs, names = load(fn)
    wt = [1 if letters is None or nm[0] in letters else 0 for nm in names]
    occ = [[] for _ in range(N)]
    for e, vs in enumerate(eqs):
        for v in vs:
            occ[v].append(e)
    f = CNF()
    x = [f.new() for _ in range(E)]
    y = [f.new() for _ in range(N)]
    c = [f.new() for _ in range(E)]
    q = [f.new() for _ in range(N)]
    z = [f.new() for _ in range(E)]
    p, r = promo_part(f, N, E, eqs, S)
    u = [f.new() for _ in range(N)]                       # u_v <-> y_v or p_v
    for v in range(N):
        f.cl.append([-u[v], y[v], p[v]]); f.cl.append([u[v], -y[v]]); f.cl.append([u[v], -p[v]])
        f.cl.append([-y[v], -p[v]])
        f.cl.append([-y[v]] + [x[e] for e in occ[v]])
        f.cl.append([-q[v], y[v]])
    for e, vs in enumerate(eqs):
        f.cl.append([-c[e], x[e]])
        f.cl.append([-c[e], r[e]])
        for v in vs:
            f.cl.append([-c[e], u[v]])
        f.cl.append([c[e], -x[e], -r[e]] + [-u[v] for v in vs])
        f.cl.append([-z[e], x[e]]); f.cl.append([-z[e], r[e]]); f.cl.append([z[e], -x[e], -r[e]])
    for v in range(N):
        for e in occ[v]:
            for g in occ[v]:
                if e != g:
                    f.cl.append([-x[e], x[g], u[v]])
        f.cl.append([q[v], -y[v]])
    oq = f.tot(q, up=True, down=False)
    oc = f.tot(c, up=False, down=True)
    nq, nc = len(q), len(c)
    for j in range(0, nq - T):
        i = T + j + 1
        if i > nq:
            break
        f.cl.append([-oq[i]] + ([oc[j + 1]] if j + 1 <= nc else []))
    zw = [z[e] for e in range(E) if wt[e]]
    rw = [r[e] for e in range(E) if wt[e]]
    oz = f.tot(zw, up=True, down=True)
    orr = f.tot(rw, up=True, down=True)
    nz, nr = len(zw), len(rw)
    for j in range(0, nr):
        if 3 * j + 1 > nr:
            break
        f.cl.append([-orr[3 * j + 1]] + ([oz[j + 1]] if j + 1 <= nz else []))
    for j in range(1, nz + 1):
        need = (3 * j + 2) // 2
        f.cl.append([-oz[j]] + ([orr[need]] if need <= nr else []))
    f.write(out)


if __name__ == "__main__":
    main()
