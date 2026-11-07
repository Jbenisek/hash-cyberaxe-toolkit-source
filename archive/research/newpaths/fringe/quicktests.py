"""Quick toy tests for the fringe angles (numpy, vectorised over many messages).
  absorb  : E0 output depends on Y0+m1 only (a and x enter G only via a1 = a+b+x)            [w=32]
  sym     : E0 eff. inputs = E2 eff. inputs  ->  out0=out2 and out5=out7                       [w=32]
  neutral : single-bit and two-bit message differences that keep the E0/E2 inputs unchanged   [w=8, w=32]
  rx      : rotational probability of one G call and of the K layer with BLAKE3 constants     [w=32]
Usage: python quicktests.py <test> [N]
"""
import sys
import itertools
import numpy as np

sys.dont_write_bytecode = True
import toyb3 as T  # noqa: E402


def vrotr(z, r, w):
    m = np.uint64((1 << w) - 1)
    r %= w
    if r == 0:
        return z & m
    return ((z >> np.uint64(r)) | (z << np.uint64(w - r))) & m


def vG(a, b, c, d, x, y, w):
    R = T.rots(w)
    m = np.uint64((1 << w) - 1)
    a = (a + b + x) & m
    d = vrotr(d ^ a, R[0], w)
    c = (c + d) & m
    b = vrotr(b ^ c, R[1], w)
    a = (a + b + y) & m
    d = vrotr(d ^ a, R[2], w)
    c = (c + d) & m
    b = vrotr(b ^ c, R[3], w)
    return a, b, c, d


def vtrace(M, w, upto="Z"):
    """M: (N,16) uint64.  Returns state after round-1 columns (Y) and final state Z (lists of arrays)."""
    N = M.shape[0]
    v = [np.full(N, x, dtype=np.uint64) for x in T.init_state(w)]
    Y = None
    for r in range(2):
        s = [M[:, i] for i in range(16)] if r == 0 else [M[:, T.PERM[i]] for i in range(16)]
        for j, idx in enumerate(T.COLS):
            o = vG(*(v[i] for i in idx), s[2 * j], s[2 * j + 1], w)
            for i, q in zip(idx, o):
                v[i] = q
        if r == 1:
            Y = list(v)
            if upto == "Y":
                return Y, None
        for j, idx in enumerate(T.DIAG):
            o = vG(*(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j], w)
            for i, q in zip(idx, o):
                v[i] = q
    return Y, v


def inA(Y, M):
    return np.stack([Y[0], Y[5], Y[10], Y[15], M[:, 1], M[:, 11], Y[2], Y[7], Y[8], Y[13], M[:, 9], M[:, 14]], axis=1)


def effA(Y, M, w):
    m = np.uint64((1 << w) - 1)
    return np.stack([(Y[0] + M[:, 1]) & m, Y[5], Y[10], Y[15], M[:, 11],
                     (Y[2] + M[:, 9]) & m, Y[7], Y[8], Y[13], M[:, 14]], axis=1)


def t_absorb(N=4096):
    w = 32
    rng = np.random.default_rng(1)
    m = np.uint64(0xFFFFFFFF)
    a, b, c, d, x, y, dl = (rng.integers(0, 2**32, N, dtype=np.uint64) for _ in range(7))
    o1 = vG(a, b, c, d, x, y, w)
    o2 = vG((a + dl) & m, b, c, d, (x - dl) & m, y, w)
    same = np.all(np.stack(o1) == np.stack(o2), axis=0).sum()
    o3 = vG(a, (b + dl) & m, c, d, (x - dl) & m, y, w)
    same_b = np.all(np.stack(o1) == np.stack(o3), axis=0).sum()
    print(f"absorb w=32: G(a+t,b,c,d,x-t,y) == G(a,b,c,d,x,y) in {same}/{N} random cases  [COMPUTED]")
    print(f"  control: G(a,b+t,c,d,x-t,y) == G(...) in {same_b}/{N} (b is used twice, no absorption)")


def t_sym(N=4096):
    w = 32
    rng = np.random.default_rng(2)
    m = np.uint64(0xFFFFFFFF)
    Y = [rng.integers(0, 2**32, N, dtype=np.uint64) for _ in range(16)]
    mm = [rng.integers(0, 2**32, N, dtype=np.uint64) for _ in range(16)]
    # impose E2 eff inputs = E0 eff inputs: Y7=Y5, Y8=Y10, Y13=Y15, m14=m11, Y2+m9 = Y0+m1 (m9 free, Y2 set)
    Y[7], Y[8], Y[13], mm[14] = Y[5], Y[10], Y[15], mm[11]
    Y[2] = (Y[0] + mm[1] - mm[9]) & m
    e0 = vG(Y[0], Y[5], Y[10], Y[15], mm[1], mm[11], w)
    e2 = vG(Y[2], Y[7], Y[8], Y[13], mm[9], mm[14], w)
    out0, out2 = e0[0] ^ e2[2], e2[0] ^ e0[2]
    out5, out7 = e0[1] ^ e2[3], e2[1] ^ e0[3]
    print(f"sym w=32: out0==out2 in {(out0 == out2).sum()}/{N}, out5==out7 in {(out5 == out7).sum()}/{N}  [COMPUTED]")
    # also through the real compression: use toyb3 at w=8 by brute-force search is too rare; E-layer suffices


