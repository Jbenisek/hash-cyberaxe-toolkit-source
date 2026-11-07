# allocator walk with several placement policies on an ATRACE file; prints high-water for each.
# usage: python walk2.py trace.txt
import sys, bisect
def need(b): return 64 + ((b + 31) & ~31)
ops = []
for l in open(sys.argv[1]):
    op, b, off = l.split(); ops.append((op, int(b), off))

def run(policy, H=None, thr=None):
    blocks = []; live = {}; hw = 0
    for op, b, off in ops:
        if op == 'T' or (op == 'A' and policy == 'role'):
            n = need(b); at = 0; gaps = []
            for (o, l) in blocks:
                if o - at >= n: gaps.append((at, o - at))
                at = o + l
            if H - at >= n: gaps.append((at, H - at))
            if not gaps: return None
            pos = (gaps[-1][0] + gaps[-1][1] - n) if op == 'T' else gaps[0][0]
            bisect.insort(blocks, (pos, n)); live[off] = (pos, n); hw = max(hw, pos + n)
        elif op == 'A':
            n = need(b); gaps = []; at = 0
            for (o, l) in blocks:
                if o - at >= n: gaps.append((at, o - at))
                at = o + l
            end = H if H is not None else None
            if end is None: gaps.append((at, 1 << 62))
            elif end - at >= n: gaps.append((at, end - at))
            if not gaps: return None
            if policy == 'ff': g = gaps[0]; pos = g[0]
            elif policy == 'bf': g = min(gaps, key=lambda x: (x[1], x[0])); pos = g[0]
            elif policy == 'bi':   # blocks >= thr placed at the highest fitting position, others first fit
                if b >= thr: g = gaps[-1]; pos = g[0] + g[1] - n
                else: pos = gaps[0][0]
            elif policy == 'bibf':
                if b >= thr: g = gaps[-1]; pos = g[0] + g[1] - n
                else: g = min(gaps, key=lambda x: (x[1], x[0])); pos = g[0]
            bisect.insort(blocks, (pos, n)); live[off] = (pos, n)
            hw = max(hw, pos + n)
        elif op == 'F':
            blocks.remove(live.pop(off))
        else:
            pos, n = live[off]; blocks.remove((pos, n)); n2 = need(b); bisect.insort(blocks, (pos, n2)); live[off] = (pos, n2)
    return hw
for p in ([] if sys.argv[2] == "search" else sys.argv[2:]):
    if p in ('ff', 'bf'): print(p, run(p)); continue
    pol, thr, H = p.split(':'); print(p, run(pol, int(H), int(thr)))
if len(sys.argv) > 2 and sys.argv[2] == 'search':
    pol, thr = sys.argv[3], int(sys.argv[4]); lo, hi = 30000000, 44307744
    while hi - lo > 4096:
        mid = (lo + hi) // 2 // 32 * 32
        r = run(pol, mid, thr)
        if r is None: lo = mid
        else: hi = mid
    print('search', pol, thr, 'feasible H', hi, flush=True)
