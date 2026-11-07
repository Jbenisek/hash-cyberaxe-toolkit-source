# vtpre.py - preprocessing as counted code (same machine as vtprog.py): P1 the set G, P2 the F7 table, P3 the A2 list,
# P4 the A2 and G records, P5 the variant lists R_j, P6 the tables T_j (zero, count, prefix, fill).
# Each pass is a loop body generated here; the interpreter counts the executed operations; the ledger charges
# (items) x (the longest path of the body, measured by executing it) and the loop control.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vt38 import *

def br_ne(a, t, val, lab):
    """branch to lab if register t != val (val 0: bnz)"""
    a('bnz', t, lab) if val == 0 else a('bne', t, val, lab)

# ---------------------------------------------------------------------------------------------------------------
# P1: row 16 of both members as a function of W16 (member x = w; member y = w + dW16)
def gen_g_body(a, nx, w='w'):
    """Falls through iff w is in G.  Constants of rows 12..15 of S*."""
    kx = {}
    for m, (Aa, Ee) in enumerate(((SAX, SEX), (SAY, SEY))):
        A = lambda i: Aa[i+4]; E = lambda i: Ee[i+4]
        kx[m] = ((A(12) + E(12) + S1(E(15)) + CH(E(15), E(14), E(13)) + K[16]) & M,
                 (-A(12) + S0(A(15)) + MAJ(A(15), A(14), A(13))) & M, E(15), A(15), A(14), E(14))
    mW, vW, dW, _ = CELLS[2][16]; mE, vE, dE, _ = CELLS[1][16]; mA, vA, dA, _ = CELLS[0][16]
    if mW: a('and', 't1', w, mW); br_ne(a, 't1', vW, nx)
    a('add', 'wy', w, DW[16]); a('and', 'wy', 'wy', M)
    a('xor', 't1', w, 'wy'); br_ne(a, 't1', dW, nx)
    for m, wr, er, ar in ((0, w, 'ex', 'ax'), (1, 'wy', 'ey', 'ay')):
        c1, c2 = kx[m][0], kx[m][1]
        a('add', er, wr, c1); a('and', er, er, M)
        if m == 0:
            if mE: a('and', 't1', er, mE); br_ne(a, 't1', vE, nx)
            if PQ[16]: a('xor', 't1', er, kx[0][2]); a('and', 't1', 't1', PQ[16]); a('bnz', 't1', nx)
        else:
            a('xor', 't1', 'ex', 'ey'); br_ne(a, 't1', dE, nx)
        a('add', ar, er, c2); a('and', ar, ar, M)
        if m == 0:
            if mA: a('and', 't1', ar, mA); br_ne(a, 't1', vA, nx)
        else:
            a('xor', 't1', 'ax', 'ay'); br_ne(a, 't1', dA, nx)
    # two-bit conditions keyed at row 16 (member x): operands at rows 14, 15 are constants of S*
    regs = {(0, 16): 'ax', (1, 16): 'ex', (2, 16): w}
    const = lambda k, i: (SAX, SEX, SWX)[k][i + (4 if k < 2 else 0)]
    for (k1, i1, b1, eq, k2, i2, b2, row) in X2:
        if row != 16: continue
        need = 0 if eq else 1            # required value of v1 ^ v2
        if (k1, i1) in regs and (k2, i2) in regs:
            a('shr', 't1', regs[(k1, i1)], b1); a('shr', 't2', regs[(k2, i2)], b2); a('xor', 't1', 't1', 't2'); a('and', 't1', 't1', 1)
            br_ne(a, 't1', need, nx)
        else:
            (kv, iv, bv), (kc, ic, bc) = ((k1, i1, b1), (k2, i2, b2)) if (k1, i1) in regs else ((k2, i2, b2), (k1, i1, b1))
            cbit = (const(kc, ic) >> bc) & 1
            a('shr', 't1', regs[(kv, iv)], bv); a('and', 't1', 't1', 1); br_ne(a, 't1', cbit ^ need, nx)

