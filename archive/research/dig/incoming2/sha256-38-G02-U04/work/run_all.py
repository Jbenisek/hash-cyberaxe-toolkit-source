import inspect, math, json, sys, time
import numpy as np
from fractions import Fraction
from decimal import Decimal, getcontext
import a0lean38 as L
import memmodel as MM
getcontext().prec = 80
CAL = MM.CAL
# --- ledger without the K=90 assert (so a subset of classes can be priced)
src = inspect.getsource(L.ledger).replace('assert g == Fraction(92475, 4)', 'pass').replace('def ledger(', 'def ledger2(')
exec(src, L.__dict__)

def s0n(x): return ((x >> 7) | (x << 25)) ^ ((x >> 18) | (x << 14)) ^ (x >> 3)
def pany_sample(classes, n=20_000_000, seed=1):
    rng = np.random.default_rng(seed); A = rng.integers(0, 2**32, size=n, dtype=np.uint64).astype(np.uint32)
    hit = np.zeros(n, dtype=bool)
    D7 = np.uint32(L.D7); T7 = np.uint32(L.T7)
    for c7, b, m in classes:
        w = (np.uint32(c7) - A).astype(np.uint32)
        hit |= ((s0n((w + D7).astype(np.uint32)) - s0n(w)).astype(np.uint32) == T7)
    return hit.mean()

def price(dFB=0, dVisit=0, dVisitMax=None, dW7=0, classes=None, grp=None, pany=None, cal=None):
    """time_log2 exact (log2(N_total/C)) for the ledger with the given extra counted operations (class subset optional)."""
    dFB, dVisit, dW7 = Fraction(dFB), Fraction(dVisit), Fraction(dW7)
    if dVisitMax is not None: dVisitMax = Fraction(dVisitMax)
    saveC, saveG, saveH = L.CLASSES, L.GRP, L.HIT0
    try:
        if classes is not None:
            L.CLASSES, L.GRP = classes, grp
            L.HIT0 = int(round((1 - pany) * 2**32))
            cal = L.calibrate(full=True)
        else: cal = CAL
        rows, info = L.ledger2(cal, show=False)
        K = len(L.CLASSES); p7 = Fraction(287309824, 2**32); khit = K * p7
        vbar = info['vbar'] + dFB + khit * dVisit + K * dW7
        dvm = dVisit if dVisitMax is None else dVisitMax
        class_max = max(7 + 15 * (cal['prog'][h] + 6) + 3840 * (cal['lane_max'][c[2]] + cal['step3b']) for c, h in zip(L.CLASSES, L.GRP)) + dvm
        vmax_f = K * (44 + 2 + 4 + class_max) + cal['fb_scalars'] + cal['planes'] + dFB + K * dW7
        g = info['g']; two = Decimal(2)
        q3 = two ** Decimal('-97.7838'); h3 = 1 - two ** Decimal('-9.5'); eps = Fraction(1, 2**16); succ = Decimal('0.39'); N = 1
        for _ in range(6):
            vb = Decimal(vbar.numerator) / Decimal(vbar.denominator)
            pcap = (Decimal(Fraction(vmax_f).numerator) / Decimal(Fraction(vmax_f).denominator)) / (Decimal(eps.denominator) ** 2 * Decimal(N) * vb) if N > 1 else Decimal(0)
            x = -(Decimal(1) - succ - two ** -60 - pcap).ln()
            N = int((x / (Decimal(g.numerator) / Decimal(g.denominator) * q3 * h3)).to_integral_value(rounding='ROUND_CEILING'))
        VMAX = -((-N * vbar * (1 + eps)).__floor__())
        tot = 0
        for nm, v in rows:
            if nm.startswith('data-dependent'): tot += VMAX
            elif nm.startswith('overshoot'): tot += int(class_max + 1000)
            else: tot += int(v)
        # preprocessing of the subset is in rows already (pre_terms uses L.CLASSES)
        return math.log2(tot) - math.log2(2728), float(vbar), N
    finally:
        L.CLASSES, L.GRP, L.HIT0 = saveC, saveG, saveH

