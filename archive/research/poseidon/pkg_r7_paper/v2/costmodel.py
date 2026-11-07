"""Cost model of the Orchard Poseidon algebraic collision program (the sources of the proof appendix, single thread, K trials).

Nothing here is measured from a run at r = 7.  Every charge is read from the C source:
  * leaf kernel charges (NTT butterfly blocks, whole passes, radix-3 position kernels) are PARSED from ntt_kern.h and ntt_a3.h
    (LD(n)/ST(n) = 2n, CTL(n) = n, each fp_add/sub/mul/sqr, BF/BFN/IB/IBN macros = 3/2/3/2);
  * the control flow of ntt.c, lean.c, line.c, hgcd.c, common.c, split.c, single.c is PORTED statement by statement (the charge of each statement
    is written next to it in the source and copied here); stage E, F and the coin draw are in costmodel_e.py.
Bounds (stated, not proved):
  A1 normal Euclid in stage D: every quotient has degree 1 (declared in H1-charging-rules);
  A2 every trial is charged as gcd degree 0 for stages A to D, and in addition with stage E at its cap (ZCAP rounds at degree DMAX), F and G;
  A3 allocator: every xalloc walks at most 2L+1 blocks (L = live blocks), every xfree costs <= 105, plan_invN lookups cost 7*(number of distinct
     plan sizes); stage E uses L <= 16.
usage: MODEL_SRC=<directory with the C files> python3 costmodel.py
"""
import re, os, sys, math, functools
import costmodel_e as LE                  # worst-case charges of the coin draw, stage E (capped isolation) and stage F (this folder)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('MODEL_SRC', HERE)

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


# ---------------------------------------------------------------- score
def ceil5(x): return math.ceil(x * 100000 - 1e-6) / 100000
def ceil3(x): return math.ceil(x * 1000) / 1000


IMAGE_EXTRA = 399216 + 32 + 4851196        # text + data + static bss besides the arena, `size` of the r = 7 build of the shipped sources (proof section 7); STACK below
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
            stage=dict(A=1126, B=1266078492, C=344571920769, D=66201757118), gcd=[66201756104]),
    4: dict(algo=3977289295772, dGs=[0, 1], F=45122, heap=1072730624,
            stage=dict(A=2252, B=10996045694, C=3184945291322, D=796457597837), gcd=[398228799447, 398228796261]),
    5: dict(algo=9171678989504, dGs=[1], F=44132, heap=4759669952,
            stage=dict(A=1126, B=23502612205, C=6583714961195, D=2598489950710), gcd=[2598489949696]),
}


def validation():
    rows = []
    for r in (3, 4, 5):
        M = MEAS[r]
        ev = evaluate(r, M['dGs'], F_val=M['F'], E_val=E_DG1)
        rows.append((r, ev, M))
    return rows


def fmt(n): return '{:,}'.format(int(n))


# ---------------------------------------------------------------- the account of the paper entry
OFFLINE_BOUND = 1000000        # offline derivation of the literals of pallas_consts.h / line.c (Montgomery forms of 201 organizer constants, 5^q, 2^65, the exponent (4(p-1)+1)/5): at most 4,000 operations per literal for at most 250 literals


def paper_account(r=7, K=2):
    ev = evaluate_paper(r, K)
    sc = score(ev['total'] + OFFLINE_BOUND, r, ev['heap_peak'])
    return ev, sc


def validation_r3_coin():
    """the shipped program at RR = 3 with the coin centre of seed 2 (one trial, gcd degree 2, stage E: 3 rounds at degree 2): model vs counters."""
    global A_CENTRE_OPS
    old = A_CENTRE_OPS; A_CENTRE_OPS = LE.COIN_DRAW
    try:
        F1, _ = LE.stage_F()
        ev = evaluate(3, [2], F_val=F1, E_val=LE.stage_E(3, 2))
    finally:
        A_CENTRE_OPS = old
    return ev, 409369405120


def main():
    print('VALIDATION against counters (algorithmic totals, thread charges excluded)')
    print('run | model total | measured | model - measured | slack (bits) | heap model | heap measured')
    for r, ev, M in validation():
        d = ev['total'] - M['algo']
        print('r=%d fixed centre | %s | %s | %s | %.3e | %s | %s' % (r, fmt(ev['total']), fmt(M['algo']), fmt(d), math.log2(ev['total'] / M['algo']), fmt(ev['heap_peak']), fmt(M['heap'])))
    ev, meas = validation_r3_coin()
    print('r=3 coin centre | %s | %s | %s | %.3e | %s | %s' % (fmt(ev['total']), fmt(meas), fmt(ev['total'] - meas), math.log2(ev['total'] / meas), fmt(ev['heap_peak']), fmt(244745792)))
    ev, sc = paper_account(7, 2)
    t = ev['trial'][0]
    print('r = 7, K = 2')
    for x in 'ABCD': print('stage %s per trial = %s' % (x, fmt(t[x].ops)))
    print('stage E per trial (cap) = %s, stage F = %s, stage G = %s, trial extra = %d' % (fmt(ev['E1']), fmt(ev['F1']), fmt(ev['G1']), TRIAL_EXTRA))
    print('init = %s, line setup = %d, plan_invN misses = %s, stage H = %d, stage I = %d, offline = %s' % (fmt(ev['init']), LINE_STAGE, fmt(ev['miss']), H_STAGE, I_STAGE, fmt(OFFLINE_BOUND)))
    N = ev['total'] + OFFLINE_BOUND
    print('N =', fmt(N))
    print('time_log2 = %.5f' % sc['time_log2'])
    print('heap_peak = %s, arena = %s, memory = %s bytes, log2 = %.3f' % (fmt(ev['heap_peak']), fmt(sc['arena']), fmt(sc['mem_bytes']), sc['mem_log2']))
    print('score = %.5f' % sc['score'])


if __name__ == '__main__':
    main()
