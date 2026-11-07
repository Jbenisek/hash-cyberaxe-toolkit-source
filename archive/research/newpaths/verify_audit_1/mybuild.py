"""Independent builder for the 'fixed' variant word-equation system (verify_audit_1).
Written from the brief, not from gd_order.py.  Also: BLAKE3 reference check (7-round empty-input digest),
numeric check that every equation holds on real 2-round computations, and comparison with the audit's
rules_fixed_len64_plain.txt.  Usage: python mybuild.py
"""
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
M32 = 0xFFFFFFFF
IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]


def rotr(x, r):
    return ((x >> r) | (x << (32 - r))) & M32


def G(v, a, b, c, d, x, y, trace=None):
    a1 = (v[a] + v[b] + x) & M32
    d1 = rotr(v[d] ^ a1, 16)
    c1 = (v[c] + d1) & M32
    b1 = rotr(v[b] ^ c1, 12)
    a2 = (a1 + b1 + y) & M32
    d2 = rotr(d1 ^ a2, 8)
    c2 = (c1 + d2) & M32
    b2 = rotr(b1 ^ c2, 7)
    if trace is not None:
        trace.append(dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2))
    v[a], v[b], v[c], v[d] = a2, b2, c2, d2


def compress(m, rounds, blen=64, flags=11, cv=IV, counter=0, trace=None):
    v = list(cv) + IV[:4] + [counter & M32, counter >> 32, blen, flags]
    s = list(m)
    for r in range(rounds):
        G(v, 0, 4, 8, 12, s[0], s[1], trace); G(v, 1, 5, 9, 13, s[2], s[3], trace)
        G(v, 2, 6, 10, 14, s[4], s[5], trace); G(v, 3, 7, 11, 15, s[6], s[7], trace)
        G(v, 0, 5, 10, 15, s[8], s[9], trace); G(v, 1, 6, 11, 12, s[10], s[11], trace)
        G(v, 2, 7, 8, 13, s[12], s[13], trace); G(v, 3, 4, 9, 14, s[14], s[15], trace)
        s = [s[p] for p in PERM]
    return v


def ref_check():
    v = compress([0] * 16, 7, blen=0, flags=1 | 2 | 8)
    out = [v[i] ^ v[i + 8] for i in range(8)]
    h = b"".join(w.to_bytes(4, "little") for w in out).hex()
    return h == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262", h


# ---- symbolic system -------------------------------------------------------------------------------------
NAMES_R0 = ["K0", "K1", "K2", "K3", "D0", "D1", "D2", "D3"]
NAMES_R1 = ["C0", "C1", "C2", "C3"]          # fixed variant: round-1 diagonals not modelled (E0,E2 inputs fixed)
IDX = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
       (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def build_fixed():
    """Return (eqs, consts, unknowns).  eqs: list of (label, tuple of word names)."""
    state = [f"init{i}" for i in range(16)]
    consts = set(state)
    msg = [f"m{i}" for i in range(16)]
    eqs = []

    def g(name, idx, x, y):
        a, b, c, d = (state[i] for i in idx)
        w = {t: f"{name}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2")}
        eqs.append((name + ":a1", (w["a1"], a, b, x)))
        eqs.append((name + ":d1", (w["d1"], d, w["a1"])))
        eqs.append((name + ":c1", (w["c1"], c, w["d1"])))
        eqs.append((name + ":b1", (w["b1"], b, w["c1"])))
        eqs.append((name + ":a2", (w["a2"], w["a1"], w["b1"], y)))
        eqs.append((name + ":d2", (w["d2"], w["d1"], w["a2"])))
        eqs.append((name + ":c2", (w["c2"], w["c1"], w["d2"])))
        eqs.append((name + ":b2", (w["b2"], w["b1"], w["c2"])))
        for i, t in zip(idx, ("a2", "b2", "c2", "d2")):
            state[i] = w[t]

    s = msg
    for j in range(8):
        g(NAMES_R0[j], IDX[j], s[2 * j], s[2 * j + 1])
    s = [s[p] for p in PERM]
    for j in range(4):
        g(NAMES_R1[j], IDX[j], s[2 * j], s[2 * j + 1])
    Y = list(state)
    # E0 = G(Y0,Y5,Y10,Y15; m'8, m'9), E2 = G(Y2,Y7,Y8,Y13; m'12, m'13) -> fixed inputs
    consts.update(Y[i] for i in (0, 5, 10, 15, 2, 7, 8, 13))
    consts.update([s[8], s[9], s[12], s[13]])
    allw = {w for _, ws in eqs for w in ws}
    unknowns = sorted(allw - consts)
    return eqs, consts, unknowns, s


