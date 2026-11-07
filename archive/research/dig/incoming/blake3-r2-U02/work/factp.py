#!/usr/bin/env python3
"""U02: own enumeration of Fact P (C3 pin) for the record profile; independent of realize.py.
C3 = G(X3,X7,X11,X15; w4, W13): a1=X3+X7+w4; d1=ror(X15^a1,16); c1=X11+d1; b1=ror(X7^c1,12);
a2=a1+b1+W13; d2=ror(d1^a2,8); c2=c1+d2; b2=ror(b1^c2,7).  Outputs Y3=a2 Y7=b2 Y11=c2 Y15=d2.
Second message: w4' = ((K+w4)^8)-K.  Free state <-> pins is a bijection (a1,b1,c1,d1) <-> (X3,X7,X11,X15)."""
import sys, json, itertools
M = 0xffffffff
ror = lambda x, n: ((x >> n) | (x << (32 - n))) & M
rol = lambda x, n: ror(x, 32 - n)
K = (0x3C6EF372 + 0x1F83D9AB) & M
W4, W13 = 0x97475638, 0x0007c006
W4B = (((K + W4) ^ 8) - K) & M
PIN = dict(X3=0x29d4fa98, X7=0xbee3af28, X11=0x44036000, X15=0x40c58500)
D3, D11 = 0xfdb77cfd, 0x0a08818b

def c3(X3, X7, X11, X15, w4, w13):
    a1 = (X3 + X7 + w4) & M; d1 = ror(X15 ^ a1, 16); c1 = (X11 + d1) & M; b1 = ror(X7 ^ c1, 12)
    a2 = (a1 + b1 + w13) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2)

def cube(D, R):
    """all x (32-bit) with x ^ (x + D) == R (mod 2^32), as (fixedmask, fixedvalue); None if empty.
    x^y=R with y=x+D: carry into bit i must be c_i = D_i ^ R_i (c_0 = 0)."""
    c = [((D >> i) ^ (R >> i)) & 1 for i in range(32)]
    if c[0]: return None
    fm = fv = 0
    for i in range(32):
        di = (D >> i) & 1
        cout = c[i + 1] if i < 31 else None
        if di == c[i]:                       # generate/kill by D alone: carry out = di, x_i free
            if cout is not None and cout != di: return None
        else:                                # propagate-or-x: carry out = x_i
            if cout is not None:
                fm |= 1 << i; fv |= cout << i
            # i == 31: x_31 forced? carry out ignored -> x_31 free
    return fm, fv
def cube_iter(cb):
    fm, fv = cb
    free = [i for i in range(32) if not (fm >> i) & 1]
    for bits in range(1 << len(free)):
        x = fv
        for j, i in enumerate(free):
            if (bits >> j) & 1: x |= 1 << i
        yield x
def csize(cb): return 1 << (32 - bin(cb[0]).count('1')) if cb else 0

def valid_R(D, limit=1 << 22):
    """all R for which cube(D,R) is non-empty (DFS over bits, forced rule R_i=0 => R_{i+1}=D_i^D_{i+1})."""
    out = []
    def rec(i, R):
        if len(out) > limit: raise RuntimeError('too many')
        if i == 32: out.append(R); return
        for r in (0, 1):
            if i == 0 and r != (D & 1): continue
            if i > 0:
                prev_r = (R >> (i - 1)) & 1
                if prev_r == 0 and r != (((D >> (i - 1)) ^ (D >> i)) & 1): continue
            rec(i + 1, R | (r << i))
    rec(0, 0)
    return out

if __name__ == '__main__':
    # ---- validation on the known answer (record pins) ----
    A = c3(PIN['X3'], PIN['X7'], PIN['X11'], PIN['X15'], W4, W13)
    B = c3(PIN['X3'], PIN['X7'], PIN['X11'], PIN['X15'], W4B, W13)
    known = dict(Y3=0x8127c181, Y3B=0x7edf3e7e, Y11=0x7af77f38, Y11B=0x850000c3, d2=0xbbfbdffe, b2=0x76f7aefd)
    got = dict(Y3=A['a2'], Y3B=B['a2'], Y11=A['c2'], Y11B=B['c2'], d2=A['d2'], b2=A['b2'])
    assert got == known and A['d2'] == B['d2'] and A['b2'] == B['b2'], (got, known)
    assert (B['a2'] - A['a2']) & M == D3 and (B['c2'] - A['c2']) & M == D11 and W4B == 0x97475640
    print('VALIDATION OK: record pins reproduce Y3/Y3B/Y11/Y11B, equal d2=bbfbdffe b2=76f7aefd, D3, D11')
    # ---- structure: which carry-run X = a1 ^ (a1+8) are compatible with the profile ----
    rd = valid_R(D11); r3 = set(valid_R(D3))
    print('valid R for D11:', len(rd), ' for D3:', len(r3))
    runs = []
    for k in range(3, 32):
        X = ((1 << (k + 1)) - 1) & ~7 & M
        R = ror(X, 16)
        c_a2, c_d1 = cube(D3, R), cube(D11, R)
        runs.append((k, X, R, csize(c_a2), csize(c_d1)))
    print('runs X(k) with R, |cube(D3,R)|, |cube(D11,R)|:')
    for r in runs: print('  k=%d X=%08x R=%08x  %d %d' % r)
    good = [r for r in runs if r[3] and r[4]]
    print('compatible runs:', [(hex(g[1])) for g in good])
    # admissible v: v in valid(D11), ROL(v,12) in valid(D11), v in valid(D3-8)
    v3 = set(valid_R((D3 - 8) & M)); vs = [v for v in rd if v in v3 and rol(v, 12) in set(rd)]
    print('admissible v:', [hex(v) for v in vs])
    json.dump(dict(runs=runs, vs=vs), open('structure.json', 'w'))