# ---------------------------------------------------------------------------------------------------------------
# P1': the live words of G (L0): for each g, count the E17 that pass the row-17 tests of the program (E17 mask, A17 mask,
# A17-internal conditions); the loop over the 2^32 values of E17 (register e) runs this body; g is live iff the count is not 0.
def gen_live_body(a, gi, nx):
    r = grec(gi, GL[gi]); b = gaddr(gi)
    a('and', 't1', 'e', r[b + 1]); br_ne(a, 't1', r[b + 2], nx)
    a('add', 'A17', 'e', r[b + 3]); a('and', 't1', 'A17', r[b + 4]); br_ne(a, 't1', r[b + 5], nx)
    for n_, (b1, b2, eq) in enumerate(a17int()):
        d_ = 't3' if n_ == 0 else 't1'
        a('shr', d_, 'A17', b1 - b2) if b1 >= b2 else a('shl', d_, 'A17', b2 - b1)
        a('xor', d_, d_, 'A17'); a('and', d_, d_, 1 << b2)
        if not eq: a('xor', d_, d_, 1 << b2)
        if n_: a('or', 't3', 't3', 't1')
    a('bnz', 't3', nx); a('add', 'cnt', 'cnt', 1)

def gen_live_end(a, gi, nx):
    """after the loop of one g: append g to the live list iff its count is not 0"""
    a('bz', 'cnt', nx); a('st', 'lv', gi); a('add', 'lv', 'lv', 1); a('li', 'cnt', 0)

def live_list(cnt=None):
    """the (gi, g) of G whose exact row-17 count (digit DP over E17 with the carry of A17 = E17 + a17) is not 0"""
    out = []
    for gi, g in enumerate(GL):
        r = grec(gi, g); b = gaddr(gi); P = a17int(); st = {(0, 0): 1}
        for i in range(32):
            ns = {}
            for (c, h), n in st.items():
                for e in (0, 1):
                    s = e + (r[b + 3] >> i & 1) + c; x = s & 1; h2 = h | x << i
                    if (r[b + 1] >> i & 1 and e != r[b + 2] >> i & 1) or (r[b + 4] >> i & 1 and x != r[b + 5] >> i & 1): continue
                    if any(max(p, q) == i and ((h2 >> p) ^ (h2 >> q)) & 1 != (0 if w else 1) for p, q, w in P): continue
                    k = (s >> 1, h2 & sum(1 << p | 1 << q for p, q, w in P if max(p, q) > i)); ns[k] = ns.get(k, 0) + n
            st = ns
        n = sum(st.values())
        if cnt is not None: cnt.append(n)
        if n: out.append((gi, g))
    return out
LIVE = live_list()

# ---------------------------------------------------------------------------------------------------------------
# P2: the F7 table: flag at w and w + 2^32 for w in F7, and the value 2 at 2^34 + 1 + w for all w (sentinel region)
def gen_f7_body(a, nx, w='w'):
    rot32(a, 'sw', w, 7, 18, 3, shr3=True, D='D1')
    a('add', 'w2', w, D7); a('and', 'w2', 'w2', M)
    rot32(a, 'sw2', 'w2', 7, 18, 3, shr3=True, D='D2')
    a('add', 'ad', w, (1 << 34) + 1); a('st', 'ad', 'two')          # sentinel region
    a('sub', 't1', 'sw2', 'sw'); a('and', 't1', 't1', M); br_ne(a, 't1', T7, nx)
    a('st', w, 'one'); a('add', 'ad', w, 1 << 32); a('st', 'ad', 'one')

