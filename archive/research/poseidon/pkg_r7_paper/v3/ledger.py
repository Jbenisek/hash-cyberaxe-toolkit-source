#!/usr/bin/env python3
"""Exact-structure cost ledger for the Orchard Poseidon algebraic collision attack (program exec_r6mt, single thread T = 1).

Nothing here is measured from a run of the program.  Every charge is read from the C source:
  * leaf kernel charges (NTT butterfly blocks, whole passes, radix-3 position kernels) are PARSED from ntt_kern.h and ntt_a3.h
    (LD(n)/ST(n) = 2n, CTL(n) = n, each fp_add/sub/mul/sqr, BF/BFN/IB/IBN macros = 3/2/3/2);
  * the control flow of ntt.c, lean.c, line.c, hgcd.c, poly.c, common.c, single.c is PORTED statement by statement (charges are
    written next to the statements in the source and copied here with the source line comment as reference).
Assumptions (stated, not proved):
  A1 normal Euclid: every quotient of the gcd has degree 1 (fails with probability <= about m/p, p ~ 2^254);
  A2 the gcd degree dG of failed trials is 0 (the more expensive case), the successful trial has dG >= 1 (E bounded);
  A3 allocator: every xalloc walks at most WALK = 2*(max live blocks)+1 blocks, every xfree costs <= 105, plan_invN lookups
     cost 7*(number of distinct plan sizes) (upper bounds; the exact values depend on fragmentation / first-use order).
usage: python ledger.py [--write]      (prints the validation and the table; --write regenerates LEDGER.md)
"""
import re, os, sys, math, functools
import ledger_e as LE                  # worst-case charges of the coin draw, stage E (capped isolation) and stage F (this folder)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('LEDGER_SRC', os.path.normpath(os.path.join(HERE, '..', 'orchard', 'exec_r6mt')))

# ---------------------------------------------------------------- field constants
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
PM1 = P - 1
PM2 = P - 2
PM1H = PM1 >> 1
Q = PM1 >> 32
QP1H = (Q + 1) >> 1
INV_CTL = 2310
STAGE_BK = 1000


def powcost(e):
    """fp_pow charges: top squarings + (popcount-1) multiplications (leading bit free)."""
    if e <= 0:
        return 0
    return (e.bit_length() - 1) + (bin(e).count('1') - 1)


def sqrt_arith(a):
    """arithmetic charged by fp_sqrt(a) (Tonelli-Shanks, pallas.c), computed on the actual field element."""
    if a % P == 0:
        return 0
    c = powcost(Q) + powcost(QP1H)
    z = pow(5, Q, P); t = pow(a, Q, P); m = 32
    while t != 1:
        i = 0; u = t
        while u != 1:
            u = u * u % P; c += 1; i += 1
            if i >= m:
                return c
        b = z
        for _ in range(m - i - 1):
            b = b * b % P; c += 1
        c += 1                      # x *= b
        z = b * b % P; c += 1       # z = b^2
        t = t * z % P; c += 1
        m = i
    return c


# ---------------------------------------------------------------- source parser (leaf charges)
def _strip(t):
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    return re.sub(r'//[^\n]*', '', t)


def _functions(text):
    out = {}
    for mm in re.finditer(r'static\s+(?:inline\s+)?void\s+(\w+)\s*\(', text):
        i = text.index('{', mm.end()); d = 0; j = i
        while True:
            if text[j] == '{': d += 1
            elif text[j] == '}':
                d -= 1
                if d == 0: break
            j += 1
        out[mm.group(1)] = text[i + 1:j]
    return out


def _num(expr):
    expr = expr.strip()
    if re.fullmatch(r'[0-9 +*]+', expr):
        return eval(expr)
    raise ValueError('non-numeric charge ' + expr)


MACRO = {'BF': 3, 'BFN': 2, 'IB': 3, 'IBN': 2, 'fp_mul': 1, 'fp_sqr': 1, 'fp_add': 1, 'fp_sub': 1}


def _padd(a, b, k=1):
    for key, v in b.items():
        a[key] = a.get(key, 0) + k * v


def _eval(name, funcs, cache):
    """charge polynomial of a function: {(i, j): coef} meaning coef * ngrp^i * (s-1)^j."""
    if name in cache:
        return cache[name]
    poly = {}
    stack = [(0, 0)]
    for line in funcs[name].split('\n'):
        s = line.strip()
        if not s:
            continue
        if s.startswith('}'):
            stack.pop()
            continue
        mult = stack[-1]
        for m_ in re.finditer(r'\b(LD|ST)\(([^()]*)\)', s):
            _padd(poly, {mult: 2 * _num(m_.group(2))})
        for m_ in re.finditer(r'\bCTL\(([^()]*)\)', s):
            _padd(poly, {mult: _num(m_.group(1))})
        for m_ in re.finditer(r'\b(BFN|BF|IBN|IB|fp_mul|fp_sqr|fp_add|fp_sub)\(', s):
            _padd(poly, {mult: MACRO[m_.group(1)]})
        for m_ in re.finditer(r'\b(k[fi]\d+z?|p[fiu]\d+c(?:_\w+)?)\(', s):
            if m_.group(1) in funcs and m_.group(1) != name:
                sub = _eval(m_.group(1), funcs, cache)
                for (i, j), v in sub.items():
                    poly[(i + mult[0], j + mult[1])] = poly.get((i + mult[0], j + mult[1]), 0) + v
        opens = s.count('{') - s.count('}')
        if 'for (size_t grp' in s:
            stack.append((mult[0] + 1, mult[1]))
        elif 'for (size_t b = 1' in s:
            stack.append((mult[0], mult[1] + 1))
        else:
            for _ in range(opens):
                stack.append(mult)
    cache[name] = poly
    return poly


def _peval(poly, ngrp, sm1):
    return sum(v * ngrp ** i * sm1 ** j for (i, j), v in poly.items())


