"""Lower bound on the free width of ANY join tree with promotions (slack <= S), window RELATIVE to the number R of
equations that keep an unknown after promotion:  R/3 <= |A n remaining| < 2R/3   (shape_any agent).
Validity (DERIVED): with k = R/3 the heavy path of any tree over the R remaining equations has a node of
size in [k, 2k) = [R/3, 2R/3); no separate drop check is needed.  Optional letters: count only equations of
those G calls (weights), both in R and in the window.
Usage: python lbsat5.py <sys> <T> <S> <out.cnf> [letters]
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
    for e, vs in enumerate(eqs):
        f.cl.append([-c[e], x[e]])
        f.cl.append([-c[e], r[e]])
        for v in vs:
            f.cl.append([-c[e], y[v], p[v]])
        f.cl.append([-z[e], x[e]]); f.cl.append([-z[e], r[e]]); f.cl.append([z[e], -x[e], -r[e]])
    for v in range(N):
        for e in occ[v]:
            for g in occ[v]:
                if e != g:
                    f.cl.append([-x[e], x[g], y[v], p[v]])
        f.cl.append([q[v], -y[v], p[v]])
    oq = f.tot(q, up=True, down=False)
    oc = f.tot(c, up=False, down=True)
    nq, nc = len(q), len(c)
    for j in range(0, nq - T):
        i = T + j + 1
        if i > nq:
            break
        if j + 1 <= nc:
            f.cl.append([-oq[i], oc[j + 1]])
        else:
            f.cl.append([-oq[i]])
    zw = [z[e] for e in range(E) if wt[e]]
    rw = [r[e] for e in range(E) if wt[e]]
    oz = f.tot(zw, up=True, down=True)
    orr = f.tot(rw, up=True, down=True)
    nz, nr = len(zw), len(rw)
    # 3 Z >= R :  R >= 3j+1  ->  Z >= j+1
    for j in range(0, nr):
        if 3 * j + 1 > nr:
            break
        f.cl.append([-orr[3 * j + 1]] + ([oz[j + 1]] if j + 1 <= nz else []))
    # 3 Z <= 2R - 1 :  Z >= j  ->  R >= ceil((3j+1)/2)
    for j in range(1, nz + 1):
        need = (3 * j + 2) // 2
        f.cl.append([-oz[j]] + ([orr[need]] if need <= nr else []))
    f.write(out)


if __name__ == "__main__":
    main()
