"""External check (not shipped): decode the 5-byte records written by the C generator (static binary, output file), run them as a bit-sliced program
on 256 lanes and compare every lane with the organizer reference blake3(M, 6) (g = f XOR q).  usage: exec_records.py <organizer-dir> <experiments-dir> <gen output file>"""
import sys, random, struct, importlib.util
sys.dont_write_bytecode = True
V, X, F = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("ref_blake3", V + "/verifier/blake3.py"); ref = importlib.util.module_from_spec(spec); spec.loader.exec_module(ref)
sys.path.insert(0, X); import bsrho as b
raw = open(F, "rb").read()
f = struct.unpack("<9I", raw[:36]); q = int.from_bytes(raw[36:68], "little")
ninst, nreg = f[0], f[1]; rec = raw[68:]
assert len(rec) == 5 * ninst and f[4] == 0
prog = []
for k in range(ninst):
    r = rec[5 * k:5 * k + 5]; w = struct.unpack("<I", r[1:5])[0]
    assert w >> 30 == 0
    prog.append((chr(r[0]), w & 1023, (w >> 10) & 1023, (w >> 20) & 1023))
st = b.step256(); assert q == st.qint and ninst == st.ops
rnd = random.Random(20261016); bad = tot = 0
for _ in range(32):
    xs = [rnd.getrandbits(256) for _ in range(256)]
    pl = list(b.pack_lanes(xs, 256, st.pin)); regs = pl + [0] * (nreg - 256)
    for op, d, a, c in prog:
        x, y = regs[a], regs[c]
        regs[d] = x ^ y if op == "^" else x & y if op == "&" else x | y
    out = b.lanes_of(regs[:256], 256, st.pin)
    for l in range(256):
        tot += 1
        bad += out[l] != int.from_bytes(ref.blake3(b.message(xs[l]), 6), "little") ^ q
print("5-byte records decoded from the generator output (%d records, %d registers): %d lanes vs organizer blake3(M,6): %d differences" % (ninst, nreg, tot, bad))
