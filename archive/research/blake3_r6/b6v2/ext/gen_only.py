"""Runs only the circuit generator of the shipped program (trace, dead-code elimination, emission, register allocation) for n = 256; no search."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import bsrho as b
st = b.Step(256)
code, regs = b.allocate(st)
print("gates", st.ops, "registers", regs, "instructions", len(code))