def t_neutral(N=2048):
    for w, pairs in ((8, True), (32, False)):
        rng = np.random.default_rng(3)
        M = rng.integers(0, 2**w, (N, 16), dtype=np.uint64)
        Y, _ = vtrace(M, w, "Y")
        base, beff = inA(Y, M), effA(Y, M, w)
        bits = [(k, b) for k in range(16) for b in range(w)]
        diffs = [((k, b),) for k, b in bits]
        if pairs:
            diffs += list(itertools.combinations(bits, 2))
        best = (0, None)
        best_eff = (0, None)
        for dset in diffs:
            M2 = M.copy()
            for k, b in dset:
                M2[:, k] ^= np.uint64(1 << b)
            Y2, _ = vtrace(M2, w, "Y")
            hit = np.all(inA(Y2, M2) == base, axis=1).sum()
            hit_e = np.all(effA(Y2, M2, w) == beff, axis=1).sum()
            if hit > best[0]:
                best = (hit, dset)
            if hit_e > best_eff[0]:
                best_eff = (hit_e, dset)
        print(f"neutral w={w}: {len(diffs)} differences x {N} base messages; best count keeping E0/E2 inputs: "
              f"{best[0]} ({best[1]}); keeping effective inputs: {best_eff[0]} ({best_eff[1]})  [COMPUTED]")


def t_rx(N=1 << 20):
    w = 32
    rng = np.random.default_rng(4)
    for r in (1, 8, 16):
        ins = [rng.integers(0, 2**32, N, dtype=np.uint64) for _ in range(6)]
        o = vG(*ins, w)
        orr = vG(*(vrotr(z, w - r, w) for z in ins), w)       # rotate left by r
        ok = np.all(np.stack([vrotr(z, w - r, w) for z in o]) == np.stack(orr), axis=0).sum()
        p = ok / N
        print(f"rx w=32 r={r}: P[G(rot x) = rot G(x)] = {ok}/{N} = 2^{np.log2(p) if p else float('-inf'):.2f}"
              f"; 16 calls -> 2^{16 * np.log2(p) if p else float('-inf'):.1f}  [COMPUTED per call, DERIVED for 16]")
    iv = T.IV32
    inv = [x for x in iv for r in range(1, 32) if ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF == x]
    print(f"rx: IV words invariant under some rotation: {inv} -> the fixed IV/counter/len/flags words of the two"
          f" members are equal, so the pair starts with a dense rotational-xor difference  [COMPUTED]")


def t_sibling(N=200):
    """Length siblings: for one base message, every block length L gets (m4_L, m5_L) with identical round-0 output.
    K2 = G(IV2, IV6, IV2, L; m4, m5): d enters only via d1 = rotr(L ^ a1, 16) and a1 only via d1 and a2, so
    a1_L = a1* ^ L, m4_L = a1_L - IV2 - IV6, m5_L = m5* + a1* - a1_L keeps K2's output (exact, any L)."""
    import random as _r
    rng = _r.Random(7)
    w, M32 = 32, 0xFFFFFFFF
    iv = T.IV32
    okQ = okQ_other = tot = 0
    diff_words = set()
    for _ in range(N):
        base = [rng.getrandbits(32) for _ in range(16)]
        L0 = 63
        a1s = (iv[2] + iv[6] + base[4]) & M32
        astar = a1s ^ L0
        ref = None
        for L in range(1, 65):
            a1L = astar ^ L
            m = list(base)
            m[4] = (a1L - iv[2] - iv[6]) & M32
            m[5] = (base[5] + a1s - a1L) & M32
            t = T.trace(m, w, blen=L)
            if ref is None:
                ref = t
            okQ += t["Q"] == ref["Q"]
            okQ_other += t["Q"] == T.trace(base, w, blen=L)["Q"]
            for i in range(16):
                if t["Y"][i] != ref["Y"][i]:
                    diff_words.add(i)
            tot += 1
    print(f"sibling w=32: round-0 output Q identical across all 64 lengths in {okQ}/{tot} sibling messages "
          f"(control, unadjusted m4,m5: {okQ_other}/{tot})  [COMPUTED]")
    print(f"  Y words (after round-1 columns) that differ between siblings: {sorted(diff_words)} "
          f"(C3 outputs only, since m4 is C3's x; m5 is E1's y)  [COMPUTED]")


if __name__ == "__main__":
    t = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    f = {"absorb": t_absorb, "sym": t_sym, "neutral": t_neutral, "rx": t_rx, "sibling": t_sibling}[t]
    f(n) if n else f()
