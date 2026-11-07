"""Vectorised toy 2-round BLAKE3 (numpy), same conventions as ../fringe/toyb3.py:
rotations floor(r*w/32) of (16,12,8,7); state = IV0..7, IV0..3, 0, 0, blocklen=2w, flags=11 (IV = low w bits).
Messages are arrays of shape (16, N) (uint64 holding w-bit words).  Round 1 uses m[PERM[i]].
selfcheck() compares against a plain scalar version and fringe/toyb3.py (read only, no bytecode written).
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
import numpy as np

sys.dont_write_bytecode = True
IV32 = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
U = np.uint64


def rots(w):
    return tuple((r * w) // 32 for r in (16, 12, 8, 7))


def vrotr(z, r, w):
    m = U((1 << w) - 1)
    r %= w
    if r == 0:
        return z & m
    return ((z >> U(r)) | (z << U(w - r))) & m


def vG(a, b, c, d, x, y, w, R):
    m = U((1 << w) - 1)
    a = (a + b + x) & m
    d = vrotr(d ^ a, R[0], w)
    c = (c + d) & m
    b = vrotr(b ^ c, R[1], w)
    a = (a + b + y) & m
    d = vrotr(d ^ a, R[2], w)
    c = (c + d) & m
    b = vrotr(b ^ c, R[3], w)
    return a, b, c, d


def init_state(w, blen=None, flags=11, cv=None):
    m = (1 << w) - 1
    iv = [x & m for x in IV32]
    cv = iv if cv is None else cv
    if blen is None:
        blen = (2 * w) & m
    return list(cv) + iv[:4] + [0, 0, blen & m, flags & m]


def vtrace(M, w, blen=None, flags=11, cv=None, rounds=2):
    """M: (16, N) uint64.  Returns dict with X (after round 0), Y (after r1 columns), Z (final), out (8, N)."""
    N = M.shape[1]
    R = rots(w)
    v = [np.full(N, s, dtype=U) for s in init_state(w, blen, flags, cv)]
    res = {}
    for r in range(rounds):
        s = [M[i] for i in range(16)] if r == 0 else [M[PERM[i]] for i in range(16)]
        for j, idx in enumerate(COLS):
            o = vG(*(v[i] for i in idx), s[2 * j], s[2 * j + 1], w, R)
            for i, t in zip(idx, o):
                v[i] = t
        if r == 1:
            res["Y"] = list(v)
        for j, idx in enumerate(DIAG):
            o = vG(*(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j], w, R)
            for i, t in zip(idx, o):
                v[i] = t
        if r == 0:
            res["X"] = list(v)
    res["Z"] = v
    res["out"] = np.stack([v[i] ^ v[i + 8] for i in range(8)])
    return res


def vout(M, w, **kw):
    return vtrace(M, w, **kw)["out"]


# ---- scalar reference -------------------------------------------------------------------------------------
def rotr(z, r, w):
    m = (1 << w) - 1
    r %= w
    return ((z >> r) | (z << (w - r))) & m if r else z & m


def G(a, b, c, d, x, y, w):
    R = rots(w)
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


def round_(v, s, w):
    v = list(v)
    for j, idx in enumerate(COLS):
        for i, t in zip(idx, G(*(v[i] for i in idx), s[2 * j], s[2 * j + 1], w)):
            v[i] = t
    for j, idx in enumerate(DIAG):
        for i, t in zip(idx, G(*(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j], w)):
            v[i] = t
    return v


def compress(msg, w, blen=None, flags=11, cv=None):
    v = init_state(w, blen, flags, cv)
    v = round_(v, list(msg), w)
    v = round_(v, [msg[PERM[i]] for i in range(16)], w)
    return [v[i] ^ v[i + 8] for i in range(8)]


def selfcheck():
    import importlib.util
    import random
    p = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/fringe/toyb3.py')
    spec = importlib.util.spec_from_file_location("fringe_toyb3_ro", p)
    fr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fr)
    rng = random.Random(11)
    n = 0
    for w in (8, 12, 16, 32):
        msgs = [[rng.getrandbits(w) for _ in range(16)] for _ in range(300)]
        M = np.array(msgs, dtype=U).T
        out = vout(M, w)
        for k, msg in enumerate(msgs):
            ref = compress(msg, w)
            assert ref == fr.compress(msg, w), w
            assert [int(out[i, k]) for i in range(8)] == ref, w
            n += 1
    assert G(0x6A09E667, 0x510E527F, 0x6A09E667, 0, 0, 0, 32) == (0xEB2778D5, 0x5A8196B9, 0x70C46342, 0xCDD3C1C3)
    print(f"selfcheck OK: {n} messages, numpy == scalar == fringe/toyb3 at w=8,12,16,32; 32-bit G hand value OK")


if __name__ == "__main__":
    selfcheck()