# ---------------------------------------------------------------------------------------------------------------
# P3: the A2 list: conditions on A2 alone
def gen_a2_body(a, nx, x='x'):
    c6 = (sa(6) - S0(sa(5)) - MAJ(sa(5), sa(4), sa(3))) & M
    a('add', 'e6', x, c6); a('and', 'e6', 'e6', M)
    mE, vE, dE, _ = CELLS[1][6]
    assert dE == 0
    if mE: a('and', 't1', 'e6', mE); br_ne(a, 't1', vE, nx)
    # '+' pairs of row 7 against E6, both members (E7 published)
    if PQ[7]:
        a('xor', 't1', 'e6', sex(7)); a('and', 't1', 't1', PQ[7]); a('bnz', 't1', nx)
        a('xor', 't1', 'e6', sey(7)); a('and', 't1', 't1', PQ[7]); a('bnz', 't1', nx)
    # W10 of both members = c10 - E6: s0 difference
    c10x = (sex(10) - sa(6) - S1(sex(9)) - CH(sex(9), sex(8), sex(7)) - K[10]) & M
    c10y = (sey(10) - say(6) - S1(sey(9)) - CH(sey(9), sey(8), sey(7)) - K[10]) & M
    a('rsub', 'w10x', c10x, 'e6'); a('and', 'w10x', 'w10x', M); a('rsub', 'w10y', c10y, 'e6'); a('and', 'w10y', 'w10y', M)
    a('sub', 't1', 'w10y', 'w10x'); a('and', 't1', 't1', M); br_ne(a, 't1', DW[10], nx)
    rot32(a, 'sx', 'w10x', 7, 18, 3, shr3=True, D='D1'); rot32(a, 'sy', 'w10y', 7, 18, 3, shr3=True, D='D2')
    a('sub', 't1', 'sy', 'sx'); a('and', 't1', 't1', M); br_ne(a, 't1', DS0[10], nx)

# ---------------------------------------------------------------------------------------------------------------
# P4: records.  A2 record (2 words) and G record (12 words) exactly as in vtprog.tables()
def gen_a2rec(a, x='x', dst='ra'):
    """x = A2 (register, masked); writes the two record words to mem[dst], mem[dst+1] (dst a register)."""
    e6c = (sa(6) - S0(sa(5)) - MAJ(sa(5), sa(4), sa(3))) & M
    a('add', 'e6', x, e6c); a('and', 'e6', 'e6', M)
    rot32(a, 'S0x', x, 2, 13, 22); a('and', 'S0x', 'S0x', M)
    # MAJ(A4, A3, A2) = (A4 & (A3 ^ A2)) ^ (A3 & A2)
    a('xor', 'mj', x, sa(3)); a('and', 'mj', 'mj', sa(4)); a('and', 't2', x, sa(3)); a('xor', 'mj', 'mj', 't2')
    a('rsub', 'e5b', (sa(5) - S0(sa(4))) & M, 'mj'); a('and', 'e5b', 'e5b', M)           # E5 - A1
    # c9 = E9 - 2 A5 + S0(A4) + MAJ(A4,A3,A2) - S1(E8) - CH(E8,E7,E6) - K9 ; CH(E8,E7,E6) = ((E7 ^ E6) & E8) ^ E6
    for tag, E, A in (('x', sex, sa), ('y', sey, say)):
        a('xor', 't2', 'e6', E(7)); a('and', 't2', 't2', E(8)); a('xor', 't2', 't2', 'e6')
        a('rsub', 'c9' + tag, (E(9) - 2 * sa(5) + S0(sa(4)) - S1(E(8)) - K[9]) & M, 't2')
        a('add', 'c9' + tag, 'c9' + tag, 'mj'); a('and', 'c9' + tag, 'c9' + tag, M)
        c10 = (E(10) - A(6) - S1(E(9)) - CH(E(9), E(8), E(7)) - K[10]) & M      # W10 = c10 - E6
        a('rsub', 'w10' + tag, c10, 'e6'); a('and', 'w10' + tag, 'w10' + tag, M)
    a('add', 'k10', 'w10x', s1(SWX[15])); a('and', 'k10', 'k10', M)
    a('shl', 'r0', 'k10', 32); a('or', 'r0', 'r0', x)
    a('shl', 't1', 'S0x', 64); a('or', 'r0', 'r0', 't1')
    a('shl', 't1', 'e6', 96); a('or', 'r0', 'r0', 't1')
    a('shl', 't1', 'e5b', 128); a('or', 'r0', 'r0', 't1')
    a('st', dst, 'r0')
    a('shl', 'r1', 'c9y', 32); a('or', 'r1', 'r1', 'c9x')
    a('shl', 't1', 'w10x', 64); a('or', 'r1', 'r1', 't1'); a('shl', 't1', 'w10y', 96); a('or', 'r1', 'r1', 't1')
    a('add', 'da', dst, 1); a('st', 'da', 'r1')