class Leaf:
    def __init__(self, src=SRC):
        kern = _strip(open(os.path.join(src, 'ntt_kern.h')).read())
        a3 = _strip(open(os.path.join(src, 'ntt_a3.h')).read())
        f = _functions(kern); cache = {}
        self.passes = {}
        for k in range(1, 5):
            self.passes[('f', k)] = _eval('pf%d' % k, f, cache)
            self.passes[('i', k)] = _eval('pi%d' % k, f, cache)
            self.passes[('usq', k)] = _eval('pu%d_sq' % k, f, cache)
            self.passes[('umul', k)] = _eval('pu%d_mul' % k, f, cache)
        g = _functions(a3); c2 = {}
        self.k3 = {}
        for nm in g:
            m_ = re.fullmatch(r'a3([fi])_(\d)_(\d)', nm)
            if m_:
                self.k3[(m_.group(1), int(m_.group(2)), int(m_.group(3)))] = _peval(_eval(nm, g, c2), 1, 0)
            m_ = re.fullmatch(r'a3r_(\d)_(\d)_(\d)', nm)
            if m_:
                self.k3[('r%d' % int(m_.group(3)), int(m_.group(1)), int(m_.group(2)))] = _peval(_eval(nm, g, c2), 1, 0)
        # driver tables: (type, pat, c0) -> rots (r0, r1, r2), read from the DRV_* lines of ntt_a3.h
        self.rots = {}
        raw = open(os.path.join(src, 'ntt_a3.h')).read()
        for m_ in re.finditer(r'^DRV_([FI])\((\d), (\d), (\d), (\d), (\d)\)', raw, re.M):
            t, pat, c0 = m_.group(1).lower(), int(m_.group(2)), int(m_.group(3))
            self.rots[(t, pat, c0)] = tuple(int(m_.group(i)) for i in (4, 5, 6))
        for m_ in re.finditer(r'^DRV_R\((\d), (\d), (\d), (\d), (\d), (\d)\)', raw, re.M):
            r_, pat, c0 = int(m_.group(1)), int(m_.group(2)), int(m_.group(3))
            self.rots[('r%d' % r_, pat, c0)] = tuple(int(m_.group(i)) for i in (4, 5, 6))

    # pass costs (ntt.c pass_fwd / pass_inv / pass_fused, T = 1: par_big returns 0 at no charge)
    def pass_fwd(self, a, l0, k):
        return 5 + (9 * k + 2) + 4 + _peval(self.passes[('f', k)], 1 << l0, (1 << (a - l0 - k)) - 1)

    def pass_inv(self, a, l0, k):
        return 6 + (9 * k + 2) + 4 + _peval(self.passes[('i', k)], 1 << l0, (1 << (a - l0 - k)) - 1)

    def pass_fused(self, a, l0, k, mode):
        poly = self.passes[('usq' if mode == 'sq' else 'umul', k)]
        return 6 + (9 * k + 2) + 6 + _peval(poly, 1 << (a - k), 0)


LEAF = None


def leaf():
    global LEAF
    if LEAF is None:
        LEAF = Leaf()
    return LEAF


# ---------------------------------------------------------------- bound parameters and the trace object
class G:                               # global bound parameters of one model evaluation
    WALK = 64                          # blocks walked by one xalloc (bound)
    CACHE = 64                         # plan_invN cache entries scanned (bound)
    NSET = set()                       # distinct plan sizes seen by plan_invN
    SCOUT = False


def alloc_ops():
    return 120 + 13 * G.WALK


FREE_OPS = 105


def blk(slots):
    return 64 + ((slots * 32 + 63) & ~63)


class Tr:
    """sequential trace: ops, current live bytes/blocks relative to entry, peaks"""
    __slots__ = ('ops', 'cur', 'peak', 'cnt', 'pcnt', 'base')

    def __init__(self, base=0):
        self.ops = 0; self.cur = 0; self.peak = 0; self.cnt = 0; self.pcnt = 0; self.base = base

    def here(self): return self.base + self.cnt            # live blocks now (for sub-traces)

    def ctl(self, n): self.ops += n
    def ld(self, n): self.ops += 2 * n
    def st(self, n): self.ops += 2 * n
    def loopc(self, n): self.ops += 3 * n + 2

    def add(self, o):
        self.ops += o.ops
        self.peak = max(self.peak, self.cur + o.peak); self.pcnt = max(self.pcnt, self.cnt + o.pcnt)
        self.cur += o.cur; self.cnt += o.cnt

    def new_fp(self, slots):
        slots = max(slots, 1) if slots else 1
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1)
        b = blk(slots); self.cur += b; self.cnt += 1
        self.peak = max(self.peak, self.cur); self.pcnt = max(self.pcnt, self.cnt)
        return slots

    def free(self, slots):
        self.ops += FREE_OPS
        self.cur -= blk(slots); self.cnt -= 1


