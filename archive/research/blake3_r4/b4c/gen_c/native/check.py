import sys, struct, hashlib, os
H = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(H, sys.argv[1] if len(sys.argv) > 1 else "o.bin"), "rb").read()
f = struct.unpack("<9I", raw[:36]); q = raw[36:68]
ninst, nreg, nodes, calls, err = f[:5]
rec = raw[68:]
assert len(rec) == 36 * ninst, (len(rec), ninst)
lines = []
for k in range(ninst):
    r = rec[36 * k:36 * k + 36]
    d, a, b = struct.unpack("<HHH", r[1:7]); assert not any(r[7:])
    lines.append("%s %d %d %d" % (chr(r[0]), d, a, b))
txt = "\n".join(lines) + "\n"
ref = dict(l.split() for l in open(os.path.join(H, "..", "ref_summary.txt")))
print("native: ninst", ninst, "nreg", nreg, "nodes", nodes, "calls", calls, "err", err, "q equal", format(int.from_bytes(q, "little"), "064x") == ref["q_hex"],
      "program sha256 equal to the Python reference:", hashlib.sha256(txt.encode()).hexdigest() == ref["sha256"], "ref lines equal:", txt == open(os.path.join(H, "..", "ref_program.txt")).read())
