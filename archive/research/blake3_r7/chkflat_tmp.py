import sys, hashlib
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import bsrho as b
st = b.step256()
fl = st.flat
print(type(fl), len(fl), fl[0], fl[-1])
lines = ["%s %d %d %d" % (op, d & 0xFFFF, a & 0xFFFF, bb & 0xFFFF) for (op, d, a, bb) in fl]
print(hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest(), st.regs, st.instr)
