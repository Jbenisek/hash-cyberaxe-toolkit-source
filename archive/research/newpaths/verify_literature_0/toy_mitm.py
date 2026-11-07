# Toy run of Algorithm 6 (Dong et al. 2021, MITM partial-target -> collision).
# w=4-bit cells, h=8 cells (32-bit output), t=m=4 cells (16-bit target, matched exactly),
# DoF+ = DoF- = 4 cells (16 bits each side). Paper eq 9 (table terms dropped) predicts
# (2^4)^(8/2 - min{4-2,4-2,4-2,2}) = 2^8 work.  Constrained bound predicts ~2^(w(h+t)/4)=2^12
# per list (2^13 for both lists).
# Episode = fresh random F,G,R (new gray constants). Forward list: L random x, key F(x);
# backward: L random y, key G(y); match F(x)==G(y) (target cells = 0); each match is a
# partial-target preimage, costs 1 evaluation of the remaining 16 output bits R(x,y);
# birthday on R across all episodes. Cost = list elements + matches, until first collision.
import numpy as np, sys

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def mix(z):
    z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return z ^ (z >> np.uint64(31))

def run(L, rng):
    seen = set(); cost = 0
    while True:
        s = np.uint64(rng.integers(1, 2**62))
        x = rng.choice(65536, size=L, replace=False).astype(np.uint64)
        y = rng.choice(65536, size=L, replace=False).astype(np.uint64)
        Fx = (mix(x ^ (s * np.uint64(3))) & np.uint64(0xFFFF))
        Gy = (mix(y ^ (s * np.uint64(5)) ^ np.uint64(1 << 40)) & np.uint64(0xFFFF))
        order = np.argsort(Fx, kind='stable'); Fs = Fx[order]
        lo = np.searchsorted(Fs, Gy, 'left'); hi = np.searchsorted(Fs, Gy, 'right')
        cnt = hi - lo
        yi = np.repeat(np.arange(L), cnt)
        xi = order[np.concatenate([np.arange(a, b) for a, b in zip(lo, hi) if b > a])] if cnt.sum() else np.array([], dtype=int)
        R = (mix((x[xi] << np.uint64(16)) | y[yi] | (s << np.uint64(32))) & np.uint64(0xFFFF)) if len(yi) else []
        cost += L  # forward list
        done_y = 0; nm = 0
        for k in range(len(yi)):
            nm += 1
            r = int(R[k])
            if r in seen:
                return cost + int(yi[k]) + 1 + nm
            seen.add(r)
        cost += L + nm

rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
print("log2L  trials  mean_cost  log2(mean_cost)")
for lg in [8, 10, 11, 12, 13, 14, 16]:
    tr = 40 if lg <= 13 else 20
    cs = [run(2**lg, rng) for _ in range(tr)]
    m = float(np.mean(cs))
    print(f"{lg:5d}  {tr:6d}  {m:10.0f}  {np.log2(m):6.2f}")
print("paper eq9 prediction: log2 = 8.00 ; constrained bound: log2 ~ 13 (2 lists of 2^12) ")
