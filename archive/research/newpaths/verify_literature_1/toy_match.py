# toy_match.py -- verify_literature_1
# Generic toy of "partial-target via MITM filter, then birthday on the rest".
# Cell size w bits (toy), h = 8 cells, t = 4 target cells, c of them matched by a two-list
# filter f(A) = g(B) (c*w bits), the other 4 cells random -> birthday.
# Lists are prefixes A = 0..L-1, B = 0..L-1. For every matched pair its entry time is
# max(i, j)+1; the first L at which two matched pairs collide on the other 4 cells is exact.
# Work = 2L (list elements) + matches up to L (full evaluations).
# Claim (literal formula, c = t = 4, DoF >= 4) predicts work ~ (2^w)^2. Generic bound
# predicts ~ 2 * (2^w)^(1 + c/2) for c >= 2.
import numpy as np, sys, math

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def mix(x):
    x = x.astype(np.uint64)
    x ^= x >> np.uint64(30); x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(27); x *= np.uint64(0x94D049BB133111EB)
    x ^= x >> np.uint64(31)
    return x

def trial(w, c, seed, hcells=8, tcells=4):
    rest_bits = (hcells - tcells) * w
    fbits = c * w
    need = w * (2 + c) / 2 if c >= 2 else w * 1.0   # log2 list length expected
    Lmax = int(2 ** (need + 1.5))
    Lmax = max(Lmax, 64)
    if Lmax > 2 ** 24:
        Lmax = 2 ** 24
    idx = np.arange(Lmax, dtype=np.uint64)
    s1 = np.uint64(seed * 7919 + 1); s2 = np.uint64(seed * 104729 + 2); s3 = np.uint64(seed * 15485863 + 3)
    if fbits > 0:
        fm = np.uint64((1 << fbits) - 1)
        fa = mix(idx ^ (s1 << np.uint64(40))) & fm
        gb = mix(idx ^ (s2 << np.uint64(40))) & fm
    else:
        fa = np.zeros(Lmax, dtype=np.uint64); gb = np.zeros(Lmax, dtype=np.uint64)
    order = np.argsort(fa, kind='stable')
    fas = fa[order]
    lo = np.searchsorted(fas, gb, 'left'); hi = np.searchsorted(fas, gb, 'right')
    cnt = hi - lo
    if c == 0:
        # every pair matches: restrict to a square of side Lsq to keep it small
        Lsq = min(Lmax, int(2 ** (w + 2.5)))
        I, J = np.meshgrid(np.arange(Lsq), np.arange(Lsq), indexing='ij')
        ii = I.ravel().astype(np.int64); jj = J.ravel().astype(np.int64)
    else:
        jj = np.repeat(np.arange(Lmax), cnt)
        starts = np.repeat(lo, cnt)
        offs = np.arange(len(jj)) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        ii = order[starts + offs].astype(np.int64)
    entry = np.maximum(ii, jj) + 1
    rm = np.uint64((1 << rest_bits) - 1)
    r = mix(mix(ii.astype(np.uint64) ^ (s3 << np.uint64(32))) ^ jj.astype(np.uint64)) & rm
    o = np.lexsort((entry, r))
    rs = r[o]; es = entry[o]
    same = rs[1:] == rs[:-1]
    if not same.any():
        return None
    # earliest collision: for runs of equal r, the 2nd smallest entry time in the run
    t_coll = np.where(same, np.maximum(es[1:], es[:-1]), np.iinfo(np.int64).max)
    # within a sorted run, consecutive pairs give the min over pairs of max(entry) -> exact
    Lstar = int(t_coll.min())
    nmatch = int((entry <= Lstar).sum())
    work = 2 * Lstar + nmatch
    return Lstar, nmatch, work

if __name__ == "__main__":
    ws = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else [4, 5, 6, 7]
    cs = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0, 2, 3, 4]
    trials = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    print("w c | median log2 L*  median log2 matches  median log2 work | claim(2w)  generic")
    for c in cs:
        for w in ws:
            res = [trial(w, c, s) for s in range(trials)]
            ok = [x for x in res if x is not None]
            if not ok:
                print(f"{w} {c} | no collision in {trials} trials"); continue
            L = sorted(math.log2(x[0]) for x in ok); M = sorted(math.log2(max(x[1], 1)) for x in ok)
            W = sorted(math.log2(x[2]) for x in ok)
            k = len(ok) // 2
            gen = 2 * w if c <= 2 else w * (1 + c / 2) + 1
            print(f"{w} {c} | {L[k]:6.2f}  {M[k]:6.2f}  {W[k]:6.2f} | {2*w:3d}  {gen:5.1f}  ({len(ok)}/{trials} found)", flush=True)
