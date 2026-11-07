"""TEST 1c: does the filed path's trial model depend on the chunk counter?
In the filed construction q2 = 0 and k2 = 0 are the counter words v12, v13 (job20 ANSWER.md:
'K0.a1 = ROL(K0.d1,16)' and 'K1.a1 = ROL(K1.d1,16)').  With the last-chunk trick (TEST 1a) the
counter t is free, so q2 = t_lo and k2 = t_hi can be chosen.  This reuses Grok's FIX7 hand model
(research/grok/work/job20_copass/compare_models.py, h1_hand + draw_hand, copied, read-only import of
exact_model), which job20 found indistinguishable from the exact model, and sweeps q2 (and k2).
Measured: H4 pass rate p0 and H4 co-pass for the e1/X2 flips (the cluster lever's inputs).
CAVEAT: the model treats the other words as independent uniform; the pins (Y3, X3, X7, X11, X15,
W13, W4) were found for t = 0 and are assumed to stay reachable (round 0 is a bijection).
Usage: python -B t1c_counter.py [log2 samples=20] [seed=1]
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job20_copass'))
import numpy as np
import exact_model as E

Y3, X11, X15, MASK = E.Y3, E.X11, E.X15, E.MASK


def u(rng, n):
    return rng.integers(0, 1 << 32, n, dtype=np.uint64).astype(np.uint32)


def u32(x):
    return np.uint32(int(x) & 0xFFFFFFFF)


def h1_hand(C, e1, X2):  # copied from compare_models.py (Grok job20)
    Y4 = (e1 - Y3) & MASK
    Y8 = E.rol(Y4, 7) ^ C["Cb"]
    Y12 = (Y8 - C["Cc"]) & MASK
    Y0 = E.rol(Y12, 8) ^ C["Cd"]
    P = (Y0 - C["Cb"] - C["w6"]) & MASK
    X12 = E.rol(C["Cd"], 16) ^ P
    Db = E.ror(C["S6"] ^ ((X11 - X12) & MASK), 12)
    Q = E.ror(Db ^ X11, 7)
    Dd = E.rol(C["X13"], 8) ^ X2
    S13 = E.rol(Dd, 16) ^ ((X2 - C["k0"]) & MASK)
    w2 = (E.rol(((C["S9"] - S13) & MASK) - C["k1"], 16) ^ C["k2"]) - C["k3"]
    w2 &= MASK
    K0b = E.rol(C["S4"], 7) ^ ((C["D2c"] - Dd) & MASK)
    w0 = (E.rol((E.rol(K0b, 12) ^ C["q0"]) - C["q1"], 16) ^ C["q2"]) - C["q3"]
    w0 &= MASK
    X0 = (P - C["X4"] - w2) & MASK
    X10 = (C["S10"] + (E.rol(X15, 8) ^ X0) + X15) & MASK
    A = (X2 + Q + C["w7"]) & MASK
    d1 = E.ror(C["X14"] ^ A, 16)
    b1 = E.ror(Q ^ ((X10 + d1) & MASK), 12)
    Y14 = E.ror(d1 ^ ((A + b1 + w0) & MASK), 8)
    return E.ror(Y14 ^ e1, 16)


def draw(rng, n, q2, k2):
    keys = "Cb Cc Cd w6 S6 X4 S10 w7 X14 k0 X13 S9 D2c S4 S7".split()
    C = {k: u(rng, n) for k in keys}
    e1 = (u(rng, n) & np.uint32(~E.CLASS["C13"][0] & 0xFFFFFFFF)) | np.uint32(E.CLASS["C13"][1])
    X2 = u(rng, n)
    C["k1"], C["k2"], C["k3"] = E.IV1, u32(k2), u32(int(E.IV1) + int(E.IV5))
    C["q0"], C["q1"], C["q2"], C["q3"] = E.IV4, E.IV0, u32(q2), u32(int(E.IV0) + int(E.IV4))
    return C, e1, X2


def flips():
    out = [("e%d" % i, np.uint32(1 << i), None) for i in E.free_bits("C13")]
    out += [("x%d" % i, None, np.uint32(1 << i)) for i in range(32)]
    return out


def measure(q2, k2, lg, seed):
    rng = np.random.default_rng(seed)
    n = 1 << lg
    C, e1, X2 = draw(rng, n, q2, k2)
    base = E.passes(h1_hand(C, e1, X2), "H4")
    idx = np.flatnonzero(base)
    Cs = {k: (v[idx] if isinstance(v, np.ndarray) else v) for k, v in C.items()}
    e1s, X2s = e1[idx], X2[idx]
    co = {}
    for nm, em, xm in flips():
        hp = h1_hand(Cs, e1s ^ em if em is not None else e1s, X2s ^ xm if xm is not None else X2s)
        co[nm] = float(E.passes(hp, "H4").sum()) / len(idx)
    return len(idx) / n, co


if __name__ == "__main__":
    lg = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    rr = np.random.default_rng(99)
    cases = [("t=0 (filed)", 0, 0), ("t=0 again (noise)", 0, 0), ("t_lo=1", 1, 0), ("t_lo=2", 2, 0),
             ("t_lo=0x10", 0x10, 0), ("t_lo=0x8000", 0x8000, 0)]
    cases += [("t_lo=rand20 %05x" % v, int(v), 0) for v in rr.integers(1, 1 << 20, 6)]
    cases += [("t_lo=rand32 %08x" % v, int(v), 0) for v in rr.integers(1, 1 << 32, 4, dtype=np.uint64)]
    cases += [("t_hi=1 (t>=2^32)", 0, 1), ("t_hi=rand19", int(rr.integers(1, 1 << 19)), int(rr.integers(1, 1 << 19)))]
    focus = ["e14", "e30", "e31", "x30", "x31", "x14"]
    print(f"# FIX7 hand model, 2^{lg} samples per case; base seed {seed} (+i per case except the noise twin)")
    for i, (name, q2, k2) in enumerate(cases):
        s = seed if i <= 1 else seed + i
        if i == 1:
            s = seed + 1000
        p0, co = measure(q2, k2, lg, s)
        xm = np.mean([co[k] for k in co if k[0] == "x"]); em = np.mean([co[k] for k in co if k[0] == "e"])
        top = sorted(co.values(), reverse=True)
        print(f"{name:24s} q2={q2:08x} k2={k2:05x} p0*16={p0*16:.4f} | " +
              " ".join("%s %.4f" % (k, co[k]) for k in focus) +
              f" | mean x {xm:.4f} mean e {em:.4f} | sum top8 {sum(top[:8]):.3f}", flush=True)
