import sys, struct, hashlib, os
H = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(H, sys.argv[1] if len(sys.argv) > 1 else "o.bin"), "rb").read()
f = struct.unpack("<9I", raw[:36]); q = raw[36:68]
ninst, nreg, nodes, calls, err = f[:5]
rec = raw[68:]
lines, off = [], 0
for k in range(ninst):
    op = chr(rec[off])
    if op == "?":
        w = int.from_bytes(rec[off + 1:off + 6], "little"); off += 6; assert w >> 40 == 0
        lines.append("? %d %d %d %d" % (w & 1023, (w >> 10) & 1023, (w >> 20) & 1023, (w >> 30) & 1023))
    else:
        w = struct.unpack("<I", rec[off + 1:off + 5])[0]; off += 5; assert w >> 30 == 0
        lines.append("%s %d %d %d" % (op, w & 1023, (w >> 10) & 1023, (w >> 20) & 1023))
assert off == len(rec), (off, len(rec))
txt = "\n".join(lines) + "\n"
ref = dict(l.split() for l in open(os.path.join(H, "..", "ref_summary.txt")))
print("native: ninst", ninst, "nreg", nreg, "nodes", nodes, "calls", calls, "err", err, "q equal", format(int.from_bytes(q, "little"), "064x") == ref["q_hex"],
      "program sha256 equal to the Python reference:", hashlib.sha256(txt.encode()).hexdigest() == ref["sha256"], "ref lines equal:", txt == open(os.path.join(H, "..", "ref_program.txt")).read())
