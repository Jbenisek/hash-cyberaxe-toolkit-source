"""TEST A2 follow-up (COMPUTED): sparse message-word sets S with a NONZERO full-collision kernel in the XOR-linear
model (generic dimension would be 0 for |S| < 8).  For each such S at width w: kernel dimension, and the minimum
exact weights over the kernel (enumerated when dim <= 14).  Usage: python -B sparse_full.py w SMAX [withlen]"""
import sys, itertools, time
import numpy as np
sys.dont_write_bytecode = True
from lin import Model, nullspace, exact_weight


def main(w, smax, withlen):
    md = Model(w)
    A = md.out_matrix()
    Fall, gall = md.positions(lambda a: True)
    g1 = [g for g in gall if md.adds[g[0]][0] == 1]
    gE = [g for g in gall if md.adds[g[0]][0] == 1 and md.adds[g[0]][1][0] == "E"]
    t0 = time.time()
    out = [f"sparse_full.py w={w} SMAX={smax} len={withlen}"]
    for size in range(1, smax + 1):
        hits = 0
        for S in itertools.combinations(range(16), size):
            cols = [i * w + j for i in S for j in range(w)] + ([16 * w + j for j in range(md.lw)] if withlen else [])
            K = nullspace(A[:, cols])
            d = K.shape[0]
            if d == 0:
                continue
            hits += 1
            best = None
            if d <= 14:
                for c in itertools.product((0, 1), repeat=d):
                    if not any(c):
                        continue
                    v = np.bitwise_xor.reduce(K[np.array(c, dtype=bool)], axis=0)
                    var = np.zeros(md.nv, dtype=np.int64)
                    var[cols] = v
                    img = ((Fall.astype(np.int64) @ var) & 1).astype(np.uint8)
                    w1 = exact_weight(img, g1, w)
                    if best is None or w1 < best[0]:
                        best = (w1, exact_weight(img, gall, w), exact_weight(img, gE, w),
                                {S[k]: hex(int("".join(str(int(b)) for b in v[k * w:(k + 1) * w][::-1]), 2)) for k in range(size)})
            out.append(f"  S={S} dim={d} best: W_r1={best[0] if best else '?'} W_all={best[1] if best else '?'} "
                       f"W_E={best[2] if best else '?'} dM={best[3] if best else '?'}")
            print(out[-1], flush=True)
        out.append(f" size {size}: {hits} sets with nonzero full-collision kernel ({time.time() - t0:.0f}s)")
        print(out[-1], flush=True)
    with open(f"sparse_full_w{w}{'_len' if withlen else ''}.txt", "w") as fh:
        fh.write(__doc__ + "\n" + "\n".join(out) + "\n")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), len(sys.argv) > 3 and sys.argv[3] == "len")
