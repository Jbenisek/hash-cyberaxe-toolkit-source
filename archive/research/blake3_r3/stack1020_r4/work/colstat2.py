import sys, importlib.util
from collections import Counter
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("b", "../pkg/blake3/experiments/bsrho.py"); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
C = Counter()
def add3(self, A, B, Cc):
    s = [None] * 32
    n0 = len(self.nodes); s[0], U = self.fa(A[0], B[0], Cc[0]); C["bit0 gates %d" % (len(self.nodes) - n0)] += 1
    u = b.ZERO
    for i in range(1, 31):
        a, bb, c, best = A[i], B[i], Cc[i], None
        for o in ((a, bb, c), (a, c, bb), (bb, a, c), (bb, c, a), (c, a, bb), (c, bb, a)):
            for tm in (0, 1, 2):
                n0, h0 = len(self.nodes), self.hits
                self._col(*o, u, U, tm, i == 30)
                k = len(self.nodes) - n0
                for nd in self.nodes[n0:]:
                    del self.memo[nd]
                del self.nodes[n0:]
                self.hits = h0
                if best is None or k < best[0]:
                    best = (k, o, tm)
        ins = best[1] + (u, U); key = (sum(t[1] << j for j, t in enumerate(ins)), int(i == 30))
        form = "lib" if best[2] == 2 and key in b.COLLIB else "t%d" % (0 if best[2] == 2 else best[2])
        C["bit%s %s %d" % ("1" if i == 1 else "30" if i == 30 else "mid", form, best[0])] += 1
        s[i], u, U = self._col(*best[1], u, U, best[2], i == 30)
    n0 = len(self.nodes); s[31] = self.XOR(self.XOR(self.XOR(A[31], B[31]), Cc[31]), U); C["bit31 gates %d" % (len(self.nodes) - n0)] += 1
    return s
b.Gen.add3 = add3
g, out = b.trace(256)
for k, v in sorted(C.items()): print(k, v)
print("live", len(b.used_gates(g, out)))
