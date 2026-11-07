#!/usr/bin/env python3
# ledger38.py - the exact ledger of the r38 variant-table attack, derivative R38d (Appendix C).  ledger38.py of the base
# package with four inputs added: the tables list the NGW = 22 live words of G (L0), entries are ESZ = 2 words (L5), the deep
# path has its own counter N2 (L4), and the W7/A17 paths and the fill pass are those of the levered program (L2).  Every operation count
# is an executed-operation count of the counted programs (runs/costs.json, runs/pre1.json, runs/pre2.json); probabilities are exact rationals except
# q3_model and delta.  With --base it is ledger38.py of 37742a53 (NGW = 32, ESZ = 3, no N2) and reproduces 2^71.695220.
#   python3 ledger38.py [--base] [--q3 -101.5] [--delta 1] [--eps-log2 -4] [--ac 70] [--as 60] [--dev 60] [--succ 0.39]
import json, math, os, sys, argparse
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
getcontext().prec = 80
HERE = os.path.dirname(os.path.abspath(__file__)); RUNS = os.path.join(HERE, '..', 'runs')
C = 2728                                   # collision-frontier-v5, 38 steps (one target compression = C word operations)
SR = 191773672732                          # sum_j |R_j| (runs/rc_full: exact)
F7 = 287309824                             # |F7|
NB = 256                                   # A0 blocks (tables)
MASK_E17_BITS = 10
CNT17 = 1 << 20                            # sum over the 32 words g of G of #{E17 : both row-17 tests pass}; 0 for the 10 dead words (L0, exact)

def log2d(x): return (Decimal(x.numerator) / Decimal(x.denominator)).ln() / Decimal(2).ln() if isinstance(x, Fr) else Decimal(x).ln() / Decimal(2).ln()
def up5(x): return math.ceil(float(x) * 1e5 - 1e-9) / 1e5

def pre_ops(cs, p1, p2, ngw, lev):
    """Preprocessing in word operations: every term is (items) x (executed operations per item) + loop control."""
    W32 = 1 << 32
    t = {}
    t['P1_G'] = W32 * (p1['G_hit_ops'] + 3)                         # longest path of the row-16 test + loop
    if lev: t['P1_live'] = 32 * W32 * (p1['LIVE_ops'] + 3) + 32 * p1['LIVE_g']   # L0: the row-17 count of every g of G (exhaustive over E17)
    t['P2_F7'] = W32 * (p1['F7_in_ops'] + 3)
    t['P2_zero'] = 4 * ((1 << 34) + W32 + 2)                          # zero the F7 table region (addresses 0 .. 2^34 + 2^32 + 1) before P2 writes its flags
    t['P3_A2'] = W32 * (p1['A2_hit_ops'] + 3) + 768 * 4
    t['P4_rec'] = p1['A2REC_total_ops'] + p1['GREC_total_ops']
    t['P5_enum'] = NB * 768 * (p2['P5_SETUP'] + (1 << 29) * (p2['P5_BODY_MAX'] + p2['P5_LOOP'])) + SR * p2['P5_APPEND']
    t['P6_zero'] = NB * (1 << 64) * 4
    entries = SR * ngw * W32                                         # (Y, variant, g) triples = entries of all tables
    t['P6_count'] = SR * W32 * (p2['P6_COUNT'] + 3) + SR * 16
    t['P6_fill'] = SR * W32 * (p2['P6_FILL'] + 3) + SR * 16
    t['P6_prefix'] = NB * (1 << 64) * (p2['P6_PREFIX_EMPTY'] + 3) + min(entries, NB * (1 << 64)) * (p2['P6_PREFIX_NONEMPTY'] - p2['P6_PREFIX_EMPTY'])   # nonempty headers <= min(entries, headers)
    return t

