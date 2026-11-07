"""TEST A2 (exact, XOR-linear model): sparse message differences, as in every published BLAKE/BLAKE2 trail
(GM09, DK11, GKNWW14 sec. 6 restrict to few active words).  For every set S of active message words
(|S| <= SMAX) and with/without a block-length difference (low 7 bits of v14), compute the dimension of
  {(dM supported on S, dv14) : dout = 0}   (full collision; fold included)
and the same for each half (out0,2,5,7 / out1,3,4,6).  Generic expectation: |S|w (+7) - 8w (or -4w).
A dimension above that would be structure; when a full-collision kernel exceeds the generic dimension
(and has dim <= 12) it is enumerated and the minimum exact weights are reported.
Usage: python -B step3_sparse.py w SMAX"""
import sys, itertools
import numpy as np
sys.dont_write_bytecode = True
from lin import Model, nullspace, exact_weight


def main(w, smax):
    md = Model(w)
    Afull = md.out_matrix().astype(np.uint8)
    Ahalf = {"full": Afull, "A": md.out_matrix((0, 2, 5, 7)), "B": md.out_matrix((1, 3, 4, 6))}
    Fall, gall = md.positions(lambda a: True)
    r1idx = [g for g in gall if md.adds[g[0]][0] == 1]
    lines = []
    stats = {}
    for withlen in (False, True):
        for size in range(1, smax + 1):
            for S in itertools.combinations(range(16), size):
                cols = [i * w + j for i in S for j in range(w)]
                if withlen:
                    cols += [16 * w + j for j in range(md.lw)]
                for tgt, A in Ahalf.items():
                    sub = A[:, cols]
                    K = nullspace(sub)
                    d = K.shape[0]
                    gen = len(cols) - A.shape[0]
                    key = (withlen, size, tgt)
                    st = stats.setdefault(key, [0, 0, 0])
                    st[0] += 1
                    if d > 0:
                        st[1] += 1
                    if d > max(gen, 0):
                        st[2] += 1
                        lines.append(f"EXCESS w={w} len={withlen} S={S} target={tgt} dim={d} generic={gen}")
                    if d > max(gen, 0) and d <= 12 and tgt == "full":   # enumerate only structured excess
                        best = None
                        for c in itertools.product((0, 1), repeat=d):
                            if not any(c):
                                continue
                            v = np.bitwise_xor.reduce(K[np.array(c, dtype=bool)], axis=0)
                            var = np.zeros(md.nv, dtype=np.int64)
                            var[cols] = v
                            img = ((Fall.astype(np.int64) @ var) & 1).astype(np.uint8)
                            wa = exact_weight(img, gall, w)
                            w1 = exact_weight(img, r1idx, w)
                            if best is None or w1 < best[1]:
                                best = (wa, w1)
                        lines.append(f"KERNEL w={w} len={withlen} S={S} dim={d} min W_r1={best[1]} (W_all {best[0]})")
    out = [f"step3_sparse.py w={w} SMAX={smax}  (COMPUTED)",
           "rows: (len_diff allowed, |S|, target): subsets tried, subsets with nonzero kernel, subsets above generic dim"]
    for k, v in sorted(stats.items()):
        out.append(f"  len={k[0]!s:5} |S|={k[1]:2d} target={k[2]:4s}: tried {v[0]:5d}  nonzero {v[1]:5d}  excess {v[2]:5d}")
    out += lines[:400]
    txt = "\n".join(out)
    print(txt)
    with open(f"step3_sparse_w{w}.txt", "w") as fh:
        fh.write(txt + "\n")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
