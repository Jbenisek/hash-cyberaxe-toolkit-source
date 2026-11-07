"""Reference listing of the Python generator (rolled_ref.listing) for the C port to match: ref_program.txt (one line per instruction: op dst a b, none = 65535), ref_summary.txt."""
import sys, os, hashlib
sys.dont_write_bytecode = True
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, ".."))
import rolled_ref as r
L = r.listing(256)
lines = ["%s %d %d %d" % (op, d & 0xFFFF, a & 0xFFFF, b & 0xFFFF) for (op, d, a, b) in L["flat"]]
txt = "\n".join(lines) + "\n"
open(os.path.join(H, "ref_program.txt"), "w", newline="\n").write(txt)
open(os.path.join(H, "ref_summary.txt"), "w", newline="\n").write(
    "instructions %d\nregisters %d\nsha256 %s\nnodes %d\ngenerator_calls %d\nq_hex %064x\n" % (
        len(lines), L["regs"], hashlib.sha256(txt.encode()).hexdigest(), L["nodes"], 2 * sum(L["g"]), 0))
print(open(os.path.join(H, "ref_summary.txt")).read())
