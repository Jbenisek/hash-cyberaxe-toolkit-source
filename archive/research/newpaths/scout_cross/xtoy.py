"""Vectorised toy 2-round BLAKE3 with free instance constants (cv, counter, flags, block length).
Windows python + numpy. Word size w in {6,8,12,16,32}; rotations floor(r*w/32) as in job28 'primary';
IV = low w bits of the real IV.  At w=32 it must equal hash-smash/verifier/blake3.py _compress(rounds=2).
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

import numpy as np

IV32 = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
        0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]


class Toy:
    def __init__(self, w, alt=False):
        self.w = w
        self.mask = np.uint64((1 << w) - 1)
        # primary: floor(r*w/32) as job28; alt: (r*w+16)//32 (job28 alt_rots)
        self.rots = tuple(((r * w + 16) // 32) if alt else ((r * w) // 32) for r in (16, 12, 8, 7))
        self.iv = [x & ((1 << w) - 1) for x in IV32]

    def rotr(self, z, r):
        w, m = self.w, self.mask
        if r == 0:
            return z
        return ((z >> np.uint64(r)) | (z << np.uint64(w - r))) & m

    def G(self, a, b, c, d, x, y):
        m = self.mask
        R0, R1, R2, R3 = self.rots
        a = (a + b + x) & m
        d = self.rotr(d ^ a, R0)
        c = (c + d) & m
        b = self.rotr(b ^ c, R1)
        a = (a + b + y) & m
        d = self.rotr(d ^ a, R2)
        c = (c + d) & m
        b = self.rotr(b ^ c, R3)
        return a, b, c, d

    def init_state(self, n, cv=None, counter=0, blen=None, flags=11):
        """blen may be an int or an array of length n."""
        m = int(self.mask)
        cv = self.iv if cv is None else [c & m for c in cv]
        full = lambda val: np.full(n, np.uint64(val & m), dtype=np.uint64)
        v = [full(c) for c in cv] + [full(c) for c in self.iv[:4]]
        lo = counter & m
        hi = (counter >> self.w) & m if self.w < 32 else (counter >> 32) & m
        v += [full(lo), full(hi)]
        if isinstance(blen, np.ndarray):
            v.append(blen.astype(np.uint64) & self.mask)
        else:
            v.append(full(blen))
        v.append(full(flags))
        return v

    def rounds(self, msg, v, keep=False):
        """msg: list of 16 arrays. Returns final state; with keep=True also X (after round 0) and Y
        (after round-1 column step)."""
        v = list(v)
        mm = list(msg)
        X = Y = None
        for r in range(2):
            G = self.G
            v[0], v[4], v[8], v[12] = G(v[0], v[4], v[8], v[12], mm[0], mm[1])
            v[1], v[5], v[9], v[13] = G(v[1], v[5], v[9], v[13], mm[2], mm[3])
            v[2], v[6], v[10], v[14] = G(v[2], v[6], v[10], v[14], mm[4], mm[5])
            v[3], v[7], v[11], v[15] = G(v[3], v[7], v[11], v[15], mm[6], mm[7])
            if r == 1:
                Y = list(v)
            v[0], v[5], v[10], v[15] = G(v[0], v[5], v[10], v[15], mm[8], mm[9])
            v[1], v[6], v[11], v[12] = G(v[1], v[6], v[11], v[12], mm[10], mm[11])
            v[2], v[7], v[8], v[13] = G(v[2], v[7], v[8], v[13], mm[12], mm[13])
            v[3], v[4], v[9], v[14] = G(v[3], v[4], v[9], v[14], mm[14], mm[15])
            if r == 0:
                X = list(v)
            mm = [mm[i] for i in PERM]
        if keep:
            return v, X, Y
        return v

    @staticmethod
    def out(v):
        return [v[i] ^ v[i + 8] for i in range(8)]


def selftest32(trials=200, seed=1):
    """Compare Toy(32) with the organizer's reference _compress(rounds=2) for random cv/counter/len/flags."""
    import importlib.util, random
    path = _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')
    spec = importlib.util.spec_from_file_location("refb3", path)
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)
    rnd = random.Random(seed)
    T = Toy(32)
    bad = 0
    for _ in range(trials):
        cv = [rnd.getrandbits(32) for _ in range(8)]
        words = [rnd.getrandbits(32) for _ in range(16)]
        counter = rnd.getrandbits(51)
        blen = rnd.randrange(0, 65)
        flags = rnd.choice([0, 1, 2, 3, 8, 9, 10, 11])
        want = ref._compress(cv, words, counter, blen, flags, 2)[:8]
        v0 = T.init_state(1, cv=cv, counter=counter, blen=blen, flags=flags)
        msg = [np.array([x], dtype=np.uint64) for x in words]
        got = [int(o[0]) for o in Toy.out(T.rounds(msg, v0))]
        bad += (list(want) != got)
    return bad


if __name__ == "__main__":
    print("w=32 mismatches vs organizer reference (200 random cv/counter/len/flags):", selftest32())

