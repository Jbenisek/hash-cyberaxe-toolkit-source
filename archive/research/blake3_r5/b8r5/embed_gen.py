"""Embeds gen_c/gen.c into pkg/blake3/experiments/bsrho.py as GEN_C (section 9), after checking its defaults against the Python model.  usage: python -B embed_gen.py"""
import sys, os, re
sys.dont_write_bytecode = True
H = os.path.dirname(os.path.abspath(__file__))
X = os.path.join(H, "pkg", "blake3", "experiments")
sys.path.insert(0, X)
import bsrho as b
st = b.step256()
ph, filt, body, code, tmax = b.machine_constants(st)
c = open(os.path.join(H, "gen_c", "gen.c"), encoding="utf-8", newline="").read()
assert "'''" not in c
m1 = re.search(r"#define NMAX (\d+)", c); m2 = re.search(r"#define CODE_BYTES (\d+)", c)
assert int(m1.group(1)) == st.L["nodes"] + 1, (m1.group(1), st.L["nodes"])
assert int(m2.group(1)) == code, (m2.group(1), code)
for nm, val in (("KPRE", b.KPRE), ("SB", b.SB), ("WB", b.WB), ("TB", b.TB)):
    assert "#define %s %d" % (nm, val) in c, nm
p = os.path.join(X, "bsrho.py")
s = open(p, encoding="utf-8", newline="").read()
i = s.index("# -------- 9 the circuit generator in C")
j = s.index('if __name__ == "__main__":')
head = """# -------- 9 the circuit generator in C
# The generator of sections 3 and 4 (pivot adder, rolled listing, register allocation) in freestanding C, two passes per segment, no node table (no segment has a shared or
# a dead gate).  Compiled to WebAssembly (clang -Os) and run with 16 pages (1,048,576 bytes) of guest memory it emits the same listing as listing() (proof 3.6).  `--gen-c` prints it.
GEN_C = r'''"""
s = s[:i] + head + c + "'''\n\n\n" + s[j:]
open(p, "w", encoding="utf-8", newline="").write(s)
print("embedded", len(c), "bytes; NMAX", st.L["nodes"] + 1, "CODE_BYTES", code, "bsrho.py", len(s.encode()))