def gen_grec(a, gi, g):
    """G record of the constant g = W16x: counted straight-line code computing the words of vtprog.grec(gi, g)."""
    vals = grec(gi, g); base = gaddr(gi)
    for m, (Aa, Ee) in enumerate(((SAX, SEX), (SAY, SEY))):
        A = lambda i: Aa[i+4]; E = lambda i: Ee[i+4]
        a('li', 'wm', g if m == 0 else (g - DW16) & M)
        a('add', 'e16', 'wm', (A(12) + E(12) + S1(E(15)) + CH(E(15), E(14), E(13)) + K[16]) & M); a('and', 'e16', 'e16', M)
        a('add', 'a16', 'e16', (-A(12) + S0(A(15)) + MAJ(A(15), A(14), A(13))) & M); a('and', 'a16', 'a16', M)
        rot32(a, 'sE', 'e16', 6, 11, 25)
        # CH(e16, E15, E14) = ((E15 ^ E14) & e16) ^ E14
        a('and', 't1', 'e16', E(15) ^ E(14)); a('xor', 't1', 't1', E(14))
        a('add', 'c17', 'sE', 't1'); a('add', 'c17', 'c17', (A(13) + E(13) + K[17]) & M); a('and', 'c17', 'c17', M)
        rot32(a, 'sA', 'a16', 2, 13, 22)
        # MAJ(a16, A15, A14) = (a16 & (A15 ^ A14)) ^ (A15 & A14)
        a('and', 't1', 'a16', A(15) ^ A(14)); a('xor', 't1', 't1', A(15) & A(14))
        a('add', 'a17', 'sA', 't1'); a('add', 'a17', 'a17', (-A(13)) & M); a('and', 'a17', 'a17', M)
        if m == 0:
            a('sti', base, 'c17'); a('sti', base + 3, 'a17'); a('sti', base + 8, 'a16'); a('sti', base + 9, 'e16')
            a('add', 'e16x', 'e16', 0); a('add', 'a16x', 'a16', 0)
        else:
            a('sti', base + 10, 'a16'); a('sti', base + 11, 'e16')
    # masks do not depend on g; values: cell values plus the (possibly inverted) bits of e16x / a16x of the folded conditions
    mE, vE, _, _ = CELLS[1][17]; mA, vA, _, _ = CELLS[0][17]
    a('sti', base + 1, vals[base + 1]); a('sti', base + 4, vals[base + 4]); a('sti', base + 6, g); a('sti', base + 7, 0)
    a('li', 'vE', vE); a('li', 'vA', vA)
    for (k1, i1, b1, eq, k2, i2, b2, row) in X2:
        if row == 17 and i1 == 16 and i2 == 17:
            src = 'e16x' if k1 == 1 else 'a16x'
            a('shr', 't1', src, b1); a('and', 't1', 't1', 1)
            if not eq: a('xor', 't1', 't1', 1)
            a('shl', 't1', 't1', b2); a('or', 'vE' if k2 == 1 else 'vA', 'vE' if k2 == 1 else 'vA', 't1')
    a('and', 't1', 'e16x', PQ[17]); a('or', 'vE', 'vE', 't1')
    a('sti', base + 2, 'vE'); a('sti', base + 5, 'vA')