# ---------------------------------------------------------------- small helpers
def for8(n):                           # FOR8 / for8_ctl charge of the loop control
    return 1 + 3 * (n // 8) + 2 + 3 * (n % 8) + 2


def udivmod_cost(a, b):
    nb = a.bit_length(); q = a // b
    return 4 * nb + 2 + 10 * nb + 2 * bin(q).count('1') + 4


class Plan:
    def __init__(self, rows, a):
        self.rows = rows; self.a = a; self.n = 1 << a; self.N = 3 * self.n if rows == 3 else self.n
        self.c0 = (1 if a & 1 else 2) if rows == 3 else 0
        self.np = (a + 3) >> 2
        kk = [0] * self.np; rem = a
        for i in range(self.np - 1, -1, -1):
            k = min(4, rem); kk[i] = k; rem -= k
        self.kk = kk


def make_plan(rows, a):
    p = Plan(rows, a)
    c = 18 + 4 + (3 * p.np + 2) + 4 * p.np + 2 + (4 if rows == 3 else 0)
    return p, c


def plan_for_len(ln, allow3):
    c = 0
    for a in range(2, 64):
        c += 3 + 1 + 2 + (4 if allow3 else 0)
        if (1 << a) >= ln:
            p, cc = make_plan(1, a); return p, c + cc
        if allow3 and 3 * (1 << a) >= ln:
            p, cc = make_plan(3, a); return p, c + cc
    raise ValueError


def plan3_for_len(ln):
    c = 0
    for a in range(2, 64):
        c += 3 + 1 + 2 + 2
        if 3 * (1 << a) >= ln:
            p, cc = make_plan(3, a); return p, c + cc
    raise ValueError


def plan_invN_ops(Pl):
    G.NSET.add(Pl.N)
    return 7 * G.CACHE


def miss_extra():                      # one-time extra per distinct plan size: 64 scans + conversion + inverse
    return 7 * 64 + 1 + powcost(PM2) + INV_CTL


# ---------------------------------------------------------------- NTT stages (ntt.c)
def split_regions(n, N, boff, lenB):
    c = 3; bp = [0]
    nt0 = 0
    for t in range(3):
        st = nt0 + N - boff
        if st >= N: st -= N
        nt0 += n; c += 9
        c += 3
        if st < lenB:
            x = lenB - st; c += 1; c += 3
            if 0 < x < n: bp.append(x); c += 1
        c += 3
        if st > 0:
            x = N - st; c += 1; c += 3
            if 0 < x < n: bp.append(x); c += 1
            x = N + lenB - st; c += 2; c += 3
            if 0 < x < n: bp.append(x); c += 1
    c += 2
    bp.append(n); c += 1
    cnt = len(bp)
    for a in range(1, cnt):
        key = bp[a]; b = a - 1; c += 3 + 2
        while b >= 0 and bp[b] > key:
            bp[b + 1] = bp[b]; b -= 1; c += 6
        c += 3
        bp[b + 1] = key
    c += 2
    out = []; pats = []
    for a in range(cnt - 1):
        c += 6
        if bp[a + 1] > bp[a]:
            lo = bp[a]; p = 0; nt1 = 0
            for t in range(3):
                idx = lo + nt1 + N - boff
                if idx >= N: idx -= N
                p |= (1 if idx < lenB else 0) << t; nt1 += n; c += 13
            c += 5
            out.append(lo); pats.append(p); c += 2
    c += 2
    out.append(n); c += 1
    return out, pats, c


def driver(typ, pat, c0, lo, hi):
    """cost of one region driver call (DRV_F / DRV_I / DRV_R macro of ntt.c) over positions lo..hi-1"""
    L = leaf()
    rots = L.rots[(typ, pat, c0)]
    K = [L.k3[(typ, pat, r)] for r in rots]
    i = lo
    c = udivmod_cost(lo, 3); ph = lo % 3; c += 1
    c += 2
    if ph == 1:
        c += 2
        if i < hi:
            c += K[1]; i += 1; c += 1
            c += 2
            if i < hi:
                c += K[2]; i += 1; c += 1
    else:
        c += 2
        if ph == 2:
            c += 2
            if i < hi:
                c += K[2]; i += 1; c += 1
    nt = 0; c += 2
    if hi > i:
        nt = (hi - i) // 3; c += udivmod_cost(hi - i, 3); c += 2
    c += nt * (K[0] + K[1] + K[2] + 4)
    i += 3 * nt
    c += 2
    c += 2
    if hi > i:
        rem = hi - i; c += 1
        c += K[0]; i += 1; c += 1
        c += 2
        if rem == 2:
            c += K[1]
    return c


def stageA_fwd(Pl, ln):
    c = 4
    n = Pl.n
    if Pl.rows == 1:
        raise NotImplementedError('plain rows==1 forward copy is not used on the charged path')
    bp, pat, cc = split_regions(n, Pl.N, 0, ln); c += cc
    c += 2
    for q in range(len(pat)):
        c += 4 + driver('f', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_inv(Pl, outlen):
    if Pl.rows == 1:
        return 0
    c = 2
    bp, pat, cc = split_regions(Pl.n, Pl.N, 0, outlen); c += cc
    c += 2
    for q in range(len(pat)):
        c += 2
        if pat[q] == 0:
            c += 3; continue
        c += 4 + driver('i', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_row(Pl, r, lenB, boff):
    n = Pl.n
    bp, pat, c = split_regions(n, Pl.N, boff, lenB)
    c += 2
    for q in range(len(pat)):
        c += 3 * 11 + 2 + 4 + driver('r%d' % r, pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def fwd_passes(Pl, cnt):
    L = leaf(); l0 = 0; c = 0
    for p in range(cnt):
        c += L.pass_fwd(Pl.a, l0, Pl.kk[p]) + 4; l0 += Pl.kk[p]
    return c


def inv_passes(Pl, first):            # inverse passes p = first down to 0
    L = leaf(); l0 = sum(Pl.kk[:first + 1]); c = 0
    for p in range(first, -1, -1):
        l0 -= Pl.kk[p]
        c += L.pass_inv(Pl.a, l0, Pl.kk[p]) + 4
    return c


def fused(Pl, mode):
    return leaf().pass_fused(Pl.a, Pl.a - Pl.kk[-1], Pl.kk[-1], mode)


def conv_core_row(Pl, mode):
    return 9 + fwd_passes(Pl, Pl.np - 1) + 4 + fused(Pl, mode) + inv_passes(Pl, Pl.np - 2) + 4


def conv_sq(Pl, ln, outlen):
    c = stageA_fwd(Pl, ln)
    c += Pl.rows * conv_core_row(Pl, 'sq') + 2
    return c + stageA_inv(Pl, outlen)


def mulc_otf_row(Pl, r, lenB, boff):
    c = 12 + stageA_row(Pl, r, lenB, boff)
    c += fwd_passes(Pl, Pl.np) + 2
    c += fwd_passes(Pl, Pl.np - 1) + fused(Pl, 'mul') + inv_passes(Pl, Pl.np - 2) + 4
    return c


def conv_mulc_otf(Pl, ln, lenB, boff, outlen):
    c = 2 + stageA_fwd(Pl, ln) + 4
    for r in range(3):
        c += mulc_otf_row(Pl, r, lenB, boff)
    return c + 2 + stageA_inv(Pl, outlen)


def pw_loop(n, mode):
    return for8(n) + n * (7 if mode == 0 else 10)


def conv_bilin_cost(Pl, nout, outlen, groups):
    """groups: list of dict(H=[lens], S=[lens], prod=[(s, h, out, sign)]) in code order.  Returns (ops, eps)."""
    c = 2
    eps = [0] * nout
    c += 2 + 3 * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                c += 6
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]:
                    eps[o] = sg
    for r in range(3):
        c += 2 + 2 + nout + 1
        done = [0] * nout
        for g in groups:
            c += 7
            for lh in g['H']:
                c += 6 + stageA_row(Pl, r, lh, 0) + fwd_passes(Pl, Pl.np)
            for s, ls in enumerate(g['S']):
                c += 6 + stageA_row(Pl, r, ls, 0) + fwd_passes(Pl, Pl.np)
                for h in range(len(g['H'])):
                    c += 8
                    o, sg = g['prod'].get((s, h), (-1, 0))
                    if o < 0: continue
                    if not done[o]:
                        done[o] = 1; c += pw_loop(Pl.n, 0)
                    elif sg == eps[o]:
                        c += pw_loop(Pl.n, 1)
                    else:
                        c += pw_loop(Pl.n, 2)
        for k in range(nout):
            c += 3
            if eps[k]:
                c += inv_passes(Pl, Pl.np - 1)
        c += 0
    for k in range(nout):
        c += 3
        if eps[k]:
            c += stageA_inv(Pl, outlen[k])
    return c, eps


# ---------------------------------------------------------------- lean.c: x^E mod g
def ebit(E, i): return (E >> i) & 1


def powx_lean(m, b, E=PM1H):
    T = Tr(b)
    PN, c1 = plan3_for_len(2 * m - 1); PNp, c2 = plan3_for_len(m + 1)
    T.ctl(c1 + c2)
    N, Np = PN.N, PNp.N
    sY = T.new_fp(N); sT = T.new_fp(PN.n); sM = T.new_fp(m - 1)
    # newton_lean
    L = m - 1
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l                                       # pl_run MULC
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)                                 # pl_run NEGMULC: mul + sub per element
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    T.ld(L); T.st(L); T.loopc(L // 2); T.ctl(2 * (L // 2))
    # prefix + scale
    T.ctl(plan_invN_ops(PN)); T.ctl(plan_invN_ops(PNp)); T.ops += 1
    T.ops += m - 1; T.ld(m - 1); T.st(m - 1); T.loopc(m - 1)
    gamma = N - (m - 2)
    top = 255
    while top > 0 and not ebit(E, top):
        top -= 1; T.ctl(12)
    v = 1; bit = top
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; T.ctl(25)
    T.st(m); T.loopc(m)
    T.ctl(plan_invN_ops(PN)); T.st(1)
    steps = bit
    lim = (2 * m - 2 - Np + 1) if 2 * m - 2 >= Np else 0
    lim = min(lim, m)
    step = conv_sq(PN, m, 2 * m - 1) + 8
    step += for8(lim) + 7 * lim + for8(m - lim) + 4 * (m - lim) + for8(m - 1) + 4 * (m - 1)
    step += conv_mulc_otf(PN, m - 1, m - 1, gamma, m - 1) + conv_mulc_otf(PNp, m - 1, m + 1, 0, m)
    step += for8(m) + 7 * m
    step += 14 + 6
    mulx = 2 + for8(m - 1) + 8 * (m - 1) + 2 + 4
    nset = sum(ebit(E, b) for b in range(bit))
    T.ops += steps * step + nset * mulx
    T.ops += 1 + m; T.ld(m); T.st(m); T.loopc(m)
    T.ctl(2 + 500)
    T.free(sY); T.free(sT); T.free(sM)
    info = dict(steps=steps, nset=nset, PN=PN, PNp=PNp, step=step, mulx=mulx)
    return T, info


# ---------------------------------------------------------------- line.c: build_g
def poly_degree_m(r):
    D = 1
    for _ in range(6 + r): D = D * 5
    return (D - 1) // 2


def perm_C(r): return 216 + 21 * r


def build_g(r, b):
    T = Tr(b)
    m = poly_degree_m(r)
    T.ctl(4 * (6 + r) + 6)
    Pl, c = plan_for_len(m + 1, 1); T.ctl(c)
    H = Pl.N; a = Pl.a
    sb = T.new_fp(H)
    rho = pow(5, PM1 // Pl.n, P)
    T.ld(1); T.ctl(1 + 2)
    if Pl.rows == 1:
        theta = rho
    else:
        w = pow(5, PM1 // 3, P)
        e = 3 - Pl.c0
        theta = rho * pow(w, e, P) % P
        T.ctl(4); T.ops += 1
    # fp_sqrt(theta): a square? theta = rho (order 2^a) is a square iff a < 32 ; psi = sqrt
    T.ops += sqrt_arith(theta)
    T.ops += powcost(PM2); T.ctl(INV_CTL + 12000)             # fp_inv(ipsi)
    T.ops += 1 + powcost(PM2)                                  # two = 1 + 1 ; half = inv(two)
    per_point = 1 + 1 + 2 * perm_C(r) + 1 + 1 + (12 + 7 * a + 2) + 2 + 10
    T.ops += H * per_point
    T.st(H); T.loopc(H)
    # ntt_inv(P, buf, m+1)
    L = leaf()
    row = 4; l0 = Pl.a
    for p in range(Pl.np - 1, -1, -1):
        l0 -= Pl.kk[p]; row += L.pass_inv(Pl.a, l0, Pl.kk[p]) + 4
    row += 2
    T.ops += Pl.rows * row + 2 + stageA_inv(Pl, m + 1)
    T.ctl(5)
    T.ops += powcost(PM2); T.ctl(INV_CTL)
    T.ops += m                                                 # pl_run MULC
    T.ld(m + 1); T.st(m + 1); T.loopc(m + 1)
    T.free(sb)
    return T, dict(m=m, plan=Pl)


# ---------------------------------------------------------------- hgcd.c on shapes (normal Euclid)
def dupv(ln, b):
    T = Tr(b); s = T.new_fp(ln if ln else 1)
    T.ld(ln); T.st(ln); T.loopc(ln)
    return T, s


def trim(it): return 11 * it           # trimlen: CTL(9 it) + LD(it)


def divrem_naive(lx, ly, term_zero=0):
    """cost of poly_divrem_naive for consecutive lengths (lx = ly + 1); returns (ops, lq, lr, iterations of the final trim)"""
    c = 3
    la, lb = lx, ly
    assert la == lb + 1
    if lb >= 2:
        c += powcost(PM2) + INV_CTL + 3 + 1
        c += 2 * 3 + 2 * 2 + 6
        c += (2 * (lb - 1) + 2 * max(lb - 2, 0))
        c += 4 * (lb - 1) + 2 * (lb - 1) + 3 * (lb - 1) + 2 + 4 + 2 * (lb - 1)
        it = 1 + term_zero * (lb - 1)
        c += trim(it)
        return c, 2, lb - 1 - term_zero * (lb - 1), it
    # general path, lb == 1 (la == 2)
    c += 2 * la + 2 * la + 3 * la + 2
    c += powcost(PM2) + INV_CTL
    c += (la - lb + 1) * (1 + 2 + 2 + 2 + 7) + (la - lb + 1) * 0
    c += trim(1)
    return c, la - lb + 1, 0, 1


def mat_identity(b):
    T = Tr(b); sl = [T.new_fp(1) for _ in range(4)]
    T.st(2)
    return T, [1, 0, 0, 1], sl


def mat_free(T, sl):
    for s in sl:
        if s: T.free(s)


def mul_add_q2(T, le, lf):
    lt = le + 1 if le else 0
    lo = max(lt, lf)
    s = T.new_fp(lo if lo else 1)
    muls = (le + max(le - 1, 0) + (1 if le > 0 else 0))
    adds = max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0)
    T.ops += muls + adds
    T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo)
    T.ctl(trim(1))
    return lo, s


def mat_mulQ(T, lens, sl):
    l0, s0 = mul_add_q2(T, lens[0], lens[1])
    l2, s2 = mul_add_q2(T, lens[2], lens[3])
    T.free(sl[1]); T.free(sl[3])
    return [l0, lens[0], l2, lens[2]], [s0, sl[0], s2, sl[2]]


def poly_mul_naive_cost(la, lb):
    return la * lb * 11 + (la * lb - (la + lb - 1)) + (la + lb - 1) * 11 + 2


def mat_mul(A, B, b):
    """A, B = (lens, slots); returns (Tr, lens, slots)"""
    T = Tr(b); T.ctl(80)
    Al, Bl = A[0], B[0]
    Ls = [0] * 4
    for i in range(2):
        for j in range(2):
            l = 0
            for t in range(2):
                la, lb = Al[2 * i + t], Bl[2 * t + j]
                if la and lb and la + lb - 1 > l: l = la + lb - 1
            Ls[2 * i + j] = l
    Lmax = max(1, max(Ls))
    outl = [0] * 4; outs = [0] * 4
    if Lmax <= 48:
        for i in range(2):
            for j in range(2):
                l = Ls[2 * i + j]
                o = T.new_fp(l if l else 1)
                T.st(l); T.loopc(l)
                for t in range(2):
                    la, lb = Al[2 * i + t], Bl[2 * t + j]
                    if not la or not lb: continue
                    tmp = T.new_fp(la + lb - 1)
                    T.ops += poly_mul_naive_cost(la, lb)
                    T.ops += la + lb - 1
                    T.ld(2 * (la + lb - 1)); T.st(la + lb - 1); T.loopc(la + lb - 1)
                    T.free(tmp); T.ctl(6)
                T.ctl(trim(1))
                outl[2 * i + j] = l; outs[2 * i + j] = o
        return T, outl, outs
    Pl, c = plan3_for_len(Lmax); T.ctl(c)
    N = Pl.N
    tH0 = T.new_fp(Pl.n); tH1 = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
    ob = [T.new_fp(N) for _ in range(4)]
    groups = []
    for t in range(2):
        g = dict(H=[], S=[], prod={}); hj = [-1, -1]
        for j in range(2):
            if Bl[2 * t + j]:
                hj[j] = len(g['H']); g['H'].append(Bl[2 * t + j])
        for i in range(2):
            if Al[2 * i + t]:
                s = len(g['S']); g['S'].append(Al[2 * i + t])
                for j in range(2):
                    if hj[j] >= 0: g['prod'][(s, hj[j])] = (2 * i + j, 1)
        if g['H'] and g['S']: groups.append(g)
        T.ctl(20)
    cc, eps = conv_bilin_cost(Pl, 4, Ls, groups); T.ctl(cc)
    T.free(tH0); T.free(tH1); T.free(tS)
    T.ctl(plan_invN_ops(Pl))
    for k in range(4):
        l = Ls[k]
        o = T.new_fp(l if l else 1); T.ctl(3)
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs


def apply_inv(Rl, Rs, h, la, lb, consume, b):
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    N = Pl.N
    tH = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
    sc_ = T.new_fp(N); sd_ = T.new_fp(N)
    sgn = -1 if (h & 1) else 1
    T.ctl(60)
    ec = [3, 1]; ed = [2, 0]; sc = [sgn, -sgn]; sd = [-sgn, sgn]
    lV = [la, lb]
    groups = []
    for v in range(2):
        g = dict(H=[lV[v]], S=[], prod={})
        if not lV[v]: continue
        if Rl[ec[v]]:
            g['prod'][(len(g['S']), 0)] = (0, sc[v]); g['S'].append(Rl[ec[v]])
        if Rl[ed[v]]:
            g['prod'][(len(g['S']), 0)] = (1, sd[v]); g['S'].append(Rl[ed[v]])
        if g['S']: groups.append(g)
        T.ctl(10)
    cc, eps = conv_bilin_cost(Pl, 2, [nres, nres], groups); T.ctl(cc)
    T.free(tH); T.free(tS)
    if consume:
        mat_free(T, Rs)
    T.ctl(plan_invN_ops(Pl))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    T.ctl(trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    return T, lc, sc_, ld, sd_


@functools.lru_cache(maxsize=None)
def hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b):
    """returns (Tr, out) ; out = (lc, sc, ld, sd, Rl, Rs, h)"""
    T = Tr(b); T.ctl(40)
    n = la - 1
    Rl = Rs = None
    if lb == 0 or n - (lb - 1) > k:
        if want_mat:
            t, Rl, Rs = mat_identity(T.here()); T.add(t)
        T.ctl(4)
        lc = sc = ld = sd = None
        if wc:
            if own & 1: sc = sa
            else:
                t, sc = dupv(la, T.here()); T.add(t)
            lc = la
        elif own & 1: T.free(sa)
        if wd:
            if own & 2: sd = sb
            else:
                t, sd = dupv(lb, T.here()); T.add(t)
            ld = lb
        elif own & 2: T.free(sb)
        return T, (lc, sc, ld, sd, Rl, Rs, 0)
    if k <= 96:
        return hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T)
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    las = la - s; lbs = lb - s if lb > s else 0
    t1, o1 = hgcd(las, 0, lbs, 0, k1, 1, 0, False, False, T.here())
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    assert h1 >= 1, 'non-generic shape'
    t2, lcc, scc, ldd, sdd = apply_inv(R1l, R1s, h1, la, lb, not want_mat, T.here())
    T.add(t2); T.ctl(4)
    if own & 1: T.free(sa)
    if own & 2: T.free(sb)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    if ldd == 0 or (lcc - ldd) > k2:
        if want_mat: Rl, Rs = R1l, R1s
        lc = sc = ld = sd = None
        if wc: lc, sc = lcc, scc
        else: T.free(scc)
        if wd: ld, sd = ldd, sdd
        else: T.free(sdd)
        return T, (lc, sc, ld, sd, Rl, Rs, h1)
    dq = lcc - ldd
    sq = T.new_fp(dq + 1); srm = T.new_fp(lcc)
    T.ctl(3)                                                  # divrem_any
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc)
    T.free(scc)
    k3 = k2 - dq
    t3, o3 = hgcd(ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here())
    T.add(t3)
    h = h1 + dq + o3[6]
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s)
        tm, Ml, Ms = mat_mul((R1l2, R1s2), (o3[4], o3[5]), T.here()); T.add(tm)
        mat_free(T, o3[5]); mat_free(T, R1s2)
        Rl, Rs = Ml, Ms
    T.free(sq)
    return T, (o3[0], o3[1], o3[2], o3[3], Rl, Rs, h)


def hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T):
    if own & 1: sx = sa
    else:
        t, sx = dupv(la, T.here()); T.add(t)
    if own & 2: sy = sb
    else:
        t, sy = dupv(lb, T.here()); T.add(t)
    lx, ly, ssum = la, lb, 0
    Rl = Rs = None
    if want_mat:
        t, Rl, Rs = mat_identity(T.here()); T.add(t)
    while ly > 0:
        dq = lx - ly
        T.ctl(6)
        if dq > k - ssum: break
        sq = T.new_fp(dq + 1); sr = T.new_fp(lx)
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc)
        if want_mat:
            Rl, Rs = mat_mulQ(T, Rl, Rs)
        ssum += dq
        T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
        T.free(sq)
    lc = sc = ld = sd = None
    if wc: lc, sc = lx, sx
    else: T.free(sx)
    if wd: ld, sd = ly, sy
    else: T.free(sy)
    return T, (lc, sc, ld, sd, Rl, Rs, ssum)


def gcd_cost(m, dG, b):
    """poly_gcd_own(g (m+1 coefficients), R-1 (m coefficients)), normal Euclid, gcd degree dG.  Returns (Tr, (lg, sg))."""
    T = Tr(b)
    lx, ly = m + 1, m
    sx = m + 1; sy = m                                         # slots of g and of F (NEW_FP(m+1), NEW_FP(m))
    T.ctl(3); T.ctl(3)
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            sq = T.new_fp(lx - ly + 1); sr = T.new_fp(lx)
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0:
                lr = 0
            T.ctl(dc)
            T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here())
        T.add(t)
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(2)
        sq = T.new_fp(lc - ld + 1); sr = T.new_fp(lc)
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc)
        T.free(sc); T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    T.ctl(2)
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    return T, (lx, sx)