def Sf(T, B): return T + max(0.0, math.log2(B) - 20)
out = {}
parts, B0 = L.memory(CAL)
T0, vb0, N0 = price()
out['base'] = dict(T=T0, B=B0, vbar=vb0, N=N0)
print('base', T0, B0, vb0)
# known-answer for pany sampling
t = time.time(); pa = pany_sample(L.CLASSES, n=2_000_000); print('pany sample (90 classes) %.5f vs ledger %.5f  (%.0fs)' % (pa, 1 - L.HIT0 / 2**32, time.time() - t))
out['pany_check'] = (pa, 1 - L.HIT0 / 2**32)
res = {}
def rec(name, dB, **kw):
    T, vb, N = price(**kw); B = B0 + dB
    res[name] = dict(dB=dB, B=B, T=T, dT=T - T0, S=Sf(T, B), dS=Sf(T, B) - T0, **{k: v for k, v in kw.items() if k in ('dFB', 'dVisit', 'dW7', 'dVisitMax')})
    print('%-34s dB=%+9d B=%9d  T=%.6f dT=%+.6f  S=%.6f dS=%+.6f' % (name, dB, B, T, T - T0, res[name]['S'], res[name]['dS']))
# ------- CTAB
rec('CTAB_pack8_per_word', -(8640 - 960), dW7=2.125, dVisit=3)
rec('CTAB_c7_from_base_64cls', -64 * 32, dFB=64 * 9)
rec('CTAB_unroll_W7', 90 * 52 * 32 - 5 * 32 - 90 * 32, dW7=-3)
# cheapest path of member_test (first test fails) in counted ops
m = L.Mach(); a = 0
e4 = m.and_(m.add(a, L.C4), L.M); w = m.and_(m.sub(L.W8C, e4), L.M); y = m.and_(m.add(w, L.D8), L.M); cm_, cv_, cd_ = L.CELLS[2][8][:3]; t_ = m.and_(w, cm_); m.br()
print('cheapest member_test path ops', m.ops); out['member_cheap_ops'] = m.ops
regenT = math.log2(2**32 * m.ops / vb0)
rec('CTAB_regen_each_FB_lowerbound', -8640, dFB=2**32 * m.ops)
# ------- CODE7
lens = [CAL['prog'][h] for h in L.GRP]; meanlen = Fraction(sum(lens), 90); maxlen = max(lens)
print('mean len', meanlen, 'max', maxlen)
rec("CODE7_resident1_regen_1op", -(318272 - maxlen * 32), dVisit=meanlen, dVisitMax=maxlen)
rate = Fraction(2**32, sum(CAL['prog'].values()))
rec('CODE7_resident1_regen_lump', -(318272 - maxlen * 32), dVisit=meanlen * rate, dVisitMax=maxlen * rate)
# drop one program (its classes) = shard the class set
for gprog in sorted(CAL['prog']):
    keep = [(c, h) for c, h in zip(L.CLASSES, L.GRP) if h != gprog]
    cl = [c for c, h in keep]; gr = [h for c, h in keep]
    pa_s = pany_sample(cl, n=6_000_000, seed=7)
    rec('CODE7_drop_prog%d(%dcls)' % (gprog, 90 - len(cl)), -CAL['prog'][gprog] * 32, classes=cl, grp=gr, pany=pa_s)
# ------- CODEO
rec('CODEO_W7_tree_regen_52', -(1824 - 0), dW7=52)
rec('CODEO_other600_regen_each_FB', -19200, dFB=600)
rec('CODEO_all_regen', -(1824 + 19200), dW7=52, dFB=600)
out['res'] = res
# break-even / penalties at the line
pen = lambda b0, x: math.log2((b0 + x) / 2**20)
out['headroom'] = 2**20 - B0
out['pen_at_line'] = {nm: math.log2(1 + b / 2**20) for nm, b in (('CTAB', 8640), ('CODE7', 318272), ('CODEO', 21024), ('CODE7_prog_max', maxlen * 32))}
out['pen_from_shipped'] = {nm: pen(B0, b) for nm, b in (('CTAB', 8640), ('CODE7', 318272), ('CODEO', 21024))}
json.dump(out, open('results.json', 'w'), indent=1, default=str)
print(json.dumps(out['pen_at_line'], indent=1), out['headroom'])