# ---------------------------------------------------------------------------------------------------------------
# P5: the variant list R_j.  For A0 = A0_j (instruction field) and an A2 of the list (record at register 'ra'), the
# candidates A1 = lo + r, r in [r0, r1), lo = (E6 & 0xe0000000) - (E5 - A1) (the '+' pair of rows 5/6 confines A1 to one
# window of 2^29).  Tests: dW8 (through CH only), ds0(W9), ds0(W8) (A0 enters W8 = Fx - A0).  Valid candidates append three
# words (c7 + 2^32, eb, c9x) at the list pointer 'lp'.
def gen_enum_setup(a, a0):
    """Per (A0, A2): constants from the A2 record at register ra (word 0: A2 | K10 << 32 | S0(A2) << 64 | E6 << 96 |
    (E5 - A1) << 128; word 1: c9x | c9y << 32 | ...)."""
    a('ld', 'w0', 'ra'); a('add', 't1', 'ra', 1); a('ld', 'w1r', 't1')
    a('and', 'A2', 'w0', M); a('shr', 'S0A2', 'w0', 64); a('and', 'S0A2', 'S0A2', M)
    a('shr', 'E6', 'w0', 96); a('and', 'E6', 'E6', M); a('shr', 'k5', 'w0', 128); a('and', 'k5', 'w0', M) if False else (a('shr', 'k5', 'w0', 128), a('and', 'k5', 'k5', M))
    a('and', 'c9x', 'w1r', M)
    # window start lo = (E6 & e0000000) - k5
    a('and', 'lo', 'E6', 0xe0000000); a('sub', 'lo', 'lo', 'k5'); a('and', 'lo', 'lo', M)
    # constants of the tests: cdw8 = DW8 - (ky - kx), kx' = kx - A0 (W8x = kx' + MAJ(A3,A2,A1) - CH(E7x,E6,E5))
    a('xor', 'xa32', 'A2', sa(3)); a('and', 'aa32', 'A2', sa(3))
    a('and', 'e67x', 'E6', sex(7)); a('and', 'e67y', 'E6', sey(7))
    # c7 constant: E7x - 2 A3 + S0(A2) - S1(E6) - K7  (S1(E6) by a rotation)
    rot32(a, 's1e6', 'E6', 6, 11, 25); a('and', 's1e6', 's1e6', M)
    a('sub', 'cst7', 'S0A2', 's1e6'); a('add', 'cst7', 'cst7', (sex(7) - 2*sa(3) - K[7]) & M); a('and', 'cst7', 'cst7', M)
    a('xor', 'x20', 'A2', a0); a('and', 'a20', 'A2', a0)
    a('sub', 'A2ad', 'ra', A2T); a('shr', 'A2ad', 'A2ad', 1); a('shl', 'A2ad', 'A2ad', 128)   # A2 index << 128
    a('shr', 'k10', 'w0', 32); a('and', 'k10', 'k10', M)                                     # W10x + s1(W15x)

