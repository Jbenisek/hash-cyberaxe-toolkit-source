#!/usr/bin/env python3
"""tree_check.py  (scout_recent; research only)
Checks, with the ORGANIZER's reference (hash-smash\\verifier\\blake3.py, imported read-only, rounds=2), that the
digest of  P || X  (P = t full 1024-byte chunks, X = a 55- or 63-byte last chunk) depends on X only through the
chunk chaining value  CV_t(X) = first 8 words of compress(IV, X, counter=t, len(X), CHUNK_START|CHUNK_END).
So two last chunks with equal CV_t give a full 2-round BLAKE3 collision of P||X and P||X'.
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

import sys, os, random, struct
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as ref                                   # organizer reference, not modified

R = 2


def cv_chunk(chunk, t):
    out = ref._chunk_output(chunk, t, R)
    return ref._compress(*out, R)[:8]


def tree_root(cvs):
    """digest from the list of chunk CVs (n >= 2): binary tree, largest power-of-two left subtree"""
    def node(lst, root):
        if len(lst) == 1: return lst[0]
        k = 1
        while k * 2 < len(lst): k *= 2
        left, right = node(lst[:k], False), node(lst[k:], False)
        fl = ref.PARENT | (ref.ROOT if root else 0)
        return ref._compress(ref.IV, left + right, 0, 64, fl, R)[:8]
    return struct.pack('<8I', *node(cvs, True))


def main():
    rng = random.Random(7)
    n = 0
    for t in (1, 2, 3, 4, 5, 6, 7, 11, 16):
        P = bytes(rng.randrange(256) for _ in range(1024 * t))
        pre = [cv_chunk(P[i * 1024:(i + 1) * 1024], i) for i in range(t)]
        for L in (55, 63):
            for _ in range(20):
                X = bytes(rng.randrange(256) for _ in range(L))
                assert ref.blake3(P + X, R) == tree_root(pre + [cv_chunk(X, t)]), (t, L)
                # the last chunk is a single block: its CV is one compression with counter t and flags 3
                w = struct.unpack('<16I', X.ljust(64, b'\0'))
                assert cv_chunk(X, t) == ref._compress(ref.IV, w, t, L, 3, R)[:8]
                n += 1
    print(f'{n} messages: organizer digest == tree_root(prefix CVs, CV_t(last chunk)) in all; '
          f'CV_t = compress(IV, block, counter t, len, flags 3)')


if __name__ == '__main__':
    main()
