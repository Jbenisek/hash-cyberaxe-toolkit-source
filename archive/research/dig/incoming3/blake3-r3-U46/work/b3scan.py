"""b3scan.py - own tools for the blake3-r3 dig (units U46-U54).
1. scalar BLAKE3 compress, written from the spec, with skip/override hooks;
2. a tracer of the packed circuit (same rules as research/blake3_r3/candidate_blake3/experiments/rho.py, rewritten
   here), with per-step op attribution, variants (pitch, lanes, mask policy, skipped steps, message-word modes) and an
   optional numpy 'real' mode that keeps the unreduced lane values;
3. validation: 7-round vectors and verifier blake3.py, 3 rounds, packed circuit vs scalar.
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

import sys, os, math, hashlib
import numpy as np
from collections import Counter

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GCALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
ROT = (16, 12, 8, 7)


def ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


# ---------------------------------------------------------------- scalar
def digest_words(m, rounds=3, flags=11, blen=64, counter=0, skip=(), mover=None):
    """skip = set of (round, call, quarter) steps left out; mover = {word index: replacement value}"""
    v = list(IV) + list(IV[:4]) + [counter & M32, counter >> 32, blen, flags]
    m = list(m)
    if mover:
        for i, x in mover.items():
            m[i] = x
    for r in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            if (r, j, 1) not in skip:
                v[a] = (v[a] + v[b] + x) & M32
                v[d] = ror(v[d] ^ v[a], 16)
            if (r, j, 2) not in skip:
                v[c] = (v[c] + v[d]) & M32
                v[b] = ror(v[b] ^ v[c], 12)
            if (r, j, 3) not in skip:
                v[a] = (v[a] + v[b] + y) & M32
                v[d] = ror(v[d] ^ v[a], 8)
            if (r, j, 4) not in skip:
                v[c] = (v[c] + v[d]) & M32
                v[b] = ror(v[b] ^ v[c], 7)
        m = [m[i] for i in PERM]
    return [v[i] ^ v[i + 8] for i in range(8)]


def word_positions(rounds=3):
    """for each original message word: list of (round, call, 'x'|'y')"""
    pos = {i: [] for i in range(16)}
    idx = list(range(16))
    for r in range(rounds):
        for j in range(8):
            pos[idx[2 * j]].append((r, j, "x"))
            pos[idx[2 * j + 1]].append((r, j, "y"))
        idx = [idx[i] for i in PERM]
    return pos


# ---------------------------------------------------------------- tracer
class V:
    __slots__ = ("c", "bound", "nv", "cs", "real", "name")

    def __init__(s, c=None, bound=0, nv=0, cs=0.0, real=None, name=None):
        s.c, s.bound, s.nv, s.cs, s.real, s.name = c, bound, nv, cs, real, name


class Tracer:
    def __init__(self, pitch=36, lanes=7, policy="shipped", swar=False, nlanes_real=None):
        self.pitch, self.lanes, self.policy, self.swar = pitch, lanes, policy, swar
        self.LIM = 1 << pitch
        self.ops = 0
        self.by_kind = Counter()
        self.by_tag = {}
        self.tag = None
        self.masks_internal = []   # (tag, bound_before)
        self.adds = []             # (tag, nv, cs, bound, real or None) for each add output
        self.k = 0

    def emit(self, kind, n=1):
        self.ops += n
        self.by_kind[kind] += n
        self.by_tag.setdefault(self.tag, Counter())[kind] += n

    def mask(self, a, internal=True):
        if internal:
            self.masks_internal.append((self.tag, a.bound))
        self.emit("and")
        return V(None, M32, 1, 0.0, None if a.real is None else (a.real & np.uint64(M32)))

    def _addpair(self, acc, v):
        if self.swar:
            self.emit("swar_add", 6)
            r = None if acc.real is None else ((acc.real + v.real) & np.uint64(M32))
            return V(None, M32, 1, 0.0, r)
        while acc.bound + v.bound >= self.LIM:
            if self.policy == "none":
                break
            if acc.bound + v.bound >= self.LIM and acc.bound <= M32 and v.bound <= M32:
                raise ValueError("pitch too small for a plain add")
            if acc.bound >= v.bound:
                acc = self.mask(acc)
            else:
                v = self.mask(v)
        self.emit("add")
        r = None if acc.real is None else acc.real + v.real
        out = V(None, acc.bound + v.bound, acc.nv + v.nv, acc.cs + v.cs, r)
        self.adds.append((self.tag, out))
        return out

    def add(self, *xs):
        c = sum(x.c for x in xs if x.c is not None) & M32
        vs = [x for x in xs if x.c is None]
        if not vs:
            return V(c=c)
        acc = vs[0]
        for v in vs[1:]:
            acc = self._addpair(acc, v)
        if c:
            if self.swar:
                self.emit("swar_add", 5)
                return V(None, M32, 1, 0.0, None if acc.real is None else ((acc.real + np.uint64(c)) & np.uint64(M32)))
            if acc.bound + c >= self.LIM and self.policy != "none":
                acc = self.mask(acc)
            self.emit("add")
            r = None if acc.real is None else acc.real + np.uint64(c)
            out = V(None, acc.bound + c, acc.nv, acc.cs + c / 2.0 ** 32, r)
            self.adds.append((self.tag, out))
            return out
        return acc

    def xor(self, a, b):
        if a.c is not None and b.c is not None:
            return V(c=a.c ^ b.c)
        if a.c is not None:
            a, b = b, a
        if b.c is not None:
            if b.c == 0:
                return a
            self.emit("xor")
            return V(None, (1 << max(a.bound.bit_length(), b.c.bit_length())) - 1, 1, 0.0,
                     None if a.real is None else a.real ^ np.uint64(b.c))
        self.emit("xor")
        return V(None, (1 << max(a.bound.bit_length(), b.bound.bit_length())) - 1, 1, 0.0,
                 None if a.real is None else a.real ^ b.real)

    def ror(self, a, r):
        if a.c is not None:
            return V(c=ror(a.c, r))
        self.emit("rot", 5)
        if a.real is None:
            rr = None
        else:
            x = a.real & np.uint64(M32)
            rr = ((x >> np.uint64(r)) | (x << np.uint64(32 - r))) & np.uint64(M32)
        return V(None, M32, 1, 0.0, rr)


def build(words=None, skip=(), policy="shipped", pitch=36, lanes=7, swar=False, rounds=3,
          inputs=None, mover=None, final_mask=True):
    """words: dict original word index -> 'z' (zero const), 'v' (variable), or int (nonzero constant).
    default: 0..7 zero, 8..15 variable. inputs: dict word -> uint64 numpy array (real mode)."""
    tr = Tracer(pitch, lanes, policy, swar)
    wm = {i: ("z" if i < 8 else "v") for i in range(16)}
    if words:
        wm.update(words)
    m = []
    for i in range(16):
        w = wm[i]
        if w == "z":
            m.append(V(c=0))
        elif w == "v":
            m.append(V(None, M32, 1, 0.0, None if inputs is None else inputs[i], "i%d" % i))
        else:
            m.append(V(c=w & M32))
    v = [V(c=w) for w in IV] + [V(c=w) for w in IV[:4]] + [V(c=0), V(c=0), V(c=64), V(c=11)]
    for r in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            tr.tag = (r, j, 1)
            if tr.tag not in skip:
                v[a] = tr.add(v[a], v[b], x)
                v[d] = tr.ror(tr.xor(v[d], v[a]), 16)
            tr.tag = (r, j, 2)
            if tr.tag not in skip:
                v[c] = tr.add(v[c], v[d])
                v[b] = tr.ror(tr.xor(v[b], v[c]), 12)
            tr.tag = (r, j, 3)
            if tr.tag not in skip:
                v[a] = tr.add(v[a], v[b], y)
                v[d] = tr.ror(tr.xor(v[d], v[a]), 8)
            tr.tag = (r, j, 4)
            if tr.tag not in skip:
                v[c] = tr.add(v[c], v[d])
                v[b] = tr.ror(tr.xor(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    tr.tag = "digest"
    out = []
    for i in range(8):
        z = tr.xor(v[i], v[i + 8])
        if z.c is None and z.bound > M32 and final_mask:
            z = tr.mask(z, internal=False)
        out.append(z)
    tr.out = out
    return tr


# ---------------------------------------------------------------- ledger (uses our rho.py, patched PH)
_RHO = None


def rho():
    global _RHO
    if _RHO is None:
        sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r3/candidate_blake3/experiments'))
        import rho as r
        _RHO = r
    return _RHO


def time_log2(ph):
    r = rho()
    old = r.PH
    r.PH = ph
    try:
        lg = r.ledger(256)
        return math.log2(lg["total"] / 638)
    finally:
        r.PH = old


def rand_inputs(n, seed):
    rng = np.random.default_rng(seed)
    return {i: rng.integers(0, 1 << 32, size=n, dtype=np.uint64) for i in range(16)}


def check_vs_scalar(tr, inputs, n, rounds=3, skip=(), words=None, nchk=200):
    """compare the real-mode outputs of the traced variant with the scalar function using the same variant"""
    wm = {i: ("z" if i < 8 else "v") for i in range(16)}
    if words:
        wm.update(words)
    bad = 0
    for s in range(min(n, nchk)):
        m = []
        for i in range(16):
            w = wm[i]
            m.append(0 if w == "z" else (int(inputs[i][s]) if w == "v" else w & M32))
        ref = digest_words(m, rounds, skip=skip)
        got = [int(tr.out[i].real[s]) & M32 if tr.out[i].c is None else tr.out[i].c for i in range(8)]
        if ref != got:
            bad += 1
    return bad


def avalanche(words=None, skip=(), n=2000, seed=1):
    """mean number of digest bits (of 256) that differ between the full 3-round function and the variant"""
    rng = np.random.default_rng(seed)
    wm = {i: ("z" if i < 8 else "v") for i in range(16)}
    if words:
        wm.update(words)
    tot, cnt_eq_words, anyword = 0, 0, 0
    for _ in range(n):
        m = [0] * 16
        for i in range(8, 16):
            m[i] = int(rng.integers(0, 1 << 32))
        a = digest_words(m, 3)
        b = digest_words(m, 3, skip=skip)
        d = sum(bin(x ^ y).count("1") for x, y in zip(a, b))
        tot += d
        eqw = sum(1 for x, y in zip(a, b) if x == y)
        cnt_eq_words += eqw
        anyword += 1 if eqw else 0
    return tot / n, cnt_eq_words / n, anyword / n


# ---------------------------------------------------------------- validation
def validate():
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone'))
    from verifier.blake3 import blake3 as vb3
    import struct
    res = {}
    # 7 rounds: empty input (known vector) = af1349b9...
    known = "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    mine = b"".join(struct.pack("<I", w) for w in digest_words([0] * 16, 7, flags=11, blen=0))
    res["empty_7r_known"] = mine.hex() == known
    res["empty_7r_verifier"] = vb3(b"", 7).hex() == known
    # random 64-byte one-block messages, rounds 1..7
    rng = np.random.default_rng(7)
    ok = True
    for rounds in (1, 2, 3, 5, 7):
        for _ in range(40):
            data = bytes(rng.integers(0, 256, size=64, dtype=np.uint8))
            w = struct.unpack("<16I", data)
            mine = b"".join(struct.pack("<I", x) for x in digest_words(list(w), rounds, flags=11, blen=64))
            if mine != vb3(data, rounds):
                ok = False
    res["blocks_vs_verifier_rounds_1_2_3_5_7"] = ok
    # target shape: 0^32 || x at 3 rounds
    ok = True
    for _ in range(100):
        x = bytes(rng.integers(0, 256, size=32, dtype=np.uint8))
        w = [0] * 8 + list(struct.unpack("<8I", x))
        mine = b"".join(struct.pack("<I", y) for y in digest_words(w, 3))
        if mine != vb3(bytes(32) + x, 3):
            ok = False
    res["prefix_target_3r_vs_verifier"] = ok
    # packed tracer vs scalar
    inputs = rand_inputs(512, 3)
    tr = build(inputs=inputs)
    res["tracer_ops"] = tr.ops
    res["tracer_by_kind"] = dict(tr.by_kind)
    res["tracer_vs_scalar_mismatch_of_200"] = check_vs_scalar(tr, inputs, 512)
    res["internal_masks"] = tr.masks_internal
    res["time_log2_595"] = time_log2(tr.ops)
    return res


if __name__ == "__main__":
    import json
    print(json.dumps(validate(), indent=1, default=str))