def gen_enum_body(a, a0, nx):
    """One candidate: register r = r; falls to the append code iff valid.  Costs: 9 ops to the first test."""
    cdw8 = (DW[8] - ((sey(8) - 2*sa(4) + S0(sa(3)) - S1(sey(7)) - K[8]) - (sex(8) - 2*sa(4) + S0(sa(3)) - S1(sex(7)) - K[8]))) & M
    kx = (sex(8) - 2*sa(4) + S0(sa(3)) - S1(sex(7)) - K[8] - a0) & M
    a('add', 'a1', 'lo', 'r'); a('add', 'E5', 'a1', 'k5')
    a('and', 'chx', 'E5', ~sex(7) & M); a('xor', 'chx', 'chx', 'e67x')
    a('and', 'chy', 'E5', ~sey(7) & M); a('xor', 'chy', 'chy', 'e67y')
    a('sub', 'd', 'chx', 'chy'); a('and', 'd', 'd', M); br_ne(a, 'd', cdw8, nx)
    # ds0(W9): w9 = c9x - A1
    a('sub', 'w9', 'c9x', 'a1'); a('and', 'w9', 'w9', M)
    a('add', 'w9p', 'w9', DW[9]); a('and', 'w9p', 'w9p', M)
    rot32(a, 'sa', 'w9', 7, 18, 3, shr3=True, D='D1'); rot32(a, 'sb', 'w9p', 7, 18, 3, shr3=True, D='D2')
    a('sub', 'd', 'sb', 'sa'); a('and', 'd', 'd', M); br_ne(a, 'd', DS0[9], nx)
    # ds0(W8): W8x = kx' + MAJ(A3, A2, A1) - CH(E7x, E6, E5)
    a('and', 'mj', 'a1', 'xa32'); a('xor', 'mj', 'mj', 'aa32')
    a('add', 'w8', 'mj', kx); a('sub', 'w8', 'w8', 'chx'); a('and', 'w8', 'w8', M)
    a('add', 'w8p', 'w8', DW[8]); a('and', 'w8p', 'w8p', M)
    rot32(a, 'sa', 'w8', 7, 18, 3, shr3=True, D='D1'); rot32(a, 'sb', 'w8p', 7, 18, 3, shr3=True, D='D2')
    a('sub', 'd', 'sb', 'sa'); a('and', 'd', 'd', M); br_ne(a, 'd', DS0[8], nx)

def gen_enum_append(a, a0):
    """Valid candidate (registers of the body): append the three list words at 'lp'."""
    # c7 = cst7 + MAJ(A2, A1, A0) - CH(E6, E5, E4) with E4 = A4 + A0 - S0(A3) - MAJ(A3, A2, A1) = (const) - mj
    a('and', 'm20', 'a1', 'x20'); a('xor', 'm20', 'm20', 'a20')
    a('rsub', 'E4', (sa(4) + a0 - S0(sa(3))) & M, 'mj')
    a('xor', 't', 'E5', 'E4'); a('and', 't', 't', 'E6'); a('xor', 't', 't', 'E4')          # CH(E6, E5, E4) = ((E5 ^ E4) & E6) ^ E4
    a('add', 'c7', 'cst7', 'm20'); a('sub', 'c7', 'c7', 't'); a('and', 'c7', 'c7', M); a('add', 'c7', 'c7', 1 << 32)
    a('and', 'a1m', 'a1', M)
    rot32(a, 's0a1', 'a1m', 2, 13, 22); a('and', 's0a1', 's0a1', M)
    # fields word (vt38.mkent): A1 | U << 32 | Q << 64 | S0(A1) << 96 | a2i << 128 | E1a << 160 | KCA << 224
    a('and', 't', 'a1m', a0); a('sub', 'u', 'A2', 's0a1'); a('sub', 'u', 'u', 't'); a('add', 'u', 'u', (-K[2]) & M); a('and', 'u', 'u', M)
    a('xor', 'qq', 'a1m', a0); a('add', 'kca', 'k10', 'a1m'); a('and', 'kca', 'kca', M)
    a('add', 'e1a', 'a1m', (1 - S0(a0)) & M); a('and', 'e1a', 'e1a', M); a('shl', 'e1a', 'e1a', 160)
    a('shl', 'e1', 'u', 32); a('or', 'e1', 'e1', 'a1m'); a('shl', 't', 'qq', 64); a('or', 'e1', 'e1', 't'); a('shl', 't', 's0a1', 96); a('or', 'e1', 'e1', 't')
    a('or', 'e1', 'e1', 'A2ad'); a('or', 'e1', 'e1', 'e1a'); a('shl', 't', 'kca', 224); a('or', 'e1', 'e1', 't')
    a('st', 'lp', 'c7'); a('add', 'lp', 'lp', 1); a('st', 'lp', 'e1'); a('add', 'lp', 'lp', 1); a('st', 'lp', 'c9x'); a('add', 'lp', 'lp', 1)

