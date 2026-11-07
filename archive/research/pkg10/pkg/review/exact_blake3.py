#!/usr/bin/env python3
"""exact lens: BLAKE3 written from the BLAKE3 specification (one chunk, inputs of at most 1024 bytes),
with the number of rounds as a parameter. Not copied from the package and not from the organizer's code.

hash(data, rounds)                -> 32 digest bytes
trace(words, n, rounds=2)         -> (output words o[0..15], dict of the values of every G call, states)
"""
import struct

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CHUNK_START, CHUNK_END, ROOT = 1, 2, 8
COLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))
DIAG = ((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))


def rotr(x, r):
    return ((x >> r) | (x << (32 - r))) & M32


def g_values(A, B, C, D, x, y):
    """the eight values of one G call, in the order they are assigned"""
    a1 = (A + B + x) & M32
    d1 = rotr(D ^ a1, 16)
    c1 = (C + d1) & M32
    b1 = rotr(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M32
    d2 = rotr(d1 ^ a2, 8)
    c2 = (c1 + d2) & M32
    b2 = rotr(b1 ^ c2, 7)
    return a1, d1, c1, b1, a2, d2, c2, b2


def compress(cv, m, counter, block_len, flags, rounds, rec=None):
    v = list(cv) + list(IV[:4]) + [counter & M32, (counter >> 32) & M32, block_len, flags]
    m = list(m)
    for r in range(rounds):
        for half, idx in ((0, COLS), (1, DIAG)):
            for i, (a, b, c, d) in enumerate(idx):
                x, y = m[2 * i + 8 * half], m[2 * i + 1 + 8 * half]
                vals = g_values(v[a], v[b], v[c], v[d], x, y)
                if rec is not None:
                    rec[(r, half, i)] = dict(inp=(v[a], v[b], v[c], v[d]), xy=(x, y), vals=vals, idx=(a, b, c, d))
                v[a], v[b], v[c], v[d] = vals[4], vals[7], vals[6], vals[5]
            if rec is not None:
                rec[("state", r, half)] = tuple(v)
        m = [m[PERM[i]] for i in range(16)]
    out = [v[i] ^ v[i + 8] for i in range(8)] + [v[i + 8] ^ cv[i] for i in range(8)]
    return out


def hash(data, rounds=7):
    """unkeyed BLAKE3-256 of one chunk (len(data) <= 1024)"""
    assert len(data) <= 1024
    blocks = [data[i:i + 64] for i in range(0, len(data), 64)] or [b""]
    cv = list(IV)
    for k, blk in enumerate(blocks):
        flags = (CHUNK_START if k == 0 else 0)
        last = k == len(blocks) - 1
        if last:
            flags |= CHUNK_END | ROOT
        words = struct.unpack("<16I", blk + bytes(64 - len(blk)))
        out = compress(cv, words, 0, len(blk), flags, rounds)
        if last:
            return struct.pack("<8I", *out[:8])
        cv = out[:8]


def trace(words, n, rounds=2):
    rec = {}
    out = compress(IV, words, 0, n, CHUNK_START | CHUNK_END | ROOT, rounds, rec)
    return out, rec


KNOWN = {
    b"": "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262",
    b"abc": "6437b3ac38465133ffb63b75273a8db548c558465d79db03fd359c6cd5bd9d85",
    b"\x00": "2d3adedff11b61f14c886e35afa036736dcd87a74d27b5c1510225d0f592e213",
}

if __name__ == "__main__":
    import sys
    bad = 0
    for msg, hx in KNOWN.items():
        ok = hash(msg, 7).hex() == hx
        bad += not ok
        print("7 rounds, published digest of %r: %s" % (msg, "equal" if ok else "DIFFERENT"))
    if len(sys.argv) > 1:
        # compare with the organizer's reference (a copy in a scratch directory), rounds 2 and 7
        sys.path.insert(0, sys.argv[1])
        import hashlib
        import org_blake3
        cnt = diff = 0
        for rounds in (2, 7):
            for n in list(range(0, 130)) + [55, 63] * 400 + [1023, 1024]:
                for t in range(3):
                    data = hashlib.shake_256(b"exact %d %d %d %d" % (rounds, n, t, cnt)).digest(n)
                    cnt += 1
                    diff += hash(data, rounds) != org_blake3.blake3(data, rounds)
        print("against the organizer's reference: %d inputs (rounds 2 and 7, lengths 0..129, 55, 63, 1023, 1024), "
              "different %d" % (cnt, diff))
        bad += diff
    sys.exit(1 if bad else 0)
