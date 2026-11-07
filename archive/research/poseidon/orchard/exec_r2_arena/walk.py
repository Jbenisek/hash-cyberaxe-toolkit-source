# allocator walk: replay an ATRACE file (A bytes off / F 0 off / S bytes off) under lowest-address first fit, 64-byte header, payload rounded to 32.
# prints the high-water mark and the live set at it.  usage: python walk.py trace.txt [twmove]
import sys
def need(b): return 64 + ((b + 31) & ~31)
ops = [l.split() for l in open(sys.argv[1])]
mode = sys.argv[2] if len(sys.argv) > 2 else ''
live = {}   # trace off -> (sim off, len, bytes, idx)
blocks = [] # sorted (off, len)
hw = 0; hwset = None; i_hw = -1
def place(n):
    at = 0
    for (o, l) in blocks:
        if o - at >= n: break
        at = o + l
    return at
for i, (op, b, off) in enumerate(ops):
    b = int(b)
    if op == 'A':
        n = need(b); at = place(n); blocks.append((at, n)); blocks.sort(); live[off] = (at, n, b, i)
        top = max(o + l for o, l in blocks)
        if top > hw: hw = top; hwset = sorted((v[0], v[2], v[3]) for v in live.values()); i_hw = i
    elif op == 'F':
        at, n, bb, _ = live.pop(off); blocks.remove((at, n))
    elif op == 'S':
        at, n, bb, k = live[off]; blocks.remove((at, n)); n2 = need(b); blocks.append((at, n2)); blocks.sort(); live[off] = (at, n2, b, k)
print('ops', len(ops), 'highwater', hw, 'at op', i_hw, 'live', len(hwset), 'payload', sum(x[1] for x in hwset))
for x in hwset: print('  off', x[0], 'bytes', x[1], 'alloc#', x[2])
