#!/usr/bin/env python3
"""adj_check.py (counter/adjudicate; research only).
1. Re-check two real counter-arrangement last chunks (structure/e2e_t1.txt, t = 1) on the organizer's own
   verifier/blake3.py: CV words 0,2,5,7 equal with counter t and flags 3; not equal as a root (counter 0, flags 11).
2. Show what an organizer 'digest-xor-mask' experiment would see for such a pair: the final digests of P||A and P||B
   (P = any one chunk) on the half-collision mask.
3. Recompute every time_log2 figure in the three reports under one formula, so the conventions can be compared.
Read-only use of the organizer verifier (imported from its path, nothing written there)."""

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

import sys, struct, os
from math import log2
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as ref   # organizer reference

A_HEX = ['ea21f9c6528a70b0a38051ac4d05107138564797368717b813a3ea6f7a26a67e5c39d2af7bfaaa763c629ac8fed02c7e72cea0f506c007',
         'f74c2cc90f18cc27f678e4c38eda271c38564797502769bbd3bbb9f54ad5724cfde2f217d51e4e8818bb24e60a37987d9b84b84d06c007']
B_HEX = ['ea21f9c6528a70b0a38051ac4d051071405647972e8717b813a3ea6f7a26a67e5c39d2af7bfaaa763c629ac8fed02c7e72cea0f506c0070000000000000000',
         'f74c2cc90f18cc27f678e4c38eda271c40564797482769bbd3bbb9f54ad5724cfde2f217d51e4e8818bb24e60a37987d9b84b84d06c0070000000000000000']
HALF = (0, 2, 5, 7)

def cv(block, counter, flags):
    words = struct.unpack('<16I', block.ljust(64, b'\0'))
    return ref._compress(ref.IV, words, counter, len(block), flags, 2)[:8]

print('== 1/2: organizer verifier on the two t = 1 pairs of structure/e2e_t1.txt')
for i, (ah, bh) in enumerate(zip(A_HEX, B_HEX)):
    a, b = bytes.fromhex(ah), bytes.fromhex(bh)
    assert len(a) == 55 and len(b) == 63 and b[55:] == b'\0' * 8
    ca, cb = cv(a, 1, 3), cv(b, 1, 3)
    ra, rb = cv(a, 0, 11), cv(b, 0, 11)
    eq_ctr = all(ca[j] == cb[j] for j in HALF)
    eq_root = sum(ra[j] == rb[j] for j in HALF)
    for pname, P in (('P = zero chunk', b'\0' * 1024), ('P = 00..ff x4', bytes(range(256)) * 4)):
        da, db = ref.blake3(P + a, rounds=2), ref.blake3(P + b, rounds=2)
        wa, wb = struct.unpack('<8I', da), struct.unpack('<8I', db)
        mask_ok = all(wa[j] == wb[j] for j in HALF)
        print(f' pair {i}, {pname}: CV_t words 0,2,5,7 equal (counter 1, flags 3): {eq_ctr}; as a root block (counter 0, flags 11):'
              f' {eq_root}/4 words equal; final digests of P||A, P||B ({len(P + a)}/{len(P + b)} bytes) equal on the'
              f' half mask: {mask_ok}; equal in full: {da == db}')

print()
print('== 3: one formula for every figure: T = log2(lambda) + 128 - log2(C / m) + log2(ops / 430) + c')
def T(C, m, ops, lam=0.5, c=0.02):
    return log2(lam) + 128 - log2(C / m) + log2(ops / 430) + c
C_FILED = 185377197.5523         # sub-class rate count (pkg10; Sol answer Y: 194382080300609 / 2^20)
C_BOARD = 185350144              # the count the board's F is set against (5/7 of it = 132,392,960)
C_CTR = 67698688 * 2 ** 11       # beta* part x 2^11 (Sol answer Y: 138,646,913,024)
print(f' rate factor counter/filed (sub-class): {C_CTR / C_FILED:.3f} = 2^{log2(C_CTR / C_FILED):.4f}')
print(f' rate factor against the board count:   {C_CTR / C_BOARD:.3f} = 2^{log2(C_CTR / C_BOARD):.4f}')
print(f' whole class (905x):                   {71698432 * 2 ** 11 / 162266763.6588:.2f}')
rows = [
 ('filed 92.53 (clusters; 1.65 per trial-equivalent; margin 2.0)', C_FILED, 2.0, 1.65),
 ('filed arrangement, no clusters, our machine 7.7, margin 2.0', C_FILED, 2.0, 7.7),
 ('counter, our machine 6.5, margin 2.0  [VALUE]', C_CTR, 2.0, 6.5),
 ('counter, our machine 6.5, margin 1.4', C_CTR, 1.4, 6.5),
 ('board leader shape: board count, margin 1.4, 3.36 ops (their lighter machine)', C_BOARD, 1.4, 3.36),
 ('counter, margin 1.4, 3.4 ops  [STRUCTURE guess]', C_CTR, 1.4, 3.4),
 ('counter, margin 1.4, 6.5 x 3.36/7.7 = 2.84 ops (board machine scaled by our ratio)', C_CTR, 1.4, 6.5 * 3.36 / 7.7),
 ('counter, margin 2.0, charge 7.7 (no cost gain at all)', C_CTR, 2.0, 7.7),
]
for name, C, m, ops in rows:
    print(f' {T(C, m, ops):8.3f}  {name}')
# ops per trial implied by the board's 93.01972 (winglock) and 93.0451 (GordoAR) at margin 1.4 on the board count
for claim in (93.01972, 93.0451):
    ops = 430 * 2 ** (claim - (log2(0.5) + 128 - log2(C_BOARD / 1.4)) - 0.0)
    print(f' board {claim}: implied ops per trial (c = 0) {ops:.3f}')
# toy realised fraction in bits
print(f' toy realised fraction 0.94 +- 0.13 -> {log2(0.94):+.3f} bit (1 sd range {log2(0.81):+.3f} .. {log2(1.07):+.3f})')
