"""Independent re-measurement for the upfront-G50-Y1 refutation.

Independent of screen_ck2.py: step CO is evaluated by a numpy interpreter of outer.py's own LINES (not
F.compile_lines), the T1/T2 automata come from outer.build_tables() (not F.F1/F.F2), the cluster gate is F.gate()
itself tabled over all 2^21 entries (not the S7 re-expression), contexts are drawn from fresh seeds with a different
rng recipe, and the pilot list is a fresh 1024-member list. Cross-checks against outer.scalar_outer and F.T1/F.T2
and against F.rebuild on random members.

Per context (whole 2^19 class): opened reps, E lanes (T2 hits in opened clusters), all T2 hits, passes, calls
(T-nonzero, nu rule of F.nu_of), fills (rep batches + 5 partner batches of opened clusters with an E lane), pilot
(T2 hits on the 1024 fixed pilot members), and the histogram of T over calls.
usage: python indep.py SEED CTX
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

import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import outer as O  # noqa: E402
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
import frontline_full as F  # noqa: E402  (gate(), VMASK, rebuild for cross-check, ledger constants only)

M = 0xFFFFFFFF
TWO32 = np.uint64(1 << 32)
SEED, CTX = int(sys.argv[1]), int(sys.argv[2])


def is_arr(x):
    return isinstance(x, np.ndarray)


def ror(x, r):
    if is_arr(x):
        x = x & np.uint64(M)
        return ((x >> np.uint64(r)) | (x << np.uint64(32 - r))) & np.uint64(M)
    return ((x >> r) | (x << (32 - r))) & M


def nev(e, v):
    if isinstance(e, int):
        return e
    if isinstance(e, str):
        return v[e]
    k = e[0]
    if k == "sum":
        terms = []
        for t in e[1]:
            if isinstance(t, tuple) and t[0] == "neg":
                x = nev(t[1], v)
                terms.append((TWO32 - (x & np.uint64(M))) if is_arr(x) else ((1 << 32) - (x & M)))
            else:
                terms.append(nev(t, v))
        if any(is_arr(t) for t in terms):
            s = np.zeros(1, dtype=np.uint64)
            for t in terms:
                s = s + (t if is_arr(t) else np.uint64(t))
            return s & np.uint64(M)
        return sum(terms) & M
    if k == "xor":
        a, b = nev(e[1], v), nev(e[2], v)
        if is_arr(a) or is_arr(b):
            return (a if is_arr(a) else np.uint64(a)) ^ (b if is_arr(b) else np.uint64(b))
        return a ^ b
    if k == "ror":
        return ror(nev(e[1], v), e[2])
    raise ValueError(k)


def step_co(ow, Y4):
    v = dict(zip(O.OUTER_WORDS, ow))
    v["Y4"] = Y4
    for name, e in O.LINES:
        v[name] = nev(e, v)
    return v


_, T1T, T2T = O.build_tables()
T1A = [np.array(t, dtype=np.int64) for t in T1T]
T2A = [np.array(t, dtype=np.int64) for t in T2T]


def look(tabs, x):
    x = x.astype(np.int64)
    s = tabs[0][x & 255]
    s = tabs[1][s + (x >> 8 & 255)]
    s = tabs[2][s + (x >> 16 & 255)]
    return tabs[3][s + (x >> 24 & 255)]


# members: bit n of member number k -> free bit CLASS_FREE[n]
KK = np.arange(1 << 19, dtype=np.int64)
E1 = np.full(1 << 19, O.CLASS_VALUE, dtype=np.uint64)
for n, b in enumerate(O.CLASS_FREE):
    E1 |= ((KK >> n) & 1).astype(np.uint64) << np.uint64(b)
YY = (E1 + TWO32 - np.uint64(O.Y3)) & np.uint64(M)

# the real gate, tabled
GT = np.array([F.gate(i) for i in range(1 << 21)], dtype=np.bool_)
VM = np.array(F.VMASK, dtype=np.int64)

# cluster index layout k = g&63 | j<<6 | (g>>6)<<11  -> reshape(256, 32, 64)[g>>6, j, g&63]
G = np.arange(1 << 14, dtype=np.int64)
KREP = (G & 63) | ((G >> 6) << 11)

rng = random.Random(SEED * 7919 + 13)
pilot = np.array(sorted(rng.sample(range(1 << 19), 1024)), dtype=np.int64)

chk = dict(scalar_n=0, scalar_mm=0, t_n=0, t_mm=0, fl_n=0, fl_mm=0)
rows = []
t0 = time.time()
for c in range(CTX):
    ow = [rng.getrandbits(32) for _ in range(7)]
    v = step_co(ow, YY)
    om = (np.uint64(O.Y3) + YY + v["w8"]) & np.uint64(M)
    Y9 = v["Y9"]
    m2 = look(T2A, om)
    m1 = look(T1A, Y9)
    x = m1 & m2
    Q = Y9.astype(np.int64)
    e1i = E1.astype(np.int64)
    r = (((Q >> 16) ^ e1i) & 4) ^ 7
    C2c = v["C2.c1"].astype(np.int64)
    C2b = v["C2.b1"].astype(np.int64)
    nu = ((((r + C2c) & M) ^ C2b) ^ 1) & 7
    T = x & VM[nu]

    # cross-checks on random members against outer.scalar_outer, F.rebuild and F.T1/F.T2
    rs = random.Random(SEED * 100003 + c)
    for _ in range(8):
        kk = rs.randrange(1 << 19)
        w = 0
        for n, b in enumerate(O.CLASS_FREE):
            if kk >> n & 1:
                w |= 1 << b
        sv = O.scalar_outer(list(ow) + [w])
        fv = F.rebuild(tuple(ow), int(YY[kk]), int(E1[kk]))
        chk["scalar_n"] += 1
        chk["scalar_mm"] += (sv["omega"], sv["Y9"], sv["Y0"], sv["C2.c1"], sv["C2.b1"]) != (
            int(om[kk]), int(Y9[kk]), int(v["Y0"][kk]), int(v["C2.c1"][kk]), int(v["C2.b1"][kk]))
        chk["fl_n"] += 1
        chk["fl_mm"] += (fv["omega"], fv["Y9"]) != (int(om[kk]), int(Y9[kk]))
        chk["t_n"] += 1
        chk["t_mm"] += (F.T2(int(om[kk])), F.T1(int(Y9[kk]))) != (int(m2[kk]), int(m1[kk]))

    # gate key as walk() builds it: a = (Y0>>16 & 127) + nA, c = (e1 + P[15]) & 127, q = (rol(X15,24)^S15) & 127
    Acx = (v["C0.b1"] + v["w6"] + v["X4"] + v["w2"]) & M
    nA = (-(Acx >> 16)) & 127
    P15 = (-(v["S0"] + v["S5"])) & M
    q = (O.rol(O.X15, 24) ^ v["S15"]) & 127
    Y0r = v["Y0"][KREP].astype(np.int64)
    a = ((Y0r >> 16 & 127) + nA) & 127
    cc = (e1i[KREP] + P15) & 127
    opened = GT[(q << 14) | (cc << 7) | a]

    E3 = (m2 != 0).reshape(256, 32, 64).transpose(0, 2, 1).reshape(1 << 14, 32)   # [g, j]
    X3 = (x != 0).reshape(256, 32, 64).transpose(0, 2, 1).reshape(1 << 14, 32)
    T3 = (T != 0).reshape(256, 32, 64).transpose(0, 2, 1).reshape(1 << 14, 32)
    e_lanes = int(E3[opened].sum())
    passes_open = int(X3[opened].sum())
    calls_open = int(T3[opened].sum())
    closed_hits = int(E3[~opened].sum())
    # fills: representative batches (7 reps; last of 4) with an opened rep having an E lane
    repE = np.zeros(2341 * 7, dtype=bool)
    repE[:1 << 14] = E3[:, 0] & opened
    f_rep = int(repE.reshape(2341, 7).any(axis=1).sum())
    f_part = 0
    for lo in (1, 8, 15, 22, 29):
        hi = min(lo + 7, 32)
        f_part += int((E3[:, lo:hi].any(axis=1) & opened).sum())
    Tvals = T[T != 0]
    hist = np.bincount(Tvals, minlength=128).tolist()
    row = dict(c=c, ow=ow, opened=int(opened.sum()), e_lanes=e_lanes, hits=int((m2 != 0).sum()),
               passes=int((x != 0).sum()), passes_open=passes_open, calls=int((T != 0).sum()), calls_open=calls_open,
               closed_hits=closed_hits, fills=f_rep + f_part, pilot=int((m2[pilot] != 0).sum()),
               pilot_pass=int((x[pilot] != 0).sum()), Thist=hist)
    rows.append(row)
    if c % 64 == 0 or c == CTX - 1:
        print("c", c, "opened", row["opened"], "hits", row["hits"], "passes", row["passes"], "calls", row["calls"],
              "fills", row["fills"], "pilot", row["pilot"], "sec", round(time.time() - t0, 1), flush=True)

print("checks", chk)
print("sec", round(time.time() - t0, 1))
with open(os.path.join(HERE, "irows_s%d.json" % SEED), "w") as fh:
    json.dump(dict(seed=SEED, ctx=CTX, checks=chk, pilot=pilot.tolist(), rows=rows), fh)
