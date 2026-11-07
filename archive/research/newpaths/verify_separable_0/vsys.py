"""verify_separable_0: independent rebuild of the 'fixed' guess-and-determine system from the brief's spec,
comparison with separable/sys_fixed_plain.txt, and a numeric check of every equation on real 2-round BLAKE3.
Writes vsys_fixed.txt (format: "N E", N names, E lines "name k idx..").
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
import sys

IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
MSCHED1 = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]   # m' of round 1 (from the brief)
M32 = 0xFFFFFFFF


def rotr(z, r):
    return ((z >> r) | (z << (32 - r))) & M32


# ---- symbolic system, written from the brief (not from gd_order.py) ----
def system():
    st = [f"init{i}" for i in range(16)]
    eqs = []   # (name, kind, out, ins)   kind: add3 a1=a+b+x, add2 c1=c+d1, xr(r) d1=rotr(d^a1,r)
    calls = []

    def g(nm, ia, ib, ic, id_, x, y):
        a, b, c, d = st[ia], st[ib], st[ic], st[id_]
        n = lambda t: f"{nm}.{t}"
        eqs.append((nm + ":a1", "add3", n("a1"), (a, b, x)))
        eqs.append((nm + ":d1", "xr16", n("d1"), (d, n("a1"))))
        eqs.append((nm + ":c1", "add2", n("c1"), (c, n("d1"))))
        eqs.append((nm + ":b1", "xr12", n("b1"), (b, n("c1"))))
        eqs.append((nm + ":a2", "add3", n("a2"), (n("a1"), n("b1"), y)))
        eqs.append((nm + ":d2", "xr8", n("d2"), (n("d1"), n("a2"))))
        eqs.append((nm + ":c2", "add2", n("c2"), (n("c1"), n("d2"))))
        eqs.append((nm + ":b2", "xr7", n("b2"), (n("b1"), n("c2"))))
        st[ia], st[ib], st[ic], st[id_] = n("a2"), n("b2"), n("c2"), n("d2")
        calls.append((nm, (ia, ib, ic, id_), x, y))

    m = [f"m{i}" for i in range(16)]
    # round 0 columns K0..K3, diagonals D0..D3 (brief)
    g("K0", 0, 4, 8, 12, m[0], m[1]); g("K1", 1, 5, 9, 13, m[2], m[3])
    g("K2", 2, 6, 10, 14, m[4], m[5]); g("K3", 3, 7, 11, 15, m[6], m[7])
    g("D0", 0, 5, 10, 15, m[8], m[9]); g("D1", 1, 6, 11, 12, m[10], m[11])
    g("D2", 2, 7, 8, 13, m[12], m[13]); g("D3", 3, 4, 9, 14, m[14], m[15])
    mp = [m[i] for i in MSCHED1]
    g("C0", 0, 4, 8, 12, mp[0], mp[1]); g("C1", 1, 5, 9, 13, mp[2], mp[3])
    g("C2", 2, 6, 10, 14, mp[4], mp[5]); g("C3", 3, 7, 11, 15, mp[6], mp[7])
    Y = list(st)
    const = {f"init{i}" for i in range(16)} | {"m1", "m11", "m9", "m14"} | {Y[i] for i in (0, 5, 10, 15, 2, 7, 8, 13)}
    return eqs, const, Y


def trace(msg):
    v = IV[:] + IV[:4] + [0, 0, 64, 11]
    val = {f"init{i}": v[i] for i in range(16)}
    for i in range(16):
        val[f"m{i}"] = msg[i]

    def g(nm, ia, ib, ic, id_, x, y):
        a, b, c, d = v[ia], v[ib], v[ic], v[id_]
        a = (a + b + x) & M32; val[nm + ".a1"] = a
        d = rotr(d ^ a, 16); val[nm + ".d1"] = d
        c = (c + d) & M32; val[nm + ".c1"] = c
        b = rotr(b ^ c, 12); val[nm + ".b1"] = b
        a = (a + b + y) & M32; val[nm + ".a2"] = a
        d = rotr(d ^ a, 8); val[nm + ".d2"] = d
        c = (c + d) & M32; val[nm + ".c2"] = c
        b = rotr(b ^ c, 7); val[nm + ".b2"] = b
        v[ia], v[ib], v[ic], v[id_] = a, b, c, d

    m = msg
    g("K0", 0, 4, 8, 12, m[0], m[1]); g("K1", 1, 5, 9, 13, m[2], m[3])
    g("K2", 2, 6, 10, 14, m[4], m[5]); g("K3", 3, 7, 11, 15, m[6], m[7])
    g("D0", 0, 5, 10, 15, m[8], m[9]); g("D1", 1, 6, 11, 12, m[10], m[11])
    g("D2", 2, 7, 8, 13, m[12], m[13]); g("D3", 3, 4, 9, 14, m[14], m[15])
    mp = [m[i] for i in MSCHED1]
    g("C0", 0, 4, 8, 12, mp[0], mp[1]); g("C1", 1, 5, 9, 13, mp[2], mp[3])
    g("C2", 2, 6, 10, 14, mp[4], mp[5]); g("C3", 3, 7, 11, 15, mp[6], mp[7])
    g("E0", 0, 5, 10, 15, mp[8], mp[9]); g("E1", 1, 6, 11, 12, mp[10], mp[11])
    g("E2", 2, 7, 8, 13, mp[12], mp[13]); g("E3", 3, 4, 9, 14, mp[14], mp[15])
    return val, [v[i] ^ v[i + 8] for i in range(8)]


def check_eq(kind, out, ins, val):
    if kind == "add3":
        return val[out] == (val[ins[0]] + val[ins[1]] + val[ins[2]]) & M32
    if kind == "add2":
        return val[out] == (val[ins[0]] + val[ins[1]]) & M32
    r = int(kind[2:])
    return val[out] == rotr(val[ins[0]] ^ val[ins[1]], r)


def main():
    eqs, const, Y = system()
    words = sorted({w for e in eqs for w in (e[2],) + e[3]} - const)
    print("COMPUTED independent rebuild: unknown words", len(words), "equations", len(eqs), "F", len(words) - len(eqs))
    # compare with separable's export
    sep = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/separable/sys_fixed_plain.txt')
    L = open(sep).read().split("\n")
    N, E = int(L[0].split()[0]), int(L[0].split()[1])
    names = L[1:1 + N]
    sepeqs = {}
    for line in L[1 + N:1 + N + E]:
        p = line.split()
        sepeqs[p[0]] = frozenset(names[int(i)] for i in p[2:])
    mine = {e[0]: frozenset(w for w in (e[2],) + e[3] if w not in const) for e in eqs}
    same = set(names) == set(words) and sepeqs == mine
    print("COMPUTED separable sys_fixed_plain.txt identical to independent rebuild (words and equation supports):", same)
    if not same:
        print(" diff words", set(names) ^ set(words))
        for k in set(sepeqs) | set(mine):
            if sepeqs.get(k) != mine.get(k):
                print(" diff", k, sepeqs.get(k), mine.get(k))
    # numeric check on real 2-round BLAKE3 (w = 32), and against Grok's job28 reference compress
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job28_newpaths'))
    try:
        import job28
        ref = lambda msg: job28.compress(msg, 32, (16, 12, 8, 7))
    except Exception as ex:  # noqa: BLE001
        print("job28 import failed:", ex)
        ref = None
    rng = random.Random(7)
    bad = 0
    refbad = 0
    for _ in range(2000):
        msg = [rng.getrandbits(32) for _ in range(16)]
        val, out = trace(msg)
        for nm, kind, o, ins in eqs:
            if not check_eq(kind, o, ins, val):
                bad += 1
        if ref and ref(msg) != out:
            refbad += 1
        # structural fact: out0,2,5,7 from E0,E2
        assert out[0] == val["E0.a2"] ^ val["E2.c2"] and out[2] == val["E2.a2"] ^ val["E0.c2"]
        assert out[5] == val["E0.b2"] ^ val["E2.d2"] and out[7] == val["E2.b2"] ^ val["E0.d2"]
    print("COMPUTED 2000 random messages: equation failures", bad, "; mismatches vs job28.compress", refbad,
          "; out0/2/5/7 = E0/E2 identities held")
    idx = {w: i for i, w in enumerate(words)}
    with open(_hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/verify_separable_0/vsys_fixed.txt'), "w") as fh:
        fh.write(f"{len(words)} {len(eqs)}\n")
        for w in words:
            fh.write(w + "\n")
        for nm, kind, o, ins in eqs:
            ws = [idx[w] for w in (o,) + ins if w not in const]
            fh.write(f"{nm} {len(ws)} " + " ".join(map(str, ws)) + "\n")
    sizes = {}
    for nm, kind, o, ins in eqs:
        k = len([w for w in (o,) + ins if w not in const])
        sizes[k] = sizes.get(k, 0) + 1
    print("COMPUTED unknowns per equation histogram:", dict(sorted(sizes.items())))


if __name__ == "__main__":
    main()
