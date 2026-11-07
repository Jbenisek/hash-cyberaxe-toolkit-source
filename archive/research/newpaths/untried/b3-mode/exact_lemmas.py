"""Exact facts behind the mode-level obstruction, checked on the reference G and compression.

Run: python -B exact_lemmas.py   (seconds, one process)

L1  For a fixed G input (a,b,c,d), the maps (x,y) -> (a2,d2) and (x,y) -> (b2,c2) are bijections.
    Consequence: equal G inputs with a message difference always change BOTH a row-a/d output word
    and a row-b/c output word.  A message-only difference can never cancel inside one G call.
L2  The G input words b and c are functions of the G output alone (no x, y involved).
    Consequence: a row-b or row-c input difference can never be absorbed by a G call,
    whatever its message words are.
L3  Mode inputs of each node type in the reference (counter, block_len, flags): parents always
    (IV, t=0, 64, PARENT[|ROOT]); every non-final block has block_len 64; the counter of a
    chunk is its index.  Checked by instrumenting the reference.
"""
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFIER = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "hash-smash", "verifier"))
sys.path.insert(0, VERIFIER)
import blake3 as ref  # noqa: E402

M32 = 0xFFFFFFFF


def rol(v, n):
    return ((v << n) | (v >> (32 - n))) & M32


def g_ref(a, b, c, d, x, y):
    v = [a, b, c, d]
    ref._g(v, 0, 1, 2, 3, x, y)
    return tuple(v)


def xy_from_bc(inp, b2, c2):
    a, b, c, d = inp
    b1 = rol(b2, 7) ^ c2
    c1 = rol(b1, 12) ^ b          # from b1 = ror(b ^ c1, 12)
    d1 = (c1 - c) & M32
    a1 = rol(d1, 16) ^ d
    x = (a1 - a - b) & M32
    d2 = (c2 - c1) & M32
    a2 = rol(d2, 8) ^ d1
    y = (a2 - a1 - b1) & M32
    return x, y


def xy_from_ad(inp, a2, d2):
    a, b, c, d = inp
    d1 = rol(d2, 8) ^ a2
    a1 = rol(d1, 16) ^ d
    x = (a1 - a - b) & M32
    c1 = (c + d1) & M32
    b1 = rol(b ^ c1, 32 - 12)     # ror 12
    y = (a2 - a1 - b1) & M32
    return x, y


def bc_from_out(out):
    a2, b2, c2, d2 = out
    b1 = rol(b2, 7) ^ c2
    c1 = (c2 - d2) & M32
    d1 = rol(d2, 8) ^ a2
    b = rol(b1, 12) ^ c1
    c = (c1 - d1) & M32
    return b, c


def main():
    rng = random.Random(20261010)
    n = 200_000
    bad1 = bad2 = bad3 = 0
    for _ in range(n):
        inp = tuple(rng.getrandbits(32) for _ in range(4))
        x, y = rng.getrandbits(32), rng.getrandbits(32)
        out = g_ref(*inp, x, y)
        if xy_from_bc(inp, out[1], out[2]) != (x, y):
            bad1 += 1
        if xy_from_ad(inp, out[0], out[3]) != (x, y):
            bad2 += 1
        if bc_from_out(out) != (inp[1], inp[2]):
            bad3 += 1
    print(f"L1 (x,y) recovered from (b2,c2): {n - bad1}/{n} ok")
    print(f"L1 (x,y) recovered from (a2,d2): {n - bad2}/{n} ok")
    print(f"L2 (b,c) recovered from output alone: {n - bad3}/{n} ok")

    # Direct pair test of L1: same input, different message -> (a2,d2) and (b2,c2) both differ.
    both = 0
    m = 100_000
    for _ in range(m):
        inp = tuple(rng.getrandbits(32) for _ in range(4))
        x, y = rng.getrandbits(32), rng.getrandbits(32)
        x2, y2 = x, y
        while (x2, y2) == (x, y):
            # sparse differences too: flip one bit of one word half the time
            if rng.random() < 0.5:
                x2, y2 = x ^ (1 << rng.randrange(32)), y
            else:
                x2, y2 = x, y ^ (1 << rng.randrange(32))
        o1, o2 = g_ref(*inp, x, y), g_ref(*inp, x2, y2)
        if (o1[0], o1[3]) != (o2[0], o2[3]) and (o1[1], o1[2]) != (o2[1], o2[2]):
            both += 1
    print(f"L1 pairs (same input, one-bit message difference): both halves differ in {both}/{m}")

    # L3: instrument the reference to log (counter, block_len, flags, cv==IV) of every compression.
    log = []
    real = ref._compress

    def spy(cv, words, counter, block_len, flags, rounds):
        log.append((counter, block_len, flags, tuple(cv) == ref.IV))
        return real(cv, words, counter, block_len, flags, rounds)

    ref._compress = spy
    try:
        for length in (1, 55, 63, 64, 65, 1024, 1025, 2048, 3136, 4097):
            log.clear()
            ref.blake3(bytes(rng.getrandbits(8) for _ in range(length)), rounds=2)
            parents = [e for e in log if e[2] & ref.PARENT]
            nonfinal_lens = sorted({e[1] for e in log[:-1] if not (e[2] & ref.PARENT) and not (e[2] & ref.CHUNK_END)})
            pc = sorted({(e[0], e[1], e[2], e[3]) for e in parents})
            print(f"L3 len {length:5d}: {len(log)} compressions; parent (t,len,flags,cv=IV) {pc}; "
                  f"non-final block lens {nonfinal_lens}; root (t,len,flags) {log[-1][:3]}")
    finally:
        ref._compress = real


if __name__ == "__main__":
    main()
