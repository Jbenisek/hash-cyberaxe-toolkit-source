"""Embeds gen_c/gen.c into pkg/blake3/experiments/bsrho.py as GEN_C (section 9), after checking its defaults against the Python model.
usage: python -B embed_gen.py"""
import sys, os, re
sys.dont_write_bytecode = True
H = os.path.dirname(os.path.abspath(__file__))
X = os.path.join(H, "pkg", "blake3", "experiments")
sys.path.insert(0, X)
import bsrho as b
st = b.step256()
ph, filt, body, code, tmax = b.machine_constants(st)
nodes = len(b.trace(256)[0].nodes)
c = open(os.path.join(H, "gen_c", "gen.c"), encoding="utf-8", newline="").read()
assert "'''" not in c
m1 = re.search(r"#define NMAX (\d+)", c); m2 = re.search(r"#define CODE_BYTES (\d+)", c)
assert int(m1.group(1)) == nodes, (m1.group(1), nodes)
assert int(m2.group(1)) == code, (m2.group(1), code)
assert "#define ROUNDS %d" % b.ROUNDS in c
p = os.path.join(X, "bsrho.py")
s = open(p, encoding="utf-8", newline="").read()
i = s.index("# ---------------------------------------------------------------- 9 the circuit generator in C")
j = s.index('if __name__ == "__main__":')
head = """# ---------------------------------------------------------------- 9 the circuit generator in C
# The generator of section 3 and 4 (pivot adder, register allocation) written in freestanding C in two passes without a node table (this circuit has no shared
# and no dead gate: the reference generator Gen/Step finds none).  It was compiled to WebAssembly (clang -Os) and run in a sandbox with 16 pages (1,048,576
# bytes) of guest memory: it emits the same program as Step/allocate (proof 3.6).  `--gen-c` prints it.
GEN_C = r'''"""
s = s[:i] + head + c + "'''\n\n\n" + s[j:]
open(p, "w", encoding="utf-8", newline="").write(s)
print("embedded", len(c), "bytes; NMAX", nodes, "CODE_BYTES", code)