# ---------------------------------------------------------------------------------------------------------------
# P6: the table T_j.  Header word of (Y, Z0) at HB + (Y << 32 | Z0), HB = HDR | j << 64.  Passes:
#   zero   : header := 0                                                                      (4 ops per header)
#   count  : header += 1 for every (Y, variant, g) with Z0 = g - X, X = s0(Y + A1) - A1 + c9x  (loop over Y inside a variant)
#   prefix : header := address of the first entry (or EMPTY), entries of a bucket followed by a sentinel entry
#   fill   : entries written backwards from the end of each bucket (header decremented by 2 per entry)
def gen_zero_body(a): a('st', 'h', 'zero'); a('add', 'h', 'h', 1)

def gen_count_body(a, hb):
    """Registers: Y (loop), A1 (masked), c9x; variant constants.  One (Y, variant): 22 header increments (live words)."""
    a('add', 'u', 'Y', 'A1'); a('and', 'u', 'u', M)
    rot32(a, 'su', 'u', 7, 18, 3, shr3=True)
    a('sub', 'X', 'su', 'A1'); a('add', 'X', 'X', 'c9x')
    a('shl', 'Ys', 'Y', 32); a('add', 'Ys', 'Ys', hb)
    for gi, g in LIVE:
        a('rsub', 'Z', g, 'X'); a('and', 'Z', 'Z', M); a('add', 'I', 'Ys', 'Z'); a('ld', 'H', 'I'); a('add', 'H', 'H', 1); a('st', 'I', 'H')

def gen_fill_body(a, hb):
    """One (Y, variant): 2-word entry (c7', w1e + gw(gi)) written backwards at the bucket of each live g."""
    a('add', 'u', 'Y', 'A1'); a('and', 'u', 'u', M)
    rot32(a, 'su', 'u', 7, 18, 3, shr3=True)
    a('sub', 'X', 'su', 'A1'); a('add', 'X', 'X', 'c9x')
    a('shl', 'Ys', 'Y', 32); a('add', 'Ys', 'Ys', hb)
    for gi, g in LIVE:
        a('rsub', 'Z', g, 'X'); a('and', 'Z', 'Z', M); a('add', 'I', 'Ys', 'Z'); a('ld', 'H', 'I'); a('sub', 'H', 'H', ESZ); a('st', 'I', 'H')
        a('st', 'H', 'c7'); a('add', 't', 'H', 1); a('add', 't2', 'w1e', gw(gi)); a('st', 't', 't2')

# ---- the bodies used by the ledger of this derivative (R38L): 16 headers per zero iteration; Y loop with u = Y + A1 (mod 2^32) as the
# loop counter in two segments (u from A1 to 2^32 - 1, then u from 0 to A1 - 1), the header base Ys = hb + (Y << 32) running with it,
# and c9x - A1 folded into one constant cc.  The loop control is part of the measured iteration.  (gen_zero_body, gen_count_body and
# gen_fill_body above are the bodies of the earlier derivative; t_pre2.py runs those.)
def gen_zero16(a, hend, top='ztop'):
    """one iteration of the header-zeroing pass: 16 headers (st, add) and the loop branch"""
    a.L(top)
    for _ in range(16): a('st', 'h', 'zero'); a('add', 'h', 'h', 1)
    a('bne', 'h', hend, top)