def ledger(q3_log2=-101.5, delta=Fr(1), eps=(Fr(1, 1 << 16), Fr(1, 1 << 14), Fr(1, 1 << 7)), ac=70, as_=60, dev=60, succ=Fr(39, 100), tol=Fr(1, 2 ** 60), show=True,
           costs=None, p1=None, p2=None, base=False, ngw=None, n2=None, eps2=Fr(1, 1 << 5), esz=None):
    lev = not base; esz = esz if esz is not None else (3 if base else 2)
    ngw = ngw if ngw is not None else (32 if base else 22); n2 = n2 if n2 is not None else lev
    cs = costs or json.load(open(os.path.join(RUNS, 'costs.json')))
    p1 = p1 or json.load(open(os.path.join(RUNS, 'pre1.json'))); p2 = p2 or json.load(open(os.path.join(RUNS, 'pre2.json')))
    if base and eps == (Fr(1, 1 << 16), Fr(1, 1 << 14), Fr(1, 1 << 7)): eps = Fr(1, 16)
    eps_ne, eps_nw, eps_n1 = eps if isinstance(eps, tuple) else (eps, eps, eps)
    MAXB = 14 * ngw * 768                                            # Lemma 6 bucket bound
    p_f7 = Fr(F7, 1 << 32)
    ent = Fr(SR * ngw, 1 << 32)                                      # E[entries per group] (exact, H1)
    E_NE = esz * (ent + NB); E_NW = ent * p_f7; E_N1 = E_NW * Fr(1, 2 ** MASK_E17_BITS)
    E_N2 = SR * p_f7 * Fr(CNT17, 1 << 64)                            # L4: W7 passes that pass both row-17 tests (H1, Lemma 4)
    B_ent = NB * MAXB
    B_NE, B_NW, B_N1, B_N2 = esz * (B_ent + NB), B_ent, B_ent, B_ent
    # per-group success rate lower bound
    fl = math.floor(q3_log2); q3 = Fr(2) ** fl * Fr(math.floor(2 ** (q3_log2 - fl) * 2 ** 40), 2 ** 40)
    S = SR * p_f7 * q3
    q_lb = S * (1 - delta / 2)
    per_group_fixed = cs['P0'] + cs['EPI'] + (NB // 4) * (cs['GROUP4'] - 4 * cs['ITER'])      # the sentinel iteration (ITER) of every block is charged through NE
    cw = cs['PASS_ENTRY'] + cs['X_E17']
    if n2: c1 = cs['X_A17int'] - cs['X_E17']; c2 = cs['X_SUCC'] - cs['X_A17int']
    else: c1 = cs['X_SUCC'] - cs['X_E17']; c2 = 0
    # iterate N_G and the Chebyshev overflow bounds (P_k <= B_k / (eps_k^2 N_G E_k))
    Ptot = Fr(0)
    for _ in range(6):
        x = (Decimal(1) - Decimal(succ.numerator) / Decimal(succ.denominator) - Decimal(Ptot.numerator) / Decimal(Ptot.denominator) - Decimal(tol.numerator) / Decimal(tol.denominator))
        mu = -x.ln()
        NG = int(-((-Fr(int(mu * 10 ** 30), 10 ** 30)) // q_lb)) + 1
        Pk = [Fr(B_NE) / (eps_ne ** 2 * NG * E_NE), Fr(B_NW) / (eps_nw ** 2 * NG * E_NW), Fr(B_N1) / (eps_n1 ** 2 * NG * E_N1)]
        if n2: Pk.append(Fr(B_N2) / (eps2 ** 2 * NG * E_N2))
        Pn = sum(Pk)
        if abs(Pn - Ptot) < Fr(1, 10 ** 12) * max(Pn, Fr(1, 10 ** 12)): Ptot = Pn; break
        Ptot = Pn
    NE_MAX = math.ceil(NG * E_NE * (1 + eps_ne)); NW_MAX = math.ceil(NG * E_NW * (1 + eps_nw)); N1_MAX = math.ceil(NG * E_N1 * (1 + eps_n1))
    N2_MAX = math.ceil(NG * E_N2 * (1 + eps2)) if n2 else 0
    online = NG * per_group_fixed + (cs['ITER'] // esz) * (NE_MAX + B_NE) + cw * (NW_MAX + B_NW) + c1 * (N1_MAX + B_N1) + (c2 * (N2_MAX + B_N2) if n2 else 0)
    pre = pre_ops(cs, p1, p2, ngw, lev); pre_total = sum(pre.values())
    init, fin_ops, fin_units = 1 << 32, 1024, 6          # init: generation of the program text (about 2^21 instructions at most 2^11 operations each)
    # memory in 32-byte words: headers, esz-word entries, sentinels, F7 table (flags + sentinel region), R_j lists, records
    entries_all = SR * ngw * (1 << 32)
    words = NB * (1 << 64) + esz * entries_all + esz * min(entries_all, NB * (1 << 64)) + (1 << 33) + 3 * SR + 20000
    mem_log2_bytes = float(log2d(Fr(words * 32)))
    allow = Fr(2) ** ac + Fr(2) ** as_ + Fr(2) ** dev
    T = allow + Fr(pre_total + init + online + fin_ops, C) + NG + fin_units
    pre_incl = allow + Fr(pre_total, C)
    lg = log2d(T); tl = up5(lg)
    k = int(round(tl * 100000)); n_, d_ = T.numerator, T.denominator
    tight_up = n_ ** 100000 <= (2 ** k) * d_ ** 100000           # T <= 2^(k/10^5)
    tight_down = n_ ** 100000 > (2 ** (k - 1)) * d_ ** 100000    # T >  2^((k-1)/10^5): k is the smallest such integer
    assert tight_up and tight_down
    mu_act = Decimal((NG * q_lb).numerator) / Decimal((NG * q_lb).denominator)
    success_bound = float(1 - (-mu_act).exp() - Decimal(Ptot.numerator) / Decimal(Ptot.denominator))
    out = dict(q3_log2=q3_log2, S_log2=float(log2d(S)), q_lb_log2=float(log2d(q_lb)), NG=NG, NG_log2=float(log2d(Fr(NG))),
               NE_MAX=NE_MAX, NW_MAX=NW_MAX, N1_MAX=N1_MAX, N2_MAX=N2_MAX, E_NE=float(E_NE), E_NW=float(E_NW), E_N1=float(E_N1), E_N2=float(E_N2),
               cap_overflow_total=float(Ptot), success_lower_bound=success_bound,
               per_group_fixed=per_group_fixed, cw=cw, c1=c1, c2=c2, online_ops=online, online_ops_log2=float(log2d(Fr(online))),
               pre_ops=pre_total, pre_units_log2=float(log2d(Fr(pre_total, C))), pre_terms={k: float(log2d(Fr(v))) for k, v in pre.items()},
               tight_up=tight_up, tight_down=tight_down, allow_log2=float(log2d(allow)), memory_log2_bytes=mem_log2_bytes, preprocessing_incl_allowances_log2=float(log2d(pre_incl)), T_num=T.numerator, T_den=T.denominator, log2_T=float(lg), time_log2=tl,
               attack_units_log2=float(log2d(T - allow)), ops_per_block_cv=float(Fr(online, NG * NB)))
    if show:
        for k, v in out.items(): print('%-22s %s' % (k, v))
    assert (1 - (-mu_act).exp() - Decimal(Ptot.numerator) / Decimal(Ptot.denominator)) >= Decimal(succ.numerator) / Decimal(succ.denominator)
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--base', action='store_true'); ap.add_argument('--q3', type=float, default=-101.5); ap.add_argument('--delta', type=float, default=1.0)
    ap.add_argument('--eps-log2', type=int, default=None); ap.add_argument('--ac', type=int, default=70); ap.add_argument('--as', dest='as_', type=int, default=60)
    ap.add_argument('--dev', type=int, default=60); ap.add_argument('--succ', default='0.39')
    a = ap.parse_args()
    eps = (Fr(1, 1 << 16), Fr(1, 1 << 14), Fr(1, 1 << 7)) if a.eps_log2 is None else Fr(1, 2 ** -a.eps_log2)
    eps2 = Fr(1, 1 << 5) if a.eps_log2 is None else Fr(1)
    ledger(a.q3, Fr(a.delta).limit_denominator(1000), eps, a.ac, a.as_, a.dev, Fr(a.succ), base=a.base, eps2=eps2)
