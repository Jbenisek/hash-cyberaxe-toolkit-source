import pickle, math, json, inspect, re
from fractions import Fraction
import a0lean38 as A
cal = pickle.load(open('cal.pkl','rb'))
src = inspect.getsource(A.ledger)
# hooks: W7X (loop add-on per test), W7OVR (replace per-test mean), CLSX(ci) extra ops per passing class, PREX extra preprocessing, and subset of classes via idx
src = src.replace("def ledger(cal=None,", "def ledger2(idx, W7X=4, W7MEAN=None, CLSX=lambda ci:0, PREX=0, cal=None,")
src = src.replace("K = len(CLASSES); g = K * 3840 * p7; assert g == Fraction(92475, 4)", "K = len(idx); g = K * 3840 * p7")
src = src.replace("w7 = (sum(c * p for (c, ok), p in cal['w7'].items()) + 4) * K", "w7 = ((sum(c * p for (c, ok), p in cal['w7'].items()) if W7MEAN is None else W7MEAN) + W7X) * K")
src = src.replace("cls = sum(p7 * (7 + 15 * (cal['prog'][h] + 6)) for h in GRP)", "cls = sum(p7 * (7 + CLSX(i) + 15 * (cal['prog'][GRP[i]] + 6)) for i in idx)")
src = src.replace("for c in CLASSES)\n    r16", "for c in [A.CLASSES[i] for i in idx])\n    r16")
src = src.replace("for c, h in zip(CLASSES, GRP))", "for c, h, ci in [(A.CLASSES[i], GRP[i], i) for i in idx])")
src = src.replace("class_max = max(7 + 15", "class_max = max(7 + CLSX(ci) + 15")
src = src.replace("PRE = sum(v for _, v in pre_terms())", "PRE = sum(v for _, v in pre_terms()) + PREX")
src = src.replace("khit = K * p7", "khit = K * p7")
src = src.replace("K * (44 + 2 + 4 + class_max)", "K * (44 + 2 + 4 + class_max)")
src = src.replace("print('N_FB", "if 0: print('N_FB")
assert "idx" in src
GRP = A.GRP
ns = dict(A.__dict__); ns["A"]=A; exec(src, ns); ledger2 = ns['ledger2']
ALL = list(range(90))
def T(idx=ALL, **kw):
    rows, info = ledger2(idx, cal=cal, show=False, **kw)
    N = sum(int(v) for _, v in rows)
    return math.log2(N/2728), info
def bytes_base():
    return A.memory(cal)[1]
if __name__ == '__main__':
    t0, i0 = T(); print('T0', t0, 'B', bytes_base(), 'vbar', float(i0['vbar']), 'pany', float(i0['pany']))
