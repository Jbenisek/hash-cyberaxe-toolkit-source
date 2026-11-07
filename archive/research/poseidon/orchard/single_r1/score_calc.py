"""Score of the single-centre entry from a ledger log, calib levels and a generated gcd bound header (same formulas as build_package.py, without writing any package).
usage: score_calc.py LEDGER_LOG GCD_BOUNDS_H [CALIB_TXT] [MEM_CAP_HEAP] [MEM_NOCAP_HEAP]"""
import math, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
C = 237; STACK, ALLOC = 65536, 4096; M = 39062; INV_CTL, INVA = 2310, 330; MARGIN = 1.02
STATIC = 102406
log = open(sys.argv[1]).read()
hdr = open(sys.argv[2]).read()
calib = open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'logs', 'calib.txt')).read()
LEVELB = {int(a): (int(b), int(c)) for a, b, c in re.findall(r'\{\s*(\d+),\s*(\d+)ULL,\s*(\d+)ULL\s*\}', hdr)}
GCD_BOUND = LEVELB[39062][0]
def lvl(d): return LEVELB[min(x for x in LEVELB if x >= d)]
def L(x): return '{:,}'.format(int(x))
def gcd_bound_cl(da, db):
    S0 = da + db; cap = max(da, db) + 1
    inner = (S0 * S0) // 4; E = S0 + 1
    setup = 5 * (S0 + 2) + 2 + 2 * (S0 + 2) + 9 * (S0 + 2) + 4
    elim = 25 * E + 11 * (S0 + 1); pas = E * (INVA + 2 + INV_CTL + 8)
    fin = INVA + 2 + INV_CTL + 8 * cap + 4
    return 12 * inner + elim + pas + setup + fin
def div_bound(la, lb): return (la - lb + 1) * (14 + 12 * (lb - 1)) + 7 * la + 2 + INVA + 2 + INV_CTL + 11 * (lb + 1)
def tries(d): return 1 if d > 40 else (40 + d - 2) // (d - 1)
def stage(name):
    m = re.search(r'^\s{2}' + re.escape(name) + r'\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+)\s+([\d.]+)s peak=(\d+)', log, re.M)
    return dict(total=int(m.group(3)), peak=int(m.group(5)), arith=int(m.group(1)))
names = ['init (twiddle table)', 'line setup', 'random centre', 'B: build g', 'C: S^((p-1)/2) mod g', 'D: gcd(g, S^h - 1) (half-gcd)', 'E: root isolation', 'F: sqrt + map back', 'G: verification (2 reference hashes)']
S = {n: stage(n) for n in names}
INIT, SETUP, RAND, BUILD, POW = (S[n]['total'] for n in names[:5])
gm = re.search(r'gcd degree (\d+), charged (\d+), derived bound (\d+)', log); GCD_OBS = int(gm.group(2))
SCAN = 10 * (M + 1); FINAL = 400000
levels = {}
for m_ in re.finditer(r'LEVEL d=(\d+) shift=(\d+) pow=(\d+) shift_abs_peak=(\d+) pow_abs_peak=(\d+)', calib):
    levels[int(m_.group(1))] = tuple(int(m_.group(i)) for i in range(2, 6))
def split_cost(start):
    d = start; total = 0
    while d >= 3:
        sh, pw, pk1, pk2 = levels[d]; t = tries(d)
        gb = gcd_bound_cl(d, d - 1) if d <= 152 else int(math.ceil(MARGIN * lvl(d)[0]))
        if d > 76: dv = int(math.ceil(MARGIN * lvl(d)[1]))
        else: dv = max(div_bound(d + 1, a + 1) for a in range(d // 2 + 1, d)) if d >= 3 else 0
        total += t * (int(math.ceil(MARGIN * (sh + pw))) + gb + dv + 100); d //= 2
    return total + 16000 + 100
base = INIT + SETUP + RAND + BUILD + POW + GCD_BOUND + SCAN + FINAL
res = {}
for name, start in (('cap6', 9), ('cap8', 9), ('nocap', M)):
    w = base + split_cost(start) + (2 if name != 'nocap' else 0)
    res[name] = w
PEAK_MAIN = max(S[n]['peak'] for n in names)
peak_pow = max(v[3] for v in levels.values()); peak_shift = max(v[2] for v in levels.values())
peak_gcd = int(sys.argv[5]) if len(sys.argv) > 5 else 10353984   # test_keep absolute peak at d = 39062 (unchanged unless the memory changed)
heap_nocap = max(PEAK_MAIN, peak_pow, peak_shift, peak_gcd)
heap_cap = int(sys.argv[4]) if len(sys.argv) > 4 else max(PEAK_MAIN, 0)
print('stages: init %s setup %s rand %s build %s power %s gcd(run) %s ; gcd bound %s ; typical power arith %s' % (L(INIT), L(SETUP), L(RAND), L(BUILD), L(POW), L(GCD_OBS), L(GCD_BOUND), L(S[names[4]]['arith'])))
for name, w in res.items():
    heap = heap_nocap if name == 'nocap' else heap_cap
    mem = heap + STATIC + STACK + ALLOC
    t = math.log2(w / C); pen = math.log2(mem) - 20
    print('%-6s worst=%s time_log2=%.3f mem=%s (log2 %.3f) score=%.3f' % (name, L(w), t, L(mem), math.log2(mem), t + pen))
