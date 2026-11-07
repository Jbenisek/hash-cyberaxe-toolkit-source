"""legal.py - is a chunk counter t >= 2^32 legal for blake3-r2-prefix-v1, and what does hashing such a message cost?

Reads the organizer's target profile (hash-smash/target-profiles/blake3-r2-prefix-v1.json) and imports the organizer's
reference hash-smash/verifier/blake3.py unchanged. Checks:
  P1  the profile's message domain and tree/counter text
  P2  blake3.py: the length bound and how _compress loads a 64-bit counter (v12 = t mod 2^32, v13 = t >> 32)
  P3  a walk trial at t = thi*2^32 + t_lo with thi = 2^19 - 1 (the largest legal high word): the reference _compress
      gives the half-collision; the message lengths 1024 t + 55 / 63 are below 2^61 bytes
  P4  the compression count of blake3(F || A) is 17 t + 1 (16 per full chunk, 1 for the last, t parents incl. the root),
      counted by wrapping _compress, for t = 1 .. 64 and a few larger t
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

import importlib.util
import json
import random
import struct

import walk_model as W

F = W.F
B3 = W.B3
PROFILE = _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/target-profiles/blake3-r2-prefix-v1.json')


def main():
    prof = json.load(open(PROFILE))
    print("P1 profile: message_domain = %r" % prof["message_domain"])
    print("   tree = %r" % prof["tree"])
    lim_bytes = 1 << 61
    print("P2 blake3.py rejects len(data) >= 2^61 bytes (bit length >= 2^64); _compress loads [counter & MASK, counter >> 32]")
    tmax = (lim_bytes - 64) // 1024        # largest t with 1024 t + 63 < 2^61
    print("   largest t with 1024 t + 63 < 2^61: %d = 2^51 - 1: %s ; t >> 32 = %d = 2^19 - 1: %s"
          % (tmax, tmax == 2 ** 51 - 1, tmax >> 32, (tmax >> 32) == 2 ** 19 - 1))
    # P3: a walk trial at the largest legal high word
    rng = random.Random(99)
    ok = 0
    for _ in range(50):
        ow = [rng.getrandbits(32) for _ in range(7)]
        e1, y = F.member(rng.getrandbits(19))
        thi = (1 << 19) - 1
        v = W.co_walk(ow, y, thi)
        c1 = W.qstar(rng.getrandbits(21))
        u = F.step_ct(v, c1)
        t = (thi << 32) | u["t"]
        cva, cvb = W.ref_cv(u["A"], t, F.LEN_A), W.ref_cv(u["B"], t, F.LEN_B)
        ok += all(cva[i] == cvb[i] for i in (0, 2, 5, 7)) and 1024 * t + 63 < lim_bytes
    print("P3 thi = 2^19 - 1: %d of 50 trials give CV words 0,2,5,7 equal on the reference, messages < 2^61 bytes" % ok)
    # P4: compression count of the organizer's tree code
    calls = [0]
    orig = B3._compress

    def counted(*a):
        calls[0] += 1
        return orig(*a)

    B3._compress = counted
    bad = 0
    for t in list(range(1, 65)) + [100, 255, 256, 257, 1000, 1023]:
        calls[0] = 0
        B3.blake3(bytes(1024 * t) + bytes(range(55)), 2)
        bad += calls[0] != 17 * t + 1
    B3._compress = orig
    print("P4 blake3(F || A) makes 17 t + 1 compressions for t = 1..64, 100, 255..257, 1000, 1023: %d mismatches" % bad)
    t = 2 ** 51 - 1
    per = 17 * t + 1
    import math
    print("   at t = 2^51 - 1: %d compressions per message = 2^%.4f; both messages 2^%.4f units; pkgCM (t < 2^32) "
          "charged both below 2^37.1" % (per, math.log2(per), math.log2(2 * per)))


if __name__ == "__main__":
    main()
