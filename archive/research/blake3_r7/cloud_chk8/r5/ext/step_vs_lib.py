"""External check (not shipped): the rolled bit-sliced step vs the blake3 library (pip blake3 1.0.11) on 64-byte messages 0^32 || x.  usage: step_vs_lib.py <experiments dir> <lib dir>"""
import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1]); sys.path.insert(1, sys.argv[2])
import bsrho as b, blake3 as lib
st = b.step256(); rnd = random.Random(99); bad = tot = 0
for _ in range(32):
    xs = [rnd.getrandbits(256) for _ in range(256)]
    out = b.lanes_of(list(st.step(*b.pack_lanes(xs, 256, st.pin))), 256, st.pin)
    for l in range(256):
        tot += 1
        bad += out[l] ^ st.qint != int.from_bytes(lib.blake3(b.message(xs[l])).digest(), "little")
print("rolled step: %d lanes vs blake3 library (7 rounds, 0^32 || x): %d differences" % (tot, bad))
