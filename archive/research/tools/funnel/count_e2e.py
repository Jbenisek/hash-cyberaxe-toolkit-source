#!/usr/bin/env python3
"""count_e2e.py CHAR.xml [CHAR.xml ...] : per file, owner_count STATE+W and wcost PASTFREE+WEXP.
Prints FLAG_UNDER_250 when owner_count TOTAL < 250 and the file has no '?' bits."""
import sys, re
import numpy as np

# ---- owner_count ----
def oc_rows_of(x):
    m = re.search(r'<char value="(.*?)"/>', x, re.S)
    n = int(re.search(r'name="n" value="(\d+)"', x).group(1))
    out = []
    for line in m.group(1).strip().split('\n'):
        mm = re.match(r'\s*(-?\d+)\s+A:\s*(\S{32})\s+E:\s*(\S{32})(?:\s+W:\s*(\S{32}))?', line)
        if mm:
            out.append((int(mm.group(1)), mm.group(2), mm.group(3), mm.group(4)))
    return n, out

V = set('01'); D = set('unx')
def owner_count(f):
    n, rows = oc_rows_of(open(f).read())
    sv = sd = wv = wd = q = 0
    for t, a, e, w in rows:
        for s in (a, e):
            sv += sum(c in V for c in s); sd += sum(c in D for c in s); q += s.count('?')
        if w and t < 16:
            wv += sum(c in V for c in w); wd += sum(c in D for c in w); q += w.count('?')
    state = sv + sd; W = wv + wd; total = state + W
    return state, W, total, q

# ---- wcost ----
NS = 1 << 20
rng = np.random.default_rng(1)
def wc_parse(f):
    txt = open(f).read()
    n = int(re.search(r'name="n" value="(\d+)"', txt).group(1))
    rows = {int(m.group(1)): (m.group(2), m.group(3), m.group(4) or '-' * 32)
            for m in re.finditer(r'^\s*(-?\d+)\s+A:\s*(\S+)\s+E:\s*(\S+)(?:[ \t]+W:\s*(\S+))?', txt, re.M)}
    return n, rows
def masks(p):
    m = {c: 0 for c in '-01unx'}
    for j, ch in enumerate(p):
        m[ch if ch in m else '-'] |= 1 << (31 - j)
    return m
def sample(p):
    m = masks(p)
    r = rng.integers(0, 1 << 32, NS, dtype=np.uint64).astype(np.uint32)
    x = (r & np.uint32(m['-'] | m['x'])) | np.uint32(m['1'] | m['u'])
    xp = (r & np.uint32(m['-'])) | np.uint32(m['1'] | m['n']) | (~r & np.uint32(m['x']))
    return x, xp
def rotr(x, k): return (x >> np.uint32(k)) | (x << np.uint32(32 - k))
s0 = lambda x: rotr(x, 7) ^ rotr(x, 18) ^ (x >> np.uint32(3))
s1 = lambda x: rotr(x, 17) ^ rotr(x, 19) ^ (x >> np.uint32(10))
def match(p, x, xp):
    m = masks(p)
    eq = np.uint32(m['-'] | m['0'] | m['1']); ok = ((x ^ xp) & eq) == 0
    ok &= (x & np.uint32(m['0'])) == 0; ok &= (x & np.uint32(m['1'])) == np.uint32(m['1'])
    ok &= (x & np.uint32(m['u'])) == np.uint32(m['u']); ok &= (xp & np.uint32(m['u'])) == 0
    ok &= (x & np.uint32(m['n'])) == 0; ok &= (xp & np.uint32(m['n'])) == np.uint32(m['n'])
    ok &= ((x ^ xp) & np.uint32(m['x'])) == np.uint32(m['x'])
    return int(ok.sum())
def wcost(f, lo=16):
    n, R = wc_parse(f)
    pf = sum(sum((R[t][0] + R[t][1]).count(c) for c in '01unx') for t in R if t >= lo)
    wexp = 0.0
    with np.errstate(over='ignore'):
        for t in range(lo, n):
            v = {s: sample(R[s][2]) for s in (t - 2, t - 7, t - 15, t - 16)}
            x = s1(v[t - 2][0]) + v[t - 7][0] + s0(v[t - 15][0]) + v[t - 16][0]
            xp = s1(v[t - 2][1]) + v[t - 7][1] + s0(v[t - 15][1]) + v[t - 16][1]
            h = match(R[t][2], x, xp)
            wexp += (-np.log2(h / NS) if h else 21.0)
    return pf, wexp

# ---- combine ----
for f in sys.argv[1:]:
    try:
        state, W, total, q = owner_count(f)
        pf, wexp = wcost(f)
    except Exception as e:
        print(f"{f}\tERR\t{e}"); continue
    flag = " FLAG_UNDER_250" if (total < 250 and q == 0) else ""
    print(f"{f}  owner_count STATE {state} W {W}  wcost PASTFREE {pf} WEXP {wexp:.1f}{flag}")
