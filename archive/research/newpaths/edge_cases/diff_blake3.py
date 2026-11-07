"""Differential test: independent BLAKE3 (my_blake3) vs organizer copy (org_blake3).
Local only. Run: python -B diff_blake3.py
"""
import hashlib, os, random, struct, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import my_blake3 as mine
import org_blake3 as org

random.seed(20261008)
fails = []
counts = {}


def note(section, ok, detail):
    counts.setdefault(section, [0, 0])
    counts[section][0] += 1
    if not ok:
        counts[section][1] += 1
        fails.append((section, detail))


# ---------- A. official vectors at 7 rounds ----------
EMPTY = "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
ABC = "6437b3ac38465133ffb63b75273a8db548c558465d79db03fd359c6cd5bd9d85"
print("A mine(empty,7) =", mine.blake3(b"", 7).hex(), mine.blake3(b"", 7).hex() == EMPTY)
print("A org (empty,7) =", org.blake3(b"", 7).hex(), org.blake3(b"", 7).hex() == EMPTY)
print("A mine(abc,7) matches remembered vector:", mine.blake3(b"abc", 7).hex() == ABC,
      "org:", org.blake3(b"abc", 7).hex() == ABC)
note("A", mine.blake3(b"", 7).hex() == EMPTY, "mine empty vector")
note("A", org.blake3(b"", 7).hex() == EMPTY, "org empty vector")


# ---------- B. full-message differential ----------
def patterns(n):
    yield "i%251", bytes(i % 251 for i in range(n))
    yield "zero", bytes(n)
    yield "ff", b"\xff" * n
    yield "rand", random.randbytes(n)


lengths = {0, 1, 2, 3, 4, 5, 31, 32, 33, 55, 56, 63, 64, 65, 127, 128, 129,
           960, 961, 1022, 1023, 1024, 1025, 1088, 2047, 2048, 2049,
           3071, 3072, 3073, 4095, 4096, 4097, 5120, 7168, 8192}
lengths |= {random.randrange(0, 9000) for _ in range(60)}
t = time.time()
for n in sorted(lengths):
    for r in range(1, 8):
        for name, data in patterns(n):
            a, b = mine.blake3(data, r), org.blake3(data, r)
            note("B-len", a == b, f"len={n} rounds={r} pat={name}")
print(f"B lengths x rounds 1..7 x 4 patterns done in {time.time()-t:.1f}s")

t = time.time()
for k in range(0, 11):  # chunk counts 2^k-1, 2^k, 2^k+1 (up to 1025 chunks = 1 MiB)
    for c in {max(1, (1 << k) - 1), 1 << k, (1 << k) + 1}:
        for n in {c * 1024 - 1, c * 1024, c * 1024 + 1}:
            for name, data in list(patterns(n))[::3] if k >= 8 else patterns(n):
                a, b = mine.blake3(data, 2), org.blake3(data, 2)
                note("B-chunks", a == b, f"chunks~{c} len={n} rounds=2 pat={name}")
print(f"B chunk-count boundaries (k<=10) at rounds=2 done in {time.time()-t:.1f}s")


# ---------- C. compression level at huge counters ----------
COUNTERS = [0, 1, 2**31, 2**32 - 2, 2**32 - 1, 2**32, 2**32 + 1, 2**33 - 1, 2**33,
            2**40 + 12345, 2**51 - 2, 2**51 - 1]  # 2^51-1 = last reachable chunk index (len < 2^61)
for ctr in COUNTERS:
    for size in (0, 1, 63, 64, 65, 1023, 1024):
        for r in range(1, 8):
            chunk = random.randbytes(size)
            o = org._compress(*org._chunk_output(chunk, ctr, r), r)[:8]
            cs = mine.ChunkState(ctr, lambda cv, w, c, bl, f: mine.real_compress(cv, w, c, bl, f, r))
            cs.update(chunk)
            m = cs.output().chaining_value(cs.C)
            note("C-counter", list(o) == list(m), f"counter={ctr} size={size} rounds={r}")
# beyond-reachable counters: organizer does not mask the high word
for ctr in (2**64 - 1, 2**64, 2**65 + 3):
    try:
        o = org._compress(*org._chunk_output(b"x" * 100, ctr, 2), 2)[:8]
        if ctr < 2**64:
            cs = mine.ChunkState(ctr, lambda cv, w, c, bl, f: mine.real_compress(cv, w, c, bl, f, 2))
            cs.update(b"x" * 100)
            same = list(o) == list(cs.output().chaining_value(cs.C))
            print(f"C counter={ctr:#x}: equal={same}")
        else:
            wide = any(x >> 32 for x in o)
            print(f"C counter={ctr:#x} (UNREACHABLE via blake3()): org returns words wider than 32 bits: {wide}")
    except Exception as e:
        print(f"C counter={ctr:#x}: org raised {type(e).__name__}: {e}")


# ---------- D. tree logic with a fast stand-in compression ----------
def stand_in(cv, words, counter, block_len, flags, rounds=None):
    raw = struct.pack("<8I16IQII", *cv, *words, counter, block_len, flags)
    d = hashlib.blake2b(raw, digest_size=64).digest()
    return struct.unpack("<16I", d)


real_org_compress = org._compress
org._compress = stand_in
t = time.time()
try:
    chunk_counts = set(range(1, 300))
    for k in range(9, 15):  # up to 2^14+1 chunks = 16 MiB
        chunk_counts |= {(1 << k) - 1, 1 << k, (1 << k) + 1}
    chunk_counts |= {3 * 1024 + 7, 5 * 1024 - 1}
    base = random.randbytes(((1 << 14) + 1) * 1024 + 2)
    for c in sorted(chunk_counts):
        for n in {c * 1024 - 1, c * 1024, c * 1024 + 1} - {-1}:
            data = base[:n]
            a = mine.Hasher(compress=lambda cv, w, ct, bl, f: stand_in(cv, w, ct, bl, f)).update(data).digest()
            b = org.blake3(data, 2)
            note("D-tree", a == b, f"stand-in tree: chunks~{c} len={n}")
finally:
    org._compress = real_org_compress
print(f"D tree logic (stand-in compress) done in {time.time()-t:.1f}s")


# ---------- E. argument guards ----------
for label, call in [("rounds=0", lambda: org.blake3(b"", 0)), ("rounds=8", lambda: org.blake3(b"", 8)),
                    ("rounds=True", lambda: org.blake3(b"", True)), ("rounds=2.0", lambda: org.blake3(b"", 2.0)),
                    ("rounds=-1", lambda: org.blake3(b"", -1)),
                    ("bytearray", lambda: org.blake3(bytearray(b"a"), 2)), ("str", lambda: org.blake3("a", 2)),
                    ("memoryview", lambda: org.blake3(memoryview(b"a"), 2))]:
    try:
        out = call()
        print(f"E {label}: ACCEPTED -> {out.hex()[:16]}")
    except Exception as e:
        print(f"E {label}: rejected ({type(e).__name__})")


class Sub(bytes):
    pass


print("E bytes subclass accepted and equal:", org.blake3(Sub(b"abc"), 2) == org.blake3(b"abc", 2))

print()
for s, (n, f) in counts.items():
    print(f"{s}: {n} comparisons, {f} differ")
print("FIRST DIFFS:", fails[:10] if fails else "none")
