#!/usr/bin/env python3
# g02_mem.py - G02 memory axis for the filed r37 table line (pkgR37c xtab.py ledger).  Own code; reads xtab.py/lowm.py as modules of OUR packages.
# Step 1 reproduce time_log2 / T_num/T_den / byte total.  Step 2 D126 shard model (known answer k=5).  Step 3 reject-early shard model, R16T and ANC variants.

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, math, importlib.util, json
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
BASE = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch')
def load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); sys.modules[n] = m; s.loader.exec_module(m); return m
x = load('xtab', BASE + r'\pkgR37c\pkg\sha256-r37\experiments\xtab.py')
l = load('lowm', BASE + r'\pkgR37M3\pkg\sha256-r37\experiments\lowm.py')

# ---------- bytes (exact, proof.md Section 14 of the filed line) ----------
T0_B = (1 << 32) * 8
REC_N = 15130951680; REC_MAX = 73024
REC_B = REC_N * REC_MAX
R16T_B = (1 << 34) * 32
ANC_B = 1 << 33            # the proof's bound "below 2^33"
CORE = T0_B + REC_B + R16T_B
BOUND = CORE + ANC_B

def mem_bound(B, r16=R16T_B, anc=ANC_B):
    return -(-T0_B // B) + -(-REC_B // B) + r16 + anc
def Sscore(t, m): return t + max(0.0, math.log2(m) - 20)

# ---------- the ledger with parameters (copy of xtab.ledger arithmetic) ----------
C = 2644
def ledger_param(B=1, mode='d126', scan_lane=None, probe_delta_group=Fr(0), pre_div=True, q3_log2=None, test_ops=3):
    SL = x.SCAN_LANE if scan_lane is None else scan_lane
    q3_log2 = x.Q3_LOG2 if q3_log2 is None else q3_log2
    p7, p6, r16 = Fr(68157440, 1 << 32), Fr(287309824, 1 << 32), Fr(1052672, 1 << 32)
    st = x.load_stats(); nvar = sum(c[3] for c in x.CLASSES); g = nvar * p7 * p6
    chunk256 = x.chunk_fixed_ops(256)
    GPAIR = x.LANE_UB[0]
    safety = x.STAT_SAFETY
    cls_cost = []; cls_worst = []; groups = Fr(0)
    for ci, (c7, base, mask, n) in enumerate(x.CLASSES):
        n_, fb, bt, gr, pd = st[ci]
        fb, bt, gr = fb * safety, bt * safety, gr * safety
        groups += p7 * p6 * gr
        lanes = p6 * fb * (SL + 1 + x.SEG_OVH + x.LANE_UB[1])
        cls_cost.append(x.CLASS_OVH + (x.W6_OPS - 1) * bt + fb / 8 + Fr(23, 8) + lanes + p6 * gr * (x.GROUP_OPS + probe_delta_group))
        nb = (n + 255) // 256
        cls_worst.append(x.CLASS_OVH + nb * (x.W6_OPS + 1 + chunk256) + n * (SL + 1 + x.SEG_OVH) + n * (x.GROUP_OPS + probe_delta_group))
    fixed = x.FBFIX
    c3b_pair = 201 + 23 + 1 + x.RARE_LOOKUP; c3b_row = x.ROWCOMP + x.ROWCHECK + 1; c3b_l = 2 + 6 + 2 * c3b_row
    setup = x.PXUB * (2 + x.ZPLANE_OPS + 1 + x.CVPRE_OPS)
    good_part = g * GPAIR
    rare = g * r16 * (c3b_pair + c3b_l + 19 * Fr(1, 512) * c3b_row)
    vbar = setup + p7 * sum(cls_cost) + good_part + rare
    fl = math.floor(q3_log2); q3ex = Fr(2) ** fl * Fr(math.floor(2 ** (q3_log2 - fl) * 2 ** 40), 2 ** 40)
    vmax_fb = sum(cls_worst) + nvar * (x.LANE_UB[0] + x.LANE_UB[1] + 3 + c3b_pair + 32 * (c3b_l + 19 * c3b_row)) + 200 + 2 * x.ZPLANE_OPS
    getcontext().prec = 60
    def mu_req(pcap):
        xx = Decimal('0.61') - Decimal(pcap.numerator) / Decimal(pcap.denominator) - Decimal(2) ** -60
        d = Decimal(1) - (Decimal(-10.4) * Decimal(2).ln()).exp()
        mu = -xx.ln() / d
        return Fr(int(math.floor(mu * 10 ** 8)) + 1, 10 ** 8)
    slack = x.SLACK
    # nfb: matched-equivalent first blocks.  d126: nfb_total = B*nfb' and pcap uses the total; reject: pcap uses matched count (nfb)
    pcap = Fr(1, 1 << 24)
    for _ in range(6):
        XREQ = mu_req(pcap)
        nfb = int(-(-XREQ // (g * 32 * q3ex)))                          # matched-equivalent (B=1 value) ; d126 below rescales
        if mode == 'd126':
            nfbT = int(-(-XREQ // (g * 32 * q3ex / B)))                 # tries, each success prob 1/B of the original
            pcap = Fr(vmax_fb) / (slack * slack * nfbT * vbar)
        else:
            pcap = Fr(vmax_fb) / (slack * slack * nfb * vbar)
    XREQ = mu_req(pcap)
    pre_items = list(x.PRE_ITEMS)
    if pre_div:
        for i in range(3): pre_items[i] = -(-pre_items[i] // B)
    PRE = sum(pre_items)
    if mode == 'd126':
        nfbT = int(-(-XREQ // (g * 32 * q3ex / B)))
        VMAX = math.ceil((1 + slack) * nfbT * vbar)
        T = Fr(2 ** 60 + 2 ** 50 + 2 ** 40) + nfbT + Fr(nfbT * fixed + VMAX + math.ceil(vmax_fb) + PRE + 1600, C) + 6
        N = nfbT
    else:
        nfb = int(-(-XREQ // (g * 32 * q3ex)))
        N = nfb * B
        VMAX = math.ceil((1 + slack) * nfb * vbar)
        T = (Fr(2 ** 60 + 2 ** 50 + 2 ** 40) + N + Fr(N * (test_ops if B > 1 else 0) + nfb * fixed + VMAX + math.ceil(vmax_fb) + PRE + 1600, C) + 6)
    return dict(T=T, tl=math.log2(T), N=N, vbar=float(vbar), groups_per_fb=float(groups), nfb=N, PRE=PRE, vmax_fb=float(vmax_fb), pcap=float(pcap))

if __name__ == '__main__':
    out = {}
    # step 1: reproduce
    r = ledger_param(1)
    print('B=1: T = %d/%d  time_log2 %.6f  (xtab.ledger: 2137189670580414105336/661  61.4877)' % (r['T'].numerator, r['T'].denominator, r['tl']), 'nfb', r['N'], 'vbar', r['vbar'])
    print('core bytes', CORE, 'bound', BOUND, 'log2 bound', math.log2(BOUND), 'D126: 1105515320967168', BOUND == 1105515320967168)
    # step 2: D126 k=5 known answer
    r5 = ledger_param(32, 'd126')
    m5 = mem_bound(32)
    print('D126 k=5: T=%d/%d nfb %d tl %.9f mem %d S %.9f  (D126: 11480695164613822619, 65.87515422098924, 35088251224064, 90.87120750106125)' % (r5['T'].numerator, r5['T'].denominator, r5['N'], r5['tl'], m5, Sscore(r5['tl'], m5)))
