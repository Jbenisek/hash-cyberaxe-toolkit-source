"""Independent rebuild (verify_audit_0) of the 'fixed' equation system, written from the BLAKE3 spec, not from
gd_order.py.  Checks:
  1. own BLAKE3 compression, 7 rounds, empty input digest vs the published value;
  2. every primitive equation of rounds 0 + round-1 columns holds on random messages (2 rounds);
  3. the equation system (non-constant words only) equals audit/rules_fixed_len64_plain.txt as a set of word-sets;
  4. writes my own rules file sys_fixed.txt (same format as bf.c input: 'nv ne 0', names, equations).
Usage: python sys_build.py
"""
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
M32 = 0xFFFFFFFF
IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
SCHED = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]


def rotr(x, r):
    return ((x >> r) | (x << (32 - r))) & M32


def compress(m, rounds, blen=64, flags=11, trace=None):
    v = IV[:] + IV[:4] + [0, 0, blen, flags]
    msg = list(m)
    for r in range(rounds):
        calls = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                 (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
        for j, (a, b, c, d) in enumerate(calls):
            x, y = msg[2 * j], msg[2 * j + 1]
            A, B, C, D = v[a], v[b], v[c], v[d]
            a1 = (A + B + x) & M32
            d1 = rotr(D ^ a1, 16)
            c1 = (C + d1) & M32
            b1 = rotr(B ^ c1, 12)
            a2 = (a1 + b1 + y) & M32
            d2 = rotr(d1 ^ a2, 8)
            c2 = (c1 + d2) & M32
            b2 = rotr(b1 ^ c2, 7)
            if trace is not None:
                trace.append((r, j, dict(a=A, b=B, c=C, d=D, x=x, y=y, a1=a1, d1=d1, c1=c1, b1=b1,
                                         a2=a2, d2=d2, c2=c2, b2=b2)))
            v[a], v[b], v[c], v[d] = a2, b2, c2, d2
        msg = [msg[SCHED[i]] for i in range(16)]
    return [v[i] ^ v[i + 8] for i in range(8)]


def digest_empty():
    out = compress([0] * 16, 7, blen=0, flags=11)
    return b"".join(w.to_bytes(4, "little") for w in out).hex()


# ---- symbolic system: names are '<G>.<field>' with G in K0..K3 (round-0 columns), D0..D3 (round-0 diagonals),
#      C0..C3 (round-1 columns); message words 'm<i>'; initial words 'init<i>'.
def symbolic():
    st = [f"init{i}" for i in range(16)]
    msg = [f"m{i}" for i in range(16)]
    eqs = []           # (eqname, op, out, ins)   op in add3/add2/xr16/xr12/xr8/xr7
    names = {}
    for r in range(2):
        calls = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                 (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
        ncalls = 8 if r == 0 else 4         # 'fixed': round-1 diagonals are not part of the system
        for j in range(ncalls):
            a, b, c, d = calls[j]
            g = ("K" if j < 4 else "D") + str(j % 4) if r == 0 else "C" + str(j)
            names[(r, j)] = g
            x, y = msg[2 * j], msg[2 * j + 1]
            A, B, C, D = st[a], st[b], st[c], st[d]
            w = {t: f"{g}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2")}
            eqs += [(g + ":a1", "add3", w["a1"], (A, B, x)), (g + ":d1", "xr16", w["d1"], (D, w["a1"])),
                    (g + ":c1", "add2", w["c1"], (C, w["d1"])), (g + ":b1", "xr12", w["b1"], (B, w["c1"])),
                    (g + ":a2", "add3", w["a2"], (w["a1"], w["b1"], y)), (g + ":d2", "xr8", w["d2"], (w["d1"], w["a2"])),
                    (g + ":c2", "add2", w["c2"], (w["c1"], w["d2"])), (g + ":b2", "xr7", w["b2"], (w["b1"], w["c2"]))]
            st[a], st[b], st[c], st[d] = w["a2"], w["b2"], w["c2"], w["d2"]
        if r == 0:
            msg = [msg[SCHED[i]] for i in range(16)]
    Y = st                                   # state after round-1 columns
    const = {f"init{i}" for i in range(16)} | {"m1", "m11", "m9", "m14"} | {Y[i] for i in (0, 5, 10, 15, 2, 7, 8, 13)}
    return eqs, const, names, Y


def check_numeric(eqs, names, trials=300):
    rng = random.Random(20261008)
    bad = 0
    for _ in range(trials):
        m = [rng.getrandbits(32) for _ in range(16)]
        tr = []
        compress(m, 2, trace=tr)
        val = {f"init{i}": w for i, w in enumerate(IV[:] + IV[:4] + [0, 0, 64, 11])}
        val.update({f"m{i}": m[i] for i in range(16)})
        for r, j, d in tr:
            if (r, j) not in names:
                continue
            g = names[(r, j)]
            for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"):
                val[f"{g}.{t}"] = d[t]
        for nm, op, o, ins in eqs:
            iv = [val[i] for i in ins]
            if op == "add3":
                ok = val[o] == (iv[0] + iv[1] + iv[2]) & M32
            elif op == "add2":
                ok = val[o] == (iv[0] + iv[1]) & M32
            else:
                ok = val[o] == rotr(iv[0] ^ iv[1], int(op[2:]))
            bad += not ok
    return bad


def main():
    dg = digest_empty()
    exp = "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    print("BLAKE3('') own ref 7 rounds:", dg, "MATCH" if dg == exp else "MISMATCH")
    eqs, const, names, Y = symbolic()
    print("Y constants:", [Y[i] for i in (0, 5, 10, 15, 2, 7, 8, 13)])
    print("numeric equation failures over 300 random messages:", check_numeric(eqs, names))
    ncq = [frozenset(v for v in (o,) + ins if v not in const) for _, _, o, ins in eqs]
    vars_ = sorted({v for s in ncq for v in s})
    print(f"own system: {len(vars_)} unknown words, {len(ncq)} equations, freedom {len(vars_) - len(ncq)}")
    # compare with audit's rules file
    fn = os.path.join(HERE, "..", "audit", "rules_fixed_len64_plain.txt")
    with open(fn) as fh:
        nv, ne, nr = map(int, fh.readline().split())
        an = fh.readline().split()
        aeq = [frozenset(an[int(t)] for t in fh.readline().split()) for _ in range(ne)]
    print("audit rules file: same variable set:", set(an) == set(vars_),
          "; same equation multiset:", sorted(map(sorted, aeq)) == sorted(map(sorted, ncq)))
    ix = {v: i for i, v in enumerate(vars_)}
    with open(os.path.join(HERE, "sys_fixed.txt"), "w") as fh:
        fh.write(f"{len(vars_)} {len(ncq)} 0\n" + " ".join(vars_) + "\n")
        for s in ncq:
            fh.write(" ".join(str(ix[v]) for v in sorted(s)) + "\n")
    print("wrote sys_fixed.txt")


if __name__ == "__main__":
    main()
