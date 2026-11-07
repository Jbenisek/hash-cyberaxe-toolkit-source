"""External regression (not shipped): the shipped bit-sliced step vs the organizer reference verifier/blake3.py blake3(M, 4) on 8,192 random messages
M = 0^32 || x (64 bytes), full 256-bit digest, one step and 4 chained steps; plus the packed recovery circuit and the scalar digest."""
import sys, random, importlib.util
sys.dont_write_bytecode = True
V = sys.argv[1]
spec = importlib.util.spec_from_file_location("ref_blake3", V + "/verifier/blake3.py"); ref = importlib.util.module_from_spec(spec); spec.loader.exec_module(ref)
sys.path.insert(0, sys.argv[2]); import bsrho as b
rnd = random.Random(20261014)
st = b.step256()
def refg(x): return int.from_bytes(ref.blake3(b.message(x), b.ROUNDS), "little")
bad = 0; tot = 0
for _ in range(32):
    xs = [rnd.getrandbits(256) for _ in range(256)]
    out = b.lanes_of(list(st.step(*b.pack_lanes(xs, 256, st.pin))), 256, st.pin)
    for l in range(256):
        tot += 1
        if out[l] != refg(xs[l]) ^ st.qint: bad += 1
print("one step: %d lanes vs organizer blake3(M,4): %d differences" % (tot, bad))
bad = 0; tot = 0
for _ in range(16):
    xs = [rnd.getrandbits(256) for _ in range(256)]
    pl = b.pack_lanes(xs, 256, st.pin); cur = list(xs)
    for _ in range(4):
        pl = list(st.step(*pl)); cur = [refg(x) ^ st.qint for x in cur]
    bad += sum(1 for u, v in zip(b.lanes_of(pl, 256, st.pin), cur) if u != v); tot += 256
print("4 chained steps: %d lanes (16 x 256) vs organizer blake3(M,4): %d differences" % (tot, bad))
xs = [rnd.getrandbits(256) for _ in range(7 * 64)]; bad = 0
for i in range(0, len(xs), 7):
    got = b.packed_f(xs[i:i+7], 256, st.qwords)
    bad += sum(1 for x, y in zip(xs[i:i+7], got) if y != refg(x) ^ st.qint)
print("packed recovery circuit: %d messages vs organizer: %d differences" % (len(xs), bad))
bad = sum(1 for _ in range(300) if (lambda x: b.f_scalar(x, 256) != refg(x))(rnd.getrandbits(256)))
print("scalar digest_words: 300 messages vs organizer: %d differences" % bad)
