'''Bit-level structural cone of the single check of the E3-fixed design (pkg13/mitm/bits/BITS.md method): additions as
carry chains (bit i of a sum reads bits 0..i of every operand), XOR bitwise, rotations permute.  For each of the 32 check
bits: which of the 32 bits of g it reads.  If every check bit reads all 32, a bit-serial guess-and-determine (any bit
order, carries in the state) cannot test anything before all 32 bits are fixed: 2^32 leaves per solve.'''
import sys
sys.dont_write_bytecode = True
from ev import Design, DESIGN, REL, M
d = Design(*DESIGN)
Z = [frozenset()] * 32
def rolc(x, r): return [x[(i - r) % 32] for i in range(32)]
def xorc(*xs): return [frozenset().union(*(x[i] for x in xs)) for i in range(32)]
def addc(*xs):
    out, acc = [], frozenset()
    for i in range(32):
        acc = acc.union(*(x[i] for x in xs)); out.append(acc)
    return out
val = {d.g: [frozenset([i]) for i in range(32)]}
def get(w): return val.get(w, Z)
def solve_c(r, u):
    if r[0] == 'add': return addc(*(get(w) for w in r[1] if w != u))
    ru = next(k for w, k in r[1] if w == u)
    x = xorc(*(rolc(get(w), k) for w, k in r[1] if w != u))
    return rolc(x, (32 - ru) % 32)
for i, w in d.loop: val[w] = solve_c(REL[i], w)
r = REL[d.chk]
chk = addc(*(get(w) for w in r[1])) if r[0] == 'add' else xorc(*(rolc(get(w), k) for w, k in r[1]))
sizes = [len(c) for c in chk]
print('check', r[3], 'cone sizes over the 32 g bits, per check bit 0..31:', sizes)
print('min cone', min(sizes), 'max cone', max(sizes))
for w in ('C1.c1', 'Y13', 'Y1', 'C1.a1', 'X12', 'Y0'):
    print('  word %-6s min/max cone %d/%d' % (w, min(len(c) for c in val[w]), max(len(c) for c in val[w])))
