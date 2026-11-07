"""External check (not shipped): program vs organizer verifier/blake3.py at 3 rounds on messages KEY || x.  usage: ref_check.py <repo> <experiments>"""
import sys, random, importlib.util
sys.dont_write_bytecode = True
V, X = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("ref_blake3", V + "/verifier/blake3.py"); ref = importlib.util.module_from_spec(spec); spec.loader.exec_module(ref)
sys.path.insert(0, X); import bsrho as b
rnd = random.Random(20261020)
R = lambda x: int.from_bytes(ref.blake3(b.message(x), 3), "little")
xs = [rnd.getrandbits(256) for _ in range(2048)]
print("scalar f(x) vs organizer blake3(KEY || x, 3), 2048 x: %d differences" % sum(b.f_scalar(x, 256) != R(x) for x in xs))
st = b.step256(); bad = 0
for k in range(8):
    ys = xs[256 * k:256 * k + 256]
    out = b.lanes_of(list(st.step(*b.pack_lanes(ys, 256, st.pin))), 256, st.pin)
    bad += sum((out[l] ^ st.qint) != R(ys[l]) for l in range(256))
print("bit-sliced step (stored planes XOR q) vs organizer, 2048 lanes: %d differences" % bad)
bad = 0
for k in range(64):
    ys = xs[7 * k:7 * k + 7]
    bad += sum((g ^ st.qint) != R(y) for g, y in zip(b.packed_f(ys, 256, st.qwords), ys))
print("packed recovery circuit vs organizer, 448 values: %d differences" % bad)
print("message prefix KEY:", b.message(0)[:32].hex())