def numeric_check(eqs, trials=200):
    """Evaluate real 2-round computations and confirm each equation's relation holds, by recomputing it."""
    rng = random.Random(5)
    bad = 0
    for _ in range(trials):
        m = [rng.getrandbits(32) for _ in range(16)]
        tr = []
        compress(m, 2, trace=tr)
        val = {f"m{i}": m[i] for i in range(16)}
        init = list(IV) + IV[:4] + [0, 0, 64, 11]
        for i in range(16):
            val[f"init{i}"] = init[i]
        names = NAMES_R0 + NAMES_R1
        for k, nm in enumerate(names):
            for t, x in tr[k].items():
                val[f"{nm}.{t}"] = x
        for lab, ws in eqs:
            kind = lab.split(":")[1]
            v = [val[w] for w in ws]
            if kind in ("a1", "a2"):
                ok = v[0] == (v[1] + v[2] + v[3]) & M32
            elif kind == "c1" or kind == "c2":
                ok = v[0] == (v[1] + v[2]) & M32
            else:
                r = {"d1": 16, "b1": 12, "d2": 8, "b2": 7}[kind]
                ok = v[0] == rotr(v[1] ^ v[2], r)
            bad += not ok
    return bad


def main():
    ok, h = ref_check()
    print(f"COMPUTED reference 7-round empty-input digest match: {ok} ({h})")
    eqs, consts, unk, sfin = build_fixed()
    print(f"COMPUTED fixed len64: unknowns={len(unk)} equations={len(eqs)} freedom={len(unk) - len(eqs)}")
    print(f"  round-1 message order m' = {['m%s' % x[1:] for x in sfin]}  (E0 msgs {sfin[8]},{sfin[9]}; E2 msgs {sfin[12]},{sfin[13]})")
    print(f"  non-init constants: {sorted(c for c in consts if not c.startswith('init'))}")
    print(f"COMPUTED numeric equation failures over 200 random messages: {numeric_check(eqs)}")
    # compare with audit rules file
    fn = os.path.join(HERE, "..", "audit", "rules_fixed_len64_plain.txt")
    with open(fn) as fh:
        nv, ne, nr = map(int, fh.readline().split())
        names = fh.readline().split()
        theirs = set()
        for _ in range(ne):
            theirs.add(frozenset(names[int(x)] for x in fh.readline().split()))
    mine = set()
    for _, ws in eqs:
        mine.add(frozenset(w for w in ws if w not in consts))
    print(f"COMPUTED audit file: nv={nv} ne={ne} nr={nr}; same unknown set: {set(names) == set(unk)}; "
          f"same equation multiset: {mine == theirs and len(mine) == ne}")
    # write my own system file in the same text format for my own solver
    ix = {v: i for i, v in enumerate(unk)}
    with open(os.path.join(HERE, "sys_fixed_plain.txt"), "w") as fh:
        fh.write(f"{len(unk)} {len(eqs)} 0\n" + " ".join(unk) + "\n")
        for _, ws in eqs:
            fh.write(" ".join(str(ix[w]) for w in ws if w not in consts) + "\n")
    print("wrote sys_fixed_plain.txt")


if __name__ == "__main__":
    main()