def gen_count_iter(a):
    """one (u, variant) iteration of the count pass, without the loop branch: 22 header increments (live words)"""
    rot32(a, 'su', 'u', 7, 18, 3, shr3=True)
    a('add', 'X', 'su', 'cc')
    for gi, g in LIVE:
        a('rsub', 'Z', g, 'X'); a('and', 'Z', 'Z', M); a('add', 'I', 'Ys', 'Z'); a('ld', 'H', 'I'); a('add', 'H', 'H', 1); a('st', 'I', 'H')
    a('add', 'u', 'u', 1); a('add', 'Ys', 'Ys', 1 << 32)

def gen_fill_iter(a):
    """one (u, variant) iteration of the fill pass, without the loop branch: 2-word entry (c7', w1e + gw(gi)) written backwards at the bucket of each live g"""
    rot32(a, 'su', 'u', 7, 18, 3, shr3=True)
    a('add', 'X', 'su', 'cc')
    for gi, g in LIVE:
        a('rsub', 'Z', g, 'X'); a('and', 'Z', 'Z', M); a('add', 'I', 'Ys', 'Z'); a('ld', 'H', 'I'); a('sub', 'H', 'H', ESZ); a('st', 'I', 'H')
        a('st', 'H', 'c7'); a('add', 't', 'H', 1); a('add', 't2', 'w1e', gw(gi)); a('st', 't', 't2')
    a('add', 'u', 'u', 1); a('add', 'Ys', 'Ys', 1 << 32)

def gen_loads(a, fill):
    """the variant's list words at the list pointer lp (c7 + 2^32, eb, c9x): the count pass reads eb and c9x, the fill pass all three"""
    if fill: a('ld', 'c7', 'lp')
    a('add', 'lp', 'lp', 1); a('ld', 'w1e', 'lp'); a('add', 'lp', 'lp', 1); a('ld', 'c9x', 'lp'); a('add', 'lp', 'lp', 1)

def gen_variant_pass(a, hb, fill, lim1=1 << 32, lim2='A1'):
    """one variant of the count (fill = False) or fill (fill = True) pass over all 2^32 values of Y: segment 1 runs u from A1 to lim1 = 2^32 - 1
    (Y = u - A1), segment 2 runs u from 0 to lim2 = A1 - 1 (Y = u + 2^32 - A1) unless A1 = 0.  The branch back to 'vtop' is the loop over the list."""
    a.L('vtop'); gen_loads(a, fill); a('and', 'A1', 'w1e', M)
    a('add', 'u', 'A1', 0); a('li', 'Ys', hb); a('sub', 'cc', 'c9x', 'A1')
    a.L('seg1'); (gen_fill_iter if fill else gen_count_iter)(a); a('bne', 'u', lim1, 'seg1')
    a('bz', 'A1', 'vdone')
    a('li', 'u', 0); a('shl', 't', 'A1', 32); a('rsub', 'Ys', hb + (1 << 64), 't')
    a.L('seg2'); (gen_fill_iter if fill else gen_count_iter)(a); a('bne', 'u', lim2, 'seg2')
    a.L('vdone'); a('bne', 'lp', 'lpend', 'vtop')

def gen_prefix_body(a, empty_lab_unused=None):
    """One header (register h): count c = mem[h]; empty -> EMPTY; else header := end of bucket (entries are filled backwards
    from it), sentinel entry written at the end, 'run' advanced by 2 (c + 1)."""
    nz, done = 'pnz', 'pdone'
    a('ld', 'c', 'h'); a('bnz', 'c', nz)
    a('li', 'e0', EMPTY); a('st', 'h', 'e0'); a('jmp', done)
    a.L(nz)
    a('shl', 'c2', 'c', 1)                                                  # 2c
    a('add', 'run', 'run', 'c2'); a('st', 'h', 'run')                      # header := end of the bucket (fill decrements it to the start)
    a('li', 'sw', SENT); a('st', 'run', 'sw'); a('add', 't', 'run', 1); a('st', 't', 'zero')
    a('add', 'run', 'run', ESZ)
    a.L(done)
