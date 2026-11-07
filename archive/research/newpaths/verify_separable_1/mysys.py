"""verify_separable_1/mysys.py - independent rebuild of the guess-and-determine system (no import of gd_order).

1. Build the fixed / outhalf systems myself from the BLAKE3 spec in the brief.
2. Evaluate 2-round BLAKE3 numerically (32-bit) on random messages and check that every primitive equation
   holds with the computed word values (catches mis-wiring), and that out0,2,5,7 = E0/E2 words as stated.
3. Compare my equation sets with separable/sys_<variant>_plain.txt (word names, nonconstant words per equation).
4. Write my own system files (same plain format) for vs.c.
Usage: python mysys.py
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

import random

IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
MASK = 0xFFFFFFFF
SEP = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/separable')
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/verify_separable_1')


def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & MASK


def system(variant, msg=None):
    """Return (eqs, const, words, val). eqs: list of (name, kind, tuple of word names); val: numeric values if msg."""
    val = {}
    st = [f"iv{i}" for i in range(16)]
    init = IV + IV[:4] + [0, 0, 64, 11]
    for i in range(16):
        val[st[i]] = init[i]
    m = [f"m{i}" for i in range(16)]
    if msg:
        for i in range(16):
            val[m[i]] = msg[i]
    eqs = []

    def g(name, idx, x, y):
        a, b, c, d = (st[i] for i in idx)
        n = {t: f"{name}.{t}" for t in ("a1", "b1", "c1", "d1", "a2", "b2", "c2", "d2")}
        # kind: add3 (t = u+v+w), xr (t = (u^v)>>>r), add2 (t = u+v)
        eqs.extend([(name + ":a1", ("add3",), (n["a1"], a, b, x)),
                    (name + ":d1", ("xr", 16), (n["d1"], d, n["a1"])),
                    (name + ":c1", ("add2",), (n["c1"], c, n["d1"])),
                    (name + ":b1", ("xr", 12), (n["b1"], b, n["c1"])),
                    (name + ":a2", ("add3",), (n["a2"], n["a1"], n["b1"], y)),
                    (name + ":d2", ("xr", 8), (n["d2"], n["d1"], n["a2"])),
                    (name + ":c2", ("add2",), (n["c2"], n["c1"], n["d2"])),
                    (name + ":b2", ("xr", 7), (n["b2"], n["b1"], n["c2"]))])
        if msg:
            A, B, C, D, X, Y = (val[w] for w in (a, b, c, d, x, y))
            A = (A + B + X) & MASK; val[n["a1"]] = A
            D = ror(D ^ A, 16); val[n["d1"]] = D
            C = (C + D) & MASK; val[n["c1"]] = C
            B = ror(B ^ C, 12); val[n["b1"]] = B
            A = (A + B + Y) & MASK; val[n["a2"]] = A
            D = ror(D ^ A, 8); val[n["d2"]] = D
            C = (C + D) & MASK; val[n["c2"]] = C
            B = ror(B ^ C, 7); val[n["b2"]] = B
        for i, v in zip(idx, (n["a2"], n["b2"], n["c2"], n["d2"])):
            st[i] = v

    s = m[:]
    for j, idx in enumerate(COLS):
        g(f"K{j}", idx, s[2 * j], s[2 * j + 1])
    for j, idx in enumerate(DIAG):
        g(f"D{j}", idx, s[8 + 2 * j], s[9 + 2 * j])
    s = [m[p] for p in PERM]
    for j, idx in enumerate(COLS):
        g(f"C{j}", idx, s[2 * j], s[2 * j + 1])
    Y = list(st)
    const = set(f"iv{i}" for i in range(16))
    if variant == "fixed":
        const |= {"m1", "m11", "m9", "m14"} | {Y[i] for i in (0, 5, 10, 15, 2, 7, 8, 13)}
        if msg:   # E0,E2 inputs must be exactly these words
            assert (s[8], s[9], s[12], s[13]) == ("m1", "m11", "m9", "m14")
    else:
        for j in (0, 2):
            g(f"E{j}", DIAG[j], s[8 + 2 * j], s[9 + 2 * j])
        for i in (0, 2, 5, 7):
            eqs.append((f"out{i}", ("xor",), (st[i], st[i + 8])))
    words = sorted({w for _, _, ws in eqs for w in ws} - const)
    return eqs, const, words, val, st, Y


def check_numeric(trials=200):
    rng = random.Random(7)
    for _ in range(trials):
        msg = [rng.getrandbits(32) for _ in range(16)]
        eqs, const, words, val, st, Y = system("outhalf", msg)
        for name, kind, ws in eqs:
            if kind[0] == "xor":
                continue
            t, *u = (val[w] for w in ws)
            if kind[0] == "add3":
                ok = t == (u[0] + u[1] + u[2]) & MASK
            elif kind[0] == "add2":
                ok = t == (u[0] + u[1]) & MASK
            else:
                ok = t == ror(u[0] ^ u[1], kind[1])
            assert ok, name
        # full 2-round output, compare with out0,2,5,7 from E0/E2 words only
        full = list(st)
        # apply E1, E3 too to get the full 2-round state
        eqs2, _, _, val2, st2, _ = system("outhalf", msg)
        s = [f"m{p}" for p in PERM]
    return True


def full_compress(msg):
    """Plain 2-round compression (independent straight-line code) -> 8 output words."""
    v = IV + IV[:4] + [0, 0, 64, 11]

    def G(a, b, c, d, x, y):
        v[a] = (v[a] + v[b] + x) & MASK; v[d] = ror(v[d] ^ v[a], 16)
        v[c] = (v[c] + v[d]) & MASK; v[b] = ror(v[b] ^ v[c], 12)
        v[a] = (v[a] + v[b] + y) & MASK; v[d] = ror(v[d] ^ v[a], 8)
        v[c] = (v[c] + v[d]) & MASK; v[b] = ror(v[b] ^ v[c], 7)
    s = list(msg)
    for r in range(2):
        for j, idx in enumerate(COLS):
            G(*idx, s[2 * j], s[2 * j + 1])
        for j, idx in enumerate(DIAG):
            G(*idx, s[8 + 2 * j], s[9 + 2 * j])
        s = [s[p] for p in PERM]
    return [v[i] ^ v[i + 8] for i in range(8)]


def check_outputs(trials=200):
    rng = random.Random(11)
    for _ in range(trials):
        msg = [rng.getrandbits(32) for _ in range(16)]
        out = full_compress(msg)
        eqs, const, words, val, st, Y = system("outhalf", msg)
        for i in (0, 2, 5, 7):
            assert out[i] == val[st[i]] ^ val[st[i + 8]], i
    return True


def load_sys(fn):
    with open(fn) as fh:
        N, E, NM, F = map(int, fh.readline().split())
        names = [fh.readline().strip() for _ in range(N)]
        eqs = {}
        for _ in range(E):
            p = fh.readline().split()
            eqs[p[0]] = frozenset(names[int(x)] for x in p[2:2 + int(p[1])])
    return N, E, F, names, eqs


def main():
    print("numeric equation check (200 random messages):", check_numeric())
    print("out0,2,5,7 from E0/E2 words == full 2-round output (200 messages):", check_outputs())
    for variant in ("fixed", "outhalf"):
        eqs, const, words, _, _, _ = system(variant)
        F = len(words) - len(eqs)
        mine = {n: frozenset(w for w in ws if w not in const) for n, _, ws in eqs}
        N, E, Ft, names, theirs = load_sys(f"{SEP}\\sys_{variant}_plain.txt")
        same = mine == theirs and sorted(names) == sorted(words)
        print(f"{variant}: mine N={len(words)} E={len(eqs)} F={F}; theirs N={N} E={E} F={Ft}; identical={same}")
        idx = {w: i for i, w in enumerate(words)}
        with open(f"{OUT}\\my_{variant}.txt", "w") as fh:
            fh.write(f"{len(words)} {len(eqs)} 0 {F}\n")
            for w in words:
                fh.write(w + "\n")
            for n, _, ws in eqs:
                nc = [idx[w] for w in ws if w not in const]
                fh.write(f"{n} {len(nc)} " + " ".join(map(str, nc)) + "\n")


if __name__ == "__main__":
    main()
