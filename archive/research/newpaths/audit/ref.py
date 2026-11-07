"""Audit reference: 2-round BLAKE3 compression (single block) at word width w, written from the spec,
recording every internal word under gd_order.py's naming (initN, mN, K0..K3, D0..D3, C0..C3, E0..E3 with
.a1 .d1 .c1 .b1 .a2 .d2 .c2 .b2).  Toy rotations floor(r*w/32) of (16,12,8,7).
Run directly: cross-checks against BLAKE3("") (7 rounds) and against Grok's job28.py (read only, no .pyc written).
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

sys.dont_write_bytecode = True

IV32 = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def rots(w):
    return tuple((r * w) // 32 for r in (16, 12, 8, 7))


def ror(z, r, w):
    m = (1 << w) - 1
    z &= m
    r %= w
    return ((z >> r) | (z << (w - r))) & m if r else z


def rol(z, r, w):
    return ror(z, (w - r % w) % w, w)


def init_state(w, blen=64, flags=11):
    m = (1 << w) - 1
    iv = [x & m for x in IV32]
    return iv[:8] + iv[:4] + [0, 0, blen & m, flags & m]


def trace(msg, w=32, blen=64, flags=11, rounds=2):
    """Returns (vals, Y, out): vals maps gd_order names -> value; Y = state after round-1 columns."""
    m = (1 << w) - 1
    R = rots(w)
    v = init_state(w, blen, flags)
    vals = {f"init{i}": v[i] for i in range(16)}
    vals.update({f"m{i}": msg[i] & m for i in range(16)})
    Y = None
    sched = list(range(16))
    for r in range(rounds):
        s = [msg[sched[i]] & m for i in range(16)]
        names = ("K", "D") if r == 0 else ("C", "E") if r == 1 else (f"R{r}c", f"R{r}d")
        for half, idxs, off in ((0, COLS, 0), (1, DIAG, 8)):
            for j, (ia, ib, ic, id_) in enumerate(idxs):
                a, b, c, d = v[ia], v[ib], v[ic], v[id_]
                x, y = s[off + 2 * j], s[off + 2 * j + 1]
                a1 = (a + b + x) & m
                d1 = ror(d ^ a1, R[0], w)
                c1 = (c + d1) & m
                b1 = ror(b ^ c1, R[1], w)
                a2 = (a1 + b1 + y) & m
                d2 = ror(d1 ^ a2, R[2], w)
                c2 = (c1 + d2) & m
                b2 = ror(b1 ^ c2, R[3], w)
                nm = f"{names[half]}{j}"
                for t, val in (("a1", a1), ("d1", d1), ("c1", c1), ("b1", b1),
                               ("a2", a2), ("d2", d2), ("c2", c2), ("b2", b2)):
                    vals[f"{nm}.{t}"] = val
                v[ia], v[ib], v[ic], v[id_] = a2, b2, c2, d2
            if r == 1 and half == 0:
                Y = list(v)
        sched = [sched[p] for p in PERM]
    out = [v[i] ^ v[i + 8] for i in range(8)]
    return vals, Y, out


def blake3_empty():
    _, _, out = trace([0] * 16, 32, blen=0, flags=11, rounds=7)
    return b"".join(x.to_bytes(4, "little") for x in out).hex()


def main():
    ok = True
    h = blake3_empty()
    exp = "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    print("BLAKE3('') via ref, 7 rounds:", h, "MATCH" if h == exp else "MISMATCH")
    ok &= h == exp
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job28_newpaths'))
    import job28
    rng = random.Random(2026)
    for w in (32, 16, 8):
        n = 2000 if w == 32 else 500
        bad = 0
        for _ in range(n):
            msg = [rng.getrandbits(w) for _ in range(16)]
            blen = job28.block_len(w)
            vals, Y, out = trace(msg, w, blen=blen)
            o2 = job28.compress(msg, w, job28.primary_rots(w), b=blen)
            tr = job28.compress_trace(msg, w, job28.primary_rots(w), b=blen)
            if out != o2 or out != tr["out"] or Y != tr["Y"]:
                bad += 1
        print(f"w={w}: {n} random messages, ref vs job28 compress/compress_trace (out and Y): {bad} mismatches")
        ok &= bad == 0
    print("ALL OK" if ok else "FAILURES")


if __name__ == "__main__":
    main()
