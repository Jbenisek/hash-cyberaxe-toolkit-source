#!/usr/bin/env python3
"""cmp_shift.py REF.pair REFSHIFT FILE.pair SHIFT [FILE SHIFT ...]: expand each pair to 48 words, print the signed-difference rows
of each file and, for every row t of the reference, whether file row t+SHIFT-REFSHIFT carries the same signed difference string."""
import sys
M = 0xffffffff
def Rr(x, n): return ((x >> n) | (x << (32 - n))) & M
def expand(w, R=48):
    W = list(w)
    for t in range(16, R):
        s0 = Rr(W[t-15], 7) ^ Rr(W[t-15], 18) ^ (W[t-15] >> 3); s1 = Rr(W[t-2], 17) ^ Rr(W[t-2], 19) ^ (W[t-2] >> 10)
        W.append((W[t-16] + s0 + W[t-7] + s1) & M)
    return W
sg = lambda x, y: ''.join('-' if ((x >> i) & 1) == ((y >> i) & 1) else ('u' if (x >> i) & 1 else 'n') for i in range(31, -1, -1))
def load(pf):
    m = {}
    for ln in open(pf):
        p = ln.split()
        if p and p[0] in ('M1', 'M2'): m[p[0]] = [int(x, 16) for x in p[1:17]]
    return expand(m['M1']), expand(m['M2'])
args = sys.argv[1:]
ref, rs = load(args[0]), int(args[1])
refd = {t: sg(ref[0][t], ref[1][t]) for t in range(48) if ref[0][t] != ref[1][t]}
print('REF', args[0].split('/')[-1], 'diff rows', sorted(refd))
for i in range(2, len(args), 2):
    X, s = load(args[i]), int(args[i+1]); d = {t: sg(X[0][t], X[1][t]) for t in range(48) if X[0][t] != X[1][t]}
    same = [t for t in refd if refd[t] == d.get(t + s - rs)]
    print(args[i].split('/')[-1], 'shift', s, 'diff rows', sorted(d))
    print('   same signed diff as REF (row->row+%d):' % (s - rs), same, 'of', len(refd), '; extra rows:', sorted(set(d) - {t + s - rs for t in refd}))
