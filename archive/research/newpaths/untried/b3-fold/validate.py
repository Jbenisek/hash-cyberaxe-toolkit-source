"""Check the pinned-pair generator against the organizer reference (hash-smash/verifier/blake3.py, rounds=2).

Checks, on n random free tuples (seed 1):
  1. Lemma L: round-0 state X identical for A (55 bytes, w4=W4) and B (63 bytes, w4=W4', w5-8).
  2. Pins: X3, X7, X11, X15 equal the front-line constants.
  3. C3 outputs equal the map's constants (Y3, Y11 differ; Y7, Y15 agree).
  4. Digest (CV) words 0, 2, 5, 7 agree; words 1, 3, 4, 6 reported.
  5. Byte legality: A is a 55-byte string, B a 63-byte string, both re-parse to the same words.
  6. numpy builder + numpy compression == reference final state, word for word.
  7. Framing: with t = 1, reference blake3(F||A) == parent(CV(F), CV(A)) built by hand.
"""
import struct
import sys
import time
import numpy as np
import b3fold_gen as g

t0 = time.time()
n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
rng = np.random.default_rng(1)
F = rng.integers(0, 2**32, size=(9, n), dtype=np.uint32)

bad = {k: 0 for k in ["lemmaL", "pins", "c3", "half", "bytes", "numpy", "e1zero", "e3zero"]}
C3A = (0x8127C181, 0x76F7AEFD, 0x7AF77F38, 0xBBFBDFFE)
C3B = (0x7EDF3E7E, 0x76F7AEFD, 0x850000C3, 0xBBFBDFFE)
c3_seen = set()
ZA_ref, ZB_ref = [], []
for i in range(n):
    free = tuple(int(F[j, i]) for j in range(9))
    wa, wb, t = g.build_pair(free)
    xa = g.round0_state(wa, t, g.LEN_A)
    xb = g.round0_state(wb, t, g.LEN_B)
    if xa != xb:
        bad["lemmaL"] += 1
    if (xa[3], xa[7], xa[11], xa[15]) != (g.X3P, g.X7P, g.X11P, g.X15P):
        bad["pins"] += 1
    # round-1 C3 = G(3,7,11,15; m4, m13) (round-1 message = PERM applied once: slots 6,7 -> w4, w13)
    ca = g.G(xa[3], xa[7], xa[11], xa[15], wa[4], wa[13])
    cb = g.G(xb[3], xb[7], xb[11], xb[15], wb[4], wb[13])
    c3_seen.add((ca, cb))
    if ca != C3A or cb != C3B:
        bad["c3"] += 1
    za, oa = g.ref_state(wa, t, g.LEN_A)
    zb, ob = g.ref_state(wb, t, g.LEN_B)
    if any(oa[w] != ob[w] for w in (0, 2, 5, 7)):
        bad["half"] += 1
    if all(za[w] == zb[w] for w in (1, 6, 11, 12)):
        bad["e1zero"] += 1
    if all(za[w] == zb[w] for w in (3, 4, 9, 14)):
        bad["e3zero"] += 1
    A = struct.pack("<16I", *wa)[:55]
    B = struct.pack("<16I", *wb)[:63]
    if (list(struct.unpack("<16I", A.ljust(64, b"\0"))) != wa or
            list(struct.unpack("<16I", B.ljust(64, b"\0"))) != wb or len(A) != 55 or len(B) != 63):
        bad["bytes"] += 1
    ZA_ref.append(za); ZB_ref.append(zb)

WA, WB, tl = g.build_pairs_v(F)
ZA = g.compress2_v(WA, tl, g.LEN_A)
ZB = g.compress2_v(WB, tl, g.LEN_B)
ZA = np.array(ZA, dtype=np.uint64).T
ZB = np.array(ZB, dtype=np.uint64).T
bad["numpy"] = int(np.sum(np.any(ZA != np.array(ZA_ref, dtype=np.uint64), axis=1) |
                          np.any(ZB != np.array(ZB_ref, dtype=np.uint64), axis=1)))

# 7. framing check with t = 1 (F = one random 1,024-byte chunk)
fr_ok = 0
fr_n = 20
for i in range(fr_n):
    free = list(int(F[j, i]) for j in range(9))
    free[5] = 1  # t_lo = 1
    wa, wb, t = g.build_pair(tuple(free))
    Fbytes = bytes(rng.integers(0, 256, size=1024, dtype=np.uint8))
    A = struct.pack("<16I", *wa)[:55]
    cv_f = g.ref._compress(*g.ref._chunk_output(Fbytes, 0, 2), 2)[:8]
    cv_a = g.ref._compress(g.IV, wa, 1, 55, 3, 2)[:8]
    root = g.ref._compress(g.IV, cv_f + cv_a, 0, 64, g.ref.PARENT | g.ref.ROOT, 2)[:8]
    if g.ref.blake3(Fbytes + A, 2) == struct.pack("<8I", *root):
        fr_ok += 1

print(f"n={n}  failures: {bad}")
print(f"distinct C3 output tuples seen: {len(c3_seen)}")
for ca, cb in list(c3_seen)[:2]:
    print("  C3 A:", " ".join(f"{x:08x}" for x in ca), "| B:", " ".join(f"{x:08x}" for x in cb))
print(f"W4'={g.W4B:08x}  DW5={g.DW5:08x}  K={g.KK:08x}")
print(f"framing check (t=1, reference blake3 vs hand-built parent): {fr_ok}/{fr_n}")
print(f"elapsed {time.time() - t0:.1f}s")
