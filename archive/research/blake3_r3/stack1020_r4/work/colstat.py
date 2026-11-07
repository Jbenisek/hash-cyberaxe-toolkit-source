import sys, importlib.util
from collections import Counter
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("b", "../pkg/blake3/experiments/bsrho.py"); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
C = Counter(); n3 = [0]
oc = b.Gen._col; oa = b.Gen.add3
def add3(self, A, B, Cc):
    n3[0] += 1; self._final = True; return oa(self, A, B, Cc)
b.Gen.add3 = add3
# count final column choices: wrap _col, a call made after the 18 dry trials is the kept one: detect by nodes kept
def col(self, x, y, z, u, U, tm, oU):
    n0 = len(self.nodes); r = oc(self, x, y, z, u, U, tm, oU); self._last = (tm, len(self.nodes) - n0, oU, (sum(t[1] << i for i, t in enumerate((x, y, z, u, U))), int(oU)) in b.COLLIB); return r
b.Gen._col = col
g, out = b.trace(256)
print("three-addend sums", n3[0])
