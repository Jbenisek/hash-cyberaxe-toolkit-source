"""Toy 2-round BLAKE3 for word size w (rotations floor(r*w/32) of 16,12,8,7), with a full trace.
Same conventions as research/grok/work/job28_newpaths/job28.py (checked by selfcheck()).
v = IV0..7, IV0..3, 0, 0, blocklen, flags.  Round 1 uses m[PERM[i]].
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


def rotr(z, r, w):
    m = (1 << w) - 1
    z &= m
    r %= w
    return ((z >> r) | (z << (w - r))) & m if r else z


def G(a, b, c, d, x, y, w, R=None):
    R = R or rots(w)
    m = (1 << w) - 1
    a = (a + b + x) & m
    d = rotr(d ^ a, R[0], w)
    c = (c + d) & m
    b = rotr(b ^ c, R[1], w)
    a = (a + b + y) & m
    d = rotr(d ^ a, R[2], w)
    c = (c + d) & m
    b = rotr(b ^ c, R[3], w)
    return a, b, c, d


def init_state(w, blen=None, flags=11, cv=None):
    m = (1 << w) - 1
    iv = [x & m for x in IV32]
    cv = iv if cv is None else cv
    if blen is None:
        blen = (2 * w) & m
    return list(cv) + iv[:4] + [0, 0, blen & m, flags & m]


def trace(msg, w, blen=None, flags=11, cv=None):
    """Returns dict: P (after r0 cols), Q (after r0), Y (after r1 cols), Z (final), out (8 words)."""
    v = init_state(w, blen, flags, cv)
    R = rots(w)
    res = {}
    for r in range(2):
        s = list(msg) if r == 0 else [msg[PERM[i]] for i in range(16)]
        for j, idx in enumerate(COLS):
            out = G(*(v[i] for i in idx), s[2 * j], s[2 * j + 1], w, R)
            for i, o in zip(idx, out):
                v[i] = o
        res["P" if r == 0 else "Y"] = v[:]
        for j, idx in enumerate(DIAG):
            out = G(*(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j], w, R)
            for i, o in zip(idx, out):
                v[i] = o
        res["Q" if r == 0 else "Z"] = v[:]
    res["out"] = [v[i] ^ v[i + 8] for i in range(8)]
    return res


def compress(msg, w, blen=None, flags=11, cv=None):
    return trace(msg, w, blen, flags, cv)["out"]


def inA(t, msg):
    """E0 and E2 inputs: Y0,Y5,Y10,Y15,m1,m11 and Y2,Y7,Y8,Y13,m9,m14."""
    Y = t["Y"]
    return (Y[0], Y[5], Y[10], Y[15], msg[1], msg[11], Y[2], Y[7], Y[8], Y[13], msg[9], msg[14])


def selfcheck():
    import importlib.util
    p = _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job28_newpaths/job28.py')
    spec = importlib.util.spec_from_file_location("job28ro", p)
    j = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(j)
    rng = random.Random(5)
    n = 0
    for w in (8, 12, 16, 32):
        for _ in range(200):
            msg = [rng.getrandbits(w) for _ in range(16)]
            assert compress(msg, w) == j.compress(msg, w, j.primary_rots(w)), w
            n += 1
    # 32-bit G hand check from job28 ANSWER.md: G(IV0,IV4,IV0,0;0,0)
    assert G(0x6A09E667, 0x510E527F, 0x6A09E667, 0, 0, 0, 32) == (0xEB2778D5, 0x5A8196B9, 0x70C46342, 0xCDD3C1C3)
    print(f"selfcheck: {n} random messages match job28.compress at w=8,12,16,32; hand-checked G matches")


if __name__ == "__main__":
    selfcheck()
