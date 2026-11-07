"""method_check.py - small checks behind METHOD_NOTE.md (research only).

Run:  python -B method_check.py > method_check.txt
Imports the organizer verifier read-only (bytecode writing off); patches only the in-memory copy in part E.
A. BLAKE3 neutral direction: (w0+d, w1-d, t ^ a1 ^ a1') leaves the whole round-0 state unchanged.
B. Where w0, w1 sit in rounds 0..6 of the BLAKE3 message schedule.
C. Speed of the organizer's Python blake3 at 2 rounds, extrapolated to the message sizes the method produces.
D. BLAKE2s tree mode: node offset sits in h2 (checked against hashlib) and absorbs m4 in round 0 the same way.
E. Generalisation: a collision of the FIRST block of any chunk i (counter i, flags CHUNK_START) lifts to a
   full-message collision (planted collision on the organizer code path).
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

import sys, os, time, random, struct, hashlib, importlib.util
sys.dont_write_bytecode = True

VER = _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')
spec = importlib.util.spec_from_file_location("org_blake3", VER)
b3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b3)
M32 = 0xFFFFFFFF
IV = b3.IV
rng = random.Random(20261008)

# ---------------- A ----------------
def partA(n=3000):
    same1 = diff2 = tzero = ctrl_same = 0
    for _ in range(n):
        w = [rng.getrandbits(32) for _ in range(16)]
        w[13] &= 0x00FFFFFF; w[14] = 0; w[15] = 0          # a 55-byte block's zero tail
        t = rng.randrange(1, 1 << 32)
        d = rng.randrange(1, 1 << 32)
        a1 = (IV[0] + IV[4] + w[0]) & M32
        a1n = (a1 + d) & M32
        w2 = list(w); w2[0] = (w[0] + d) & M32; w2[1] = (w[1] - d) & M32
        t2 = t ^ a1 ^ a1n
        if t2 == 0:
            tzero += 1; continue
        r1a = b3._compress(IV, w, t, 55, 3, 1); r1b = b3._compress(IV, w2, t2, 55, 3, 1)
        same1 += r1a == r1b
        diff2 += b3._compress(IV, w, t, 55, 3, 2) != b3._compress(IV, w2, t2, 55, 3, 2)
        ctrl_same += r1a == b3._compress(IV, w2, t, 55, 3, 1)  # control: counter NOT re-solved
    print(f"A. trials {n}: round-0 state equal {same1}/{n - tzero}; 2-round outputs differ {diff2}/{n - tzero};"
          f" t'=0 skipped {tzero}; control (t kept constant) round-0 equal {ctrl_same}/{n - tzero}")
    print("   identity used: K0.a1 = IV0+IV4+w0, K0.d1 = ROR16(t ^ a1) fixed  =>  t' = t ^ a1 ^ a1', and"
          " w0 + w1 = K0.a2 - K0.b1 - IV0 - IV4 is constant along the direction")

# ---------------- B ----------------
def partB():
    names = ["col0", "col1", "col2", "col3", "diag0", "diag1", "diag2", "diag3"]
    m = list(range(16))
    print("B. message-schedule slots of w0 and w1 (G index, x = first word, y = second word)")
    for r in range(7):
        pos = {m[i]: i for i in range(16)}
        s = []
        for wi in (0, 1):
            i = pos[wi]
            s.append(f"w{wi}: {names[i // 2]}.{'x' if i % 2 == 0 else 'y'}")
        print(f"   round {r}: " + ", ".join(s))
        m = [m[i] for i in b3.PERMUTATION]

# ---------------- C ----------------
def partC():
    data = bytes(1024 * 256)  # 256 chunks
    t0 = time.perf_counter(); b3.blake3(data, 2); dt = time.perf_counter() - t0
    per_chunk = dt / 256
    print(f"C. organizer blake3(rounds=2): {dt:.3f} s for 256 chunks = {per_chunk * 1e3:.3f} ms/chunk (one core)")
    for label, t in (("t=1 (1079/1087 B)", 1), ("t=3 (harness cap 4096 B)", 3), ("t=63 (cap 65536 B)", 63),
                     ("t=2^31 (typical)", 1 << 31), ("t=2^32-1 (largest, v13=0)", (1 << 32) - 1)):
        s = 2 * (t + 1) * per_chunk
        print(f"   pair with {label}: about {s:.3g} s = {s / 86400:.3g} days single-threaded Python")

# ---------------- D ----------------
SIG = [[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],[14,10,4,8,9,15,13,6,1,12,0,2,11,7,5,3],
       [11,8,12,0,5,2,15,13,10,14,3,6,7,1,9,4],[7,9,3,1,13,12,11,14,2,6,5,10,4,0,15,8],
       [9,0,5,7,2,4,10,15,14,1,11,12,6,8,3,13],[2,12,6,10,0,11,8,3,4,13,7,5,15,14,1,9],
       [12,5,1,15,14,13,4,10,0,7,6,3,9,2,8,11],[13,11,7,14,12,1,3,9,5,0,15,4,8,6,2,10],
       [6,15,14,9,11,3,0,8,12,2,13,7,1,4,10,5],[10,2,8,4,7,6,1,5,15,11,9,14,3,12,13,0]]
def ror(x, n): return ((x >> n) | (x << (32 - n))) & M32
def g2(v, a, b, c, d, x, y):
    v[a] = (v[a] + v[b] + x) & M32; v[d] = ror(v[d] ^ v[a], 16); v[c] = (v[c] + v[d]) & M32; v[b] = ror(v[b] ^ v[c], 12)
    v[a] = (v[a] + v[b] + y) & M32; v[d] = ror(v[d] ^ v[a], 8);  v[c] = (v[c] + v[d]) & M32; v[b] = ror(v[b] ^ v[c], 7)
def b2s_state(h, m, t, f0, f1, rounds):
    v = list(h) + list(IV)
    v[12] ^= t & M32; v[13] ^= t >> 32; v[14] ^= f0; v[15] ^= f1
    for r in range(rounds):
        s = SIG[r % 10]
        g2(v, 0, 4, 8, 12, m[s[0]], m[s[1]]); g2(v, 1, 5, 9, 13, m[s[2]], m[s[3]])
        g2(v, 2, 6, 10, 14, m[s[4]], m[s[5]]); g2(v, 3, 7, 11, 15, m[s[6]], m[s[7]])
        g2(v, 0, 5, 10, 15, m[s[8]], m[s[9]]); g2(v, 1, 6, 11, 12, m[s[10]], m[s[11]])
        g2(v, 2, 7, 8, 13, m[s[12]], m[s[13]]); g2(v, 3, 4, 9, 14, m[s[14]], m[s[15]])
    return v
def b2s_param_h(offset, leaf, fanout=0, depth=2, node_depth=0, inner=32):
    p = bytes([32, 0, fanout, depth]) + struct.pack("<I", leaf) + offset.to_bytes(6, "little") + bytes([node_depth, inner]) + bytes(16)
    return [IV[i] ^ x for i, x in enumerate(struct.unpack("<8I", p))]
def b2s_leaf(data, offset, leaf):
    h = b2s_param_h(offset, leaf)
    m = list(struct.unpack("<16I", data.ljust(64, b"\0")))
    v = b2s_state(h, m, len(data), M32, M32, 10)
    return struct.pack("<8I", *[h[i] ^ v[i] ^ v[i + 8] for i in range(8)])
def partD(n=200, m_abs=2000):
    ok = 0
    for _ in range(n):
        L = rng.choice([64, 1024, 4096])
        off = rng.randrange(0, 1 << 48)
        data = os.urandom(rng.randrange(1, 65))
        ref = hashlib.blake2s(data, fanout=0, depth=2, leaf_size=L, node_offset=off, node_depth=0,
                              inner_size=32, last_node=True).digest()
        ok += ref == b2s_leaf(data, off, L)
    print(f"D. own BLAKE2s leaf (node offset in parameter bytes 8..13 -> h2, h3) == hashlib.blake2s: {ok}/{n}")
    same = ctrl = 0
    for _ in range(m_abs):
        L = 1024; off = rng.randrange(0, 1 << 32) | (rng.randrange(0, 1 << 16) << 32)
        m = [rng.getrandbits(32) for _ in range(16)]
        h = b2s_param_h(off, L); d = rng.randrange(1, 1 << 32)
        v2n = (h[2] - d) & M32                                  # keep a1 = v2 + v6 + m4 fixed
        off2 = (off & ~M32) | (v2n ^ IV[2])
        m2 = list(m); m2[4] = (m[4] + d) & M32
        s1 = b2s_state(h, m, 55, M32, M32, 1); s2 = b2s_state(b2s_param_h(off2, L), m2, 55, M32, M32, 1)
        same += s1[:16] == s2[:16]
        ctrl += s1[:16] == b2s_state(h, m2, 55, M32, M32, 1)[:16]
    print(f"   offset-absorbs-m4 direction: round-0 state equal {same}/{m_abs}; control (offset kept) {ctrl}/{m_abs}")

# ---------------- E ----------------
def partE(n=40):
    real = b3._compress
    ok = differ_unpatched = 0
    for k in range(n):
        i = rng.randrange(1, 9)                      # chunk index of the colliding first block
        nch = i + 1 + rng.randrange(0, 4)            # total chunks (colliding chunk need not be last)
        msg = bytearray(os.urandom(1024 * (nch - 1) + rng.randrange(65, 1025)))
        X = bytes(msg[1024 * i:1024 * i + 64]); Xp = os.urandom(64)
        msg2 = bytearray(msg); msg2[1024 * i:1024 * i + 64] = Xp
        wX = struct.unpack("<16I", X); wXp = struct.unpack("<16I", Xp)
        def patched(cv, words, counter, block_len, flags, rounds):
            if tuple(cv) == IV and tuple(words) == wXp and counter == i and flags & 1:
                return real(cv, wX, counter, block_len, flags, rounds)
            return real(cv, words, counter, block_len, flags, rounds)
        b3._compress = patched
        ok += b3.blake3(bytes(msg), 2) == b3.blake3(bytes(msg2), 2)
        b3._compress = real
        differ_unpatched += b3.blake3(bytes(msg), 2) != b3.blake3(bytes(msg2), 2)
    print(f"E. planted first-block collision in chunk i (1..8), chunks after it allowed: digests equal {ok}/{n};"
          f" unpatched digests differ {differ_unpatched}/{n}")

if __name__ == "__main__":
    t0 = time.time()
    partA(); partB(); partC(); partD(); partE()
    print(f"done in {time.time() - t0:.1f} s")
