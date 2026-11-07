"""Reference program of the Python generator (Step + allocate) for the C port to match: ref_program.txt (one line per instruction: op dst a b), ref_summary.txt."""
import sys, os, hashlib
sys.dont_write_bytecode = True
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, "..", "pkg", "blake3", "experiments"))
import bsrho as b
st = b.Step(256)
code, regs = b.allocate(st)
lines = []
for (nm, d, ra, rb) in code:
    lines.append("%s %d %d %d" % (st.opsym[nm][0], d, ra, rb))
txt = "\n".join(lines) + "\n"
open(os.path.join(H, "ref_program.txt"), "w", newline="\n").write(txt)
g = b.trace(256)[0]
open(os.path.join(H, "ref_summary.txt"), "w", newline="\n").write(
    "instructions %d\nregisters %d\nsha256 %s\nnodes %d\ngenerator_calls %d\nq_hex %064x\n" % (
        len(code), regs, hashlib.sha256(txt.encode()).hexdigest(), len(g.nodes), 2 * st.gen_calls, st.qint))
print(open(os.path.join(H, "ref_summary.txt")).read())