# ---------------------------------------------------------------- stage model
H_STAGE = 5644                         # stage H: constant in the three logs (stage_open + 6 conversions, 384 digits)
I_STAGE = 3384436                      # stage I: constant (single.c comment: FMT_PER_BYTE * OUTCAP + ...)
LINE_STAGE = 4910                      # line setup: independent of r (identical in the r3, r4, r5 logs)
F_BOUND = 48100                        # stage F upper bound (observed 43,682 .. 45,122); see LEDGER.md
E_DG1 = 1110
E_BOUND = 100000000                    # stage E bound for 1 <= dG <= 40 (see LEDGER.md); dG = 1 costs 1,110, dG = 2 under 25,000


def G_stage(r):
    return STAGE_BK + 10 * (2 * perm_C(r)) + 32


def init_stage(amax):
    T = Tr(0)
    T.ctl(STAGE_BK + 500)
    T.ctl(2)
    T.ctl(18 + 6)
    T.ops += 1
    T.ctl(2 + 84)
    T.ops += powcost(PM1 >> amax)
    taken = bin(PM1 // 3).count('1')
    T.ctl(4 * 4 + 2 + 12 * 256 + 2 + 7 * taken)
    T.ops += powcost(PM1 // 3)
    T.ctl(10)
    nmax = 1 << amax
    s = T.new_fp(nmax // 2)
    T.st(1)
    T.ops += (nmax // 2 - 1) * 5
    T.loopc(nmax // 2)
    T.ctl(5 * INV_CTL)
    T.ops += 1 + 1 + powcost(PM2) + 1 + 1 + 1 + 1
    T.ctl(8)                                                   # first xalloc: header of the initial free block
    return T, s


def amax_for(r):
    m = poly_degree_m(r)
    for a in range(2, 40):
        if 3 * (1 << a) >= 2 * m - 1: return a


A_CENTRE_OPS = 1                       # stage A: one conversion (centre c_i = i, the executed r3-r5 programs); the paper program draws a coin centre: LE.COIN_DRAW = 91


def run_stages(r, dG=0):
    """per-stage traces for one trial (A, B, C, D) with failing-trial tail; also info"""
    G.NSET = set()
    m = poly_degree_m(r)
    A = Tr(1); A.ctl(STAGE_BK + 5); A.ops += A_CENTRE_OPS; sg = A.new_fp(m + 1)
    B, binfo = build_g(r, 2)
    B.ctl(STAGE_BK); sF = B.new_fp(m)
    Cs, cinfo = powx_lean(m, 3); Cs.ctl(STAGE_BK)
    D = Tr(3); D.ctl(STAGE_BK); D.ops += 1; D.ctl(11)
    t, (lg, sgg) = gcd_cost(m, dG, 3)
    D.add(t); D.ctl(2)
    gcd_ops = t.ops
    if dG < 1:
        D.free(sgg)
    return dict(A=A, B=B, C=Cs, D=D, gcd_ops=gcd_ops, cinfo=cinfo, binfo=binfo, lg=lg, nset=len(G.NSET))


_STAGE_CACHE = {}


def stages_cached(r, dG):
    key = (r, dG, A_CENTRE_OPS)
    if key not in _STAGE_CACHE:
        _STAGE_CACHE[key] = run_stages(r, dG)
    return _STAGE_CACHE[key]


def evaluate(r, dGs, F_val=F_BOUND, E_val=None):
    """full program totals for len(dGs) trials with the given gcd degrees (last one must be >= 1 for the as-run validation;
    the table passes 0 everywhere = upper bound).  Returns dict."""
    G.CACHE = 64
    amax = amax_for(r)
    ini, tws = init_stage(amax)
    twb = blk(tws)
    res = dict(r=r, m=poly_degree_m(r), amax=amax)
    trials = [stages_cached(r, dG) for dG in dGs]
    res['trial'] = trials
    tot = ini.ops + LINE_STAGE
    for st in trials:
        tot += sum(st[x].ops for x in 'ABCD')
    nset = max(t['nset'] for t in trials)
    assert nset < 64, 'plan_invN cache would overflow'
    miss = nset * miss_extra()
    tot += miss
    last = dGs[-1]
    Eop = E_val if E_val is not None else (E_DG1 if last == 1 else E_BOUND)
    tot += int(Eop) + F_val + G_stage(r) + H_STAGE + I_STAGE
    res['total'] = tot; res['init'] = ini.ops; res['miss'] = miss; res['nset'] = nset
    st = trials[0]
    g_b = blk(res['m'] + 1); F_b = blk(res['m'])
    res['peaks'] = dict(A=twb + st['A'].peak, B=twb + g_b + st['B'].peak, C=twb + g_b + F_b + st['C'].peak, D=twb + g_b + F_b + st['D'].peak)
    res['heap_peak'] = max(res['peaks'].values())
    res['maxblocks'] = max(st[x].pcnt for x in 'ABCD')
    return res


# ---------------------------------------------------------------- the paper program (coin centres, K trials, capped isolation, one thread)
TRIAL_EXTRA = 12                       # statements of main not in the counters per trial: the test trials > MAXTR (2), trials++, t_centre/t_deg/t_gcd stores and the print call arguments (<= 10)
RET2 = 0                               # the failure exit (return 2) happens before stage H; the bound below charges H and I anyway


def evaluate_paper(r, K=2, dG_run=0):
    """Worst case of the shipped paper program: K trials, each charged as dG = 0 for A-D and, in addition, with stage E at its cap (ZCAP rounds at degree DMAX),
    stage F at its worst case, stage G, TRIAL_EXTRA; once: init, line setup, plan_invN misses, H and I."""
    global A_CENTRE_OPS
    old = A_CENTRE_OPS; A_CENTRE_OPS = LE.COIN_DRAW
    try:
        ev = evaluate(r, [dG_run] * K)               # fixed part and K x (A + B + C + D) with the coin centre; the single E, F, G of evaluate() are replaced below
    finally:
        A_CENTRE_OPS = old
    single_EFG = E_BOUND + F_BOUND + G_stage(r)
    E1 = LE.stage_E()
    F1, _ = LE.stage_F()
    G1 = G_stage(r)
    ev['total'] = ev['total'] - single_EFG + K * (E1 + F1 + G1 + TRIAL_EXTRA)
    ev['E1'], ev['F1'], ev['G1'] = E1, F1, G1
    ev['K'] = K
    return ev


def m_p1(m): return m + 1


# ---------------------------------------------------------------- score
def ceil5(x): return math.ceil(x * 100000 - 1e-6) / 100000
def ceil3(x): return math.ceil(x * 1000) / 1000


IMAGE_EXTRA = 402168 + 32 + 4851708        # text + data + static bss besides the arena (exec_r6mt build, NT_MAX 96); STACK below
STACK = 65536
ARENA_FACTOR = 1.177
HEAP_MARGIN = 704                         # 11 live arrays at the peak, each possibly one 64-byte rounding unit larger (r4: measured 64 B above the model)


def memory_bytes(heap_peak):
    arena = (int(math.ceil((heap_peak + HEAP_MARGIN) * ARENA_FACTOR)) + 63) & ~63
    return arena, arena + IMAGE_EXTRA + STACK


def score(total, r, heap_peak):
    C = perm_C(r)
    t = ceil5(math.log2(total / C))
    arena, mem = memory_bytes(heap_peak)
    ml = ceil3(math.log2(mem))
    return dict(time_log2=t, mem_bytes=mem, arena=arena, mem_log2=ml, score=ceil5(t + max(0, ml - 20)))


# ---------------------------------------------------------------- measured reference values (logs, algorithmic totals)
MEAS = {
    3: dict(algo=409369056359, dGs=[1], F=43682, heap=244745792,
            stage=dict(A=1126, B=1266078492, C=344571920769, D=66201757118), gcd=[66201756104],
            note='exec_r6mt sources, RR=3, T=4 run /tmp/r6val/out4.txt (stage rows include thread control)'),
    4: dict(algo=3977289295772, dGs=[0, 1], F=45122, heap=1072730624,
            stage=dict(A=2252, B=10996045694, C=3184945291322, D=796457597837), gcd=[398228799447, 398228796261],
            note='exec_r4mt cloud run T=6'),
    5: dict(algo=9171678989504, dGs=[1], F=44132, heap=4759669952,
            stage=dict(A=1126, B=23502612205, C=6583714961195, D=2598489950710), gcd=[2598489949696],
            note='exec_r5mt run_r5t T=13'),
}


def validation():
    rows = []
    for r in (3, 4, 5):
        M = MEAS[r]
        ev = evaluate(r, M['dGs'], F_val=M['F'], E_val=E_DG1)
        rows.append((r, ev, M))
    return rows


def table(rmin=3, rmax=8, Ks=(1, 2)):
    out = []
    for r in range(rmin, rmax + 1):
        res = {}
        for K in Ks:
            ev = evaluate(r, [0] * K)
            sc = score(ev['total'], r, ev['heap_peak'])
            res[K] = (ev, sc)
        out.append((r, res))
    return out


def fmt(n): return '{:,}'.format(int(n))


def report():
    L = []
    L.append('VALIDATION (as-run configuration, observed F and E; model vs algorithmic total)')
    L.append('r | model total | measured algorithmic | model - measured | slack (bits) | heap model | heap measured')
    for r, ev, M in validation():
        d = ev['total'] - M['algo']
        L.append('%d | %s | %s | %s | %.3e | %s | %s' % (r, fmt(ev['total']), fmt(M['algo']), fmt(d), math.log2(ev['total'] / M['algo']), fmt(ev['heap_peak']), fmt(M['heap'])))
    return '\n'.join(L)

THR = {3: (412047449296, 2678351361 + 41576), 4: (3992419235666, 15129788786 + 151108), 5: (9205778231873, 34099083617 + 158752)}


def md():
    o = []
    A = o.append
    A('# Poseidon algebraic attack: exact-structure cost ledger (single thread, no run)')
    A('')
    A('Generated by `ledger.py` (this folder). Source of truth: `research/poseidon/orchard/exec_r6mt` (same code as exec_r4mt/exec_r5mt apart from RR, AMAX, ARENA, NT_MAX). '
      'Nothing is measured from a run of the r6/r7/r8 program: leaf charges are parsed from `ntt_kern.h` / `ntt_a3.h`, all control flow is ported from `ntt.c, lean.c, line.c, hgcd.c, common.c, single.c`. '
      'The only numbers taken from logs are the stage constants H, I and line setup (identical in the r3, r4, r5 logs) and the observed stage F used in the validation.')
    A('')
    A('## 1. Formula (per trial, T = 1, no thread_control)')
    A("Sizes: m = (5^(6+r)-1)/2; N = 3*2^a is the smallest 3*2^a >= 2m-1 (powering plan PN), N' = 3*2^a' >= m+1 (PNp); AMAX = a; H = smallest 2^b or 3*2^b >= m+1 (build_g plan).")
    A('')
    A('`trial = A + B + C + D` (each stage_open charges 1000), plus once per run: init (ntt_init(AMAX): (2^(AMAX-1)-1) twiddle multiplications at 5 ops each + 3*2^(AMAX-1) loop ops + 5*2310 + two fp_pow of the roots + the division by 3), line setup 4,910, E + F + G (last trial), H = 5,644, I = 3,384,436, and one plan_invN miss per distinct plan size.')
    A('')
    A('* **A** = 1000 + 6 + one xalloc.')
    A('* **B** (build_g) = 1000 + H*(2*C(r) + 7*a_H + 30) + ntt_inv (rows * inverse passes + stage-A inverse of the radix 3) + 1 field inversion + m multiplications + linear charges of m+1 elements + sqrt(theta) and inverse arithmetic (Tonelli-Shanks evaluated on the real field element). C(r) = 216 + 21 r; 2*C(r) is charged per point as perm units.')
    A('* **C** (powx_lean) = Newton reciprocal (a conv_mulc_otf pair per doubling of l) + prefix/scale + steps * S_step + (number of set exponent bits below the prefix) * S_mulx, with steps = 253 - (prefix length) (229 at r5), '
      'S_step = conv_sq(PN, m, 2m-1) + conv_mulc_otf(PN, m-1, m-1, gamma, m-1) + conv_mulc_otf(PNp, m-1, m+1, 0, m) + FOLD + COPY + SHIFT + SUB loops (7, 4, 4, 7 ops per element + FOR8 control) + 20. '
      'conv_* = Good-Thomas radix-3 stage (region drivers over the nonzero patterns, split_regions) + rows * passes of the radix-2 NTT; every pass is the polynomial in (groups, blocks per group) read from the kernel source (section 8).')
    A('* **D** = 1000 + 12 + poly_gcd_own: shape simulation of the half-gcd recursion (hgcd, BASEK = 96, k1 = ceil(k/2)) with apply_inv (conv_bilin_otf), mat_mulQ, mat_mul (naive up to length 48, bilinear above), naive divisions. '
      'The simulation follows every allocation (sizes, rounding, headers).')
    A('')
    A('## 2. Assumptions (stated, not proved) and what is exact / bounded')
    A('* A1 normal Euclid: every quotient of every gcd step has degree 1. A non-normal step needs a vanishing leading coefficient; probability per step about 1/p, over m steps at most m/p (r6: 2^-227, r8: 2^-222). Not proved for the specific polynomial; the r4 trial rows (398,228,799,447 vs 398,228,796,261 for dG = 0 and 1) support it.')
    A('* A2 the table charges dG = 0 for every trial including the last (dG >= 1 is cheaper by about 3,000 ops); the last trial adds E, F, G: E <= 1e8 for dG <= 40 (dG = 1: 1,110; probability dG > 40 below 1/40!), F <= 48,100 (observed 43,682 to 45,122), G = 1000 + 10*2*C(r) + 32 (exact).')
    A('* A3 allocator: an xalloc is charged 121 + 13*(2L+1) with L = live blocks at that moment (the walk visits every block; at most 2L+1 exist); an xfree 105; a plan_invN hit 7*64, a miss added once per distinct plan size. These are upper bounds, not a simulation of fragmentation, and are the deliberate slack.')
    A('* Exact by construction (read from source): every NTT pass, region driver, linear loop, build_g, the powering schedule, matrix and array sizes. Bounded: allocator walk, plan_invN position, E, F, dG, A1.')
    A('')
    A('## 3. Validation against the measured algorithmic totals (thread_control and split_extra excluded)')
    A('Model uses the as-run configuration (r3: 1 trial dG=1; r4: 2 trials dG=0,1; r5: 1 trial dG=1; observed F; E = 1,110). r3 = exec_r6mt sources at RR=3, T=4 (R6_PLAN section 3).')
    A('')
    A('| r | model total | measured algorithmic | model - measured | slack (bits) | model heap peak | measured heap_peak |')
    A('|---|---:|---:|---:|---:|---:|---:|')
    vrows = validation()
    for r, ev, M in vrows:
        d = ev['total'] - M['algo']
        A('| %d | %s | %s | %s | %.5f | %s | %s |' % (r, fmt(ev['total']), fmt(M['algo']), fmt(d), math.log2(ev['total'] / M['algo']), fmt(ev['heap_peak']), fmt(M['heap'])))
    A('')
    A('The model is above the measured algorithmic total at r3, r4 and r5 (never below). The model heap peak is exact at r3 and r5 in every stage (A, B, C, D); at r4 stage D is 64 bytes below the measurement, hence HEAP_MARGIN = 704 B below.')
    A('')
    A('Per stage (sum over the trials of the run). The measured rows include thread control (r3: T=4, r4: T=6, r5: T=13), so model <= measured is expected for stages that are not allocator-dominated; the total line closes the account.')
    A('')
    A('| r | stage | model | measured (incl. thread ctl) | model - measured |')
    A('|---|---|---:|---:|---:|')
    for r, ev, M in vrows:
        for x in 'ABCD':
            mod = sum(t[x].ops for t in ev['trial'])
            A('| %d | %s | %s | %s | %s |' % (r, x, fmt(mod), fmt(M['stage'][x]), fmt(mod - M['stage'][x])))
        tall, thr = THR[r]
        A('| %d | total | %s | total_all %s - thread ctl/extra %s = %s | %s |' % (r, fmt(ev['total']), fmt(tall), fmt(thr), fmt(M['algo']), fmt(ev['total'] - M['algo'])))
    A('')
    A('Where the slack sits: with the allocator charged zero the model is 3.9e9 (r3), 4.4e10 (r4), 1.2e11 (r5) BELOW the measured total, so the real allocator cost is 0.96-1.3 % of the run and the bound over-charges it by about 40 %. Stage C (91 % of the work at r3-r5) is below its measured row by about the thread-control share; stage D carries the allocator slack.')
    A('')
    A('## 4. Table r3..r8 (K trials executed, every trial charged as dG = 0; time_log2 = log2(total / C(r)), C(r) = 216 + 21 r)')
    A('')
    A('| r | m | a | N = 3*2^a | per-trial ops (A+B+C+D) | fixed (init, E, F, G, H, I, ...) | heap_peak B | arena B | memory B | log2 mem | K | total ops | time_log2 | score |')
    A('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for r, res in table(3, 8):
        for K, (ev, sc) in res.items():
            pt = sum(ev['trial'][0][x].ops for x in 'ABCD')
            A('| %d | %s | %d | %s | %s | %s | %s | %s | %s | %.3f | %d | %s | %.5f | %.5f |' % (r, fmt(ev['m']), ev['amax'], fmt(3 << ev['amax']), fmt(pt), fmt(ev['total'] - K * pt), fmt(ev['heap_peak']), fmt(sc['arena']), fmt(sc['mem_bytes']), sc['mem_log2'], K, fmt(ev['total']), sc['time_log2'], sc['score']))
    A('')
    A('score = ceil5(time_log2) + (ceil3(log2 memory bytes) - 20), as in exec_r5mt/build_package.py. Memory = arena + image + stack; image = text 402,168 + data 32 + static bss 4,851,708 (NT_MAX 96 build, `size` figures in R6_PLAN) + arena; stack 65,536. The r3-r5 rows use the r6 build constants (the measured r5 filing used a 3,721,212 B static bss).')
    A('')
    A('Note r6: the model gives about 7.77e13 ops per trial; R6_PLAN.md estimated 8.4e13 by extrapolating k*N*a (0.11 bit higher). The structural figure is lower because at r6 the plan padding (N = 1.65 * (2m-1)) leaves many radix-3 positions with zero inputs, which the region kernels skip; the same padding is present in the validated r3 (1.61).')
    A('')
    A('## 5. Memory rule')
    A('heap_peak = max over stages of (twiddle table + g + F + stage-live set), each array counted as 64 + 32*slots rounded up to 64 B (headers included), from the allocation walk of the same simulation; it reproduces the measured heap_peak exactly at r3 and r5 (all four stage peaks) and within 64 B at r4. '
      'Arena rule: ARENA >= 1.177 * (heap_peak + 704) rounded up to 64 (r5t ran with 1.177; r4 with 1.144; r3 with 1.185 on the mt build, while a 1.06 arena failed in stage D of the older r3 build). Touched RSS is about 1.135 x live. This is an empirical rule from r3-r5, not a proof that the arena fits at r7/r8 (fragmentation was not simulated).')
    A('')
    A('## 6. r7 and r8 (the existing program, a <= 31)')
    A('r7: a = 29, r8: a = 31 (3*2^31 >= 2m-1 = 6.1e9); both are within the 2-adicity 32 of the Pallas field, so the program runs as written with the numbers above (r8 needs about 0.7 TB of memory). They are paper figures, not executed.')
    A('')
    A('## 7. r9 and above (flagged, not filed)')
    A('For r >= 9, 2m-1 exceeds 3*2^32 (the largest transform the field supports), so this program cannot be extended by changing RR: the multiplications would have to be split into blocks (or use another transform), which changes every figure and is not modelled here. Continuing the trend r6 to r8 (about +4.3 score points per round) would reach the generic Poseidon score (127.009) near r22-r23, but that extrapolates an invalid program, is a lower bound on cost, and is not part of this ledger.')
    A('')
    A('## 8. Leaf charges read from the source (parsed by ledger.py)')
    L = leaf()
    A('Pass charge polynomial = c0 + c1*g + c2*g*(s-1) with g = groups and s = blocks per group (the pass-call wrapper constants are added in ledger.py):')
    A('')
    A('| pass | k=1 | k=2 | k=3 | k=4 |')
    A('|---|---|---|---|---|')
    for nm in ('f', 'i', 'usq', 'umul'):
        cells = []
        for k in range(1, 5):
            p = L.passes[(nm, k)]
            cells.append('%d + %d g + %d g(s-1)' % (p.get((0, 0), 0), p.get((1, 0), 0), p.get((1, 1), 0)))
        A('| %s | %s |' % (nm, ' | '.join(cells)))
    A('')
    A('Radix-3 position kernels (ops per triple position, patterns 0..7, rotation 0): forward ' + ', '.join(str(L.k3[('f', p, 0)]) for p in range(8)) + '; inverse (patterns 1..7) ' + ', '.join(str(L.k3[('i', p, 0)]) for p in range(1, 8)) + '.')
    return '\n'.join(o) + '\n'


if __name__ == '__main__':
    print(report())
    if '--write' in sys.argv:
        open(os.path.join(HERE, 'LEDGER.md'), 'w', encoding='utf-8').write(md())
        print('wrote LEDGER.md')
