"""Assemble the candidate folder pkg_stage/ (claim.json, proof.md, certificates/) and submission-note.md for the single-centre entry from the ledger logs.
Every number in proof.md and claim.json is computed here from: logs/single_<seed>.txt (data-independent stages), logs/calib.txt (levels of the root
isolation), gcd_bounds.h (generated worst-case gcd/division bounds), logs/size.txt (static image), data/collisions.json (certificates).
Section 8 (success probability) is the file section8.md (built from the cloud proof sections and the CERT B certificate; final). PCLAIM is the claimed probability."""
import json, math, os, re, shutil, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
# optional environment (the defaults reproduce the original behaviour exactly; cycle.sh sets them for the cap-6 entry):
#   PKG_OUT     output folder name inside HERE (default pkg_stage)      LOGPREFIX  ledger log prefix in logs/ (default single_)
#   CAP         DEG_CAP of the build (0 = no cap); with a cap the root isolation is charged from degree 9 down (+2 for the cap test) and the heap is the ledger peak
#   SIZE_FILE   output of `size` for the shipped binary (default logs/size.txt)    NOTE_OUT / NUMBERS  names of the note and the numbers file
OUT = os.path.join(HERE, os.environ.get('PKG_OUT', 'pkg_stage'))
CAP = int(os.environ.get('CAP', '0'))
LOGPREFIX = os.environ.get('LOGPREFIX', 'single_')
SIZE_FILE = os.environ.get('SIZE_FILE', os.path.join('logs', 'size.txt'))
NOTE_OUT = os.environ.get('NOTE_OUT', 'submission-note.md')
NUMBERS = os.environ.get('NUMBERS', 'numbers.json')
C = 237
STACK, ALLOC = 65536, 4096
M = 39062
INV_CTL, INVA = 2310, 330
MARGIN = 1.02
PCLAIM = 0.3934
P_CENTRE = '0.39346786834977'
sys.path.insert(0, HERE)
import poseidon_ref as ref


def L(x):
    return '{:,}'.format(int(x))


def ceil5(x):
    return math.ceil(round(x * 100000, 6)) / 100000


def ceil3(x):
    return math.ceil(x * 1000) / 1000


def gcd_bound_cl(da, db):
    S0 = da + db; cap = max(da, db) + 1
    inner = (S0 * S0) // 4; E = S0 + 1
    setup = 5 * (S0 + 2) + 2 + 2 * (S0 + 2) + 9 * (S0 + 2) + 4
    elim = 25 * E + 11 * (S0 + 1)
    pas = E * (INVA + 2 + INV_CTL + 8)
    fin = INVA + 2 + INV_CTL + 8 * cap + 4
    return 12 * inner + elim + pas + setup + fin


def div_bound(la, lb):
    return (la - lb + 1) * (14 + 12 * (lb - 1)) + 7 * la + 2 + INVA + 2 + INV_CTL + 11 * (lb + 1)


def tries(d):
    return 1 if d > 40 else (40 + d - 2) // (d - 1)


# ---- generated bounds
hdr = open(os.path.join(HERE, 'gcd_bounds.h')).read()
LEVELB = {int(a): (int(b), int(c)) for a, b, c in re.findall(r'\{\s*(\d+),\s*(\d+)ULL,\s*(\d+)ULL\s*\}', hdr)}
GCD_BOUND = LEVELB[39062][0]


def lvl(d):
    cands = [x for x in LEVELB if x >= d]
    return LEVELB[min(cands)]


# ---- ledger log: prefer a success run made with verbose=1 (powering breakdown); any run reaching stage D otherwise
logs = sorted(glob.glob(os.path.join(HERE, 'logs', LOGPREFIX + '*.txt')))
texts = {f: open(f).read() for f in logs}
ledger_f = os.environ.get('LEDGER')
if ledger_f:
    ledger_f = os.path.join(HERE, 'logs', ledger_f)
else:
    cand = [f for f, t in texts.items() if 'lean-pow breakdown' in t and 'success=1' in t]
    ledger_f = cand[0] if cand else [f for f, t in texts.items() if 'success=1' in t][0]
logtxt = texts[ledger_f]
print('ledger log', os.path.basename(ledger_f))


def stage(txt, name):
    m = re.search(r'^\s{2}' + re.escape(name) + r'\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+)\s+([\d.]+)s peak=(\d+)', txt, re.M)
    return None if not m else dict(arith=int(m.group(1)), other=int(m.group(2)), total=int(m.group(3)), sec=float(m.group(4)), peak=int(m.group(5)))


names = ['init (twiddle table)', 'line setup', 'random centre', 'B: build g', 'C: S^((p-1)/2) mod g', 'D: gcd(g, S^h - 1) (half-gcd)', 'E: root isolation', 'F: sqrt + map back', 'G: verification (2 reference hashes)']
S_ = {n: stage(logtxt, n) for n in names}
for n in names:
    assert S_[n], n
INIT, SETUP, RAND, BUILD, POW = (S_[n]['total'] for n in names[:5])
GCD_STAGE = S_[names[5]]['total']
gm = re.search(r'gcd degree (\d+), charged (\d+), derived bound (\d+)', logtxt)
GCD_OBS = int(gm.group(2))
assert int(gm.group(3)) == GCD_BOUND, (gm.group(3), GCD_BOUND)
SCAN_ALLOW = 10 * (M + 1)
FINAL_OBS = S_[names[7]]['total'] + S_[names[8]]['total']
FINAL_ALLOW = 400000
ROOT_STAGE = S_[names[6]]['total']
sm = re.search(r'SUMMARY total_all=(\d+)', logtxt)
TYP_ROOT = int(sm.group(1))
TYP_NOROOT = None
for f, t in texts.items():
    if 'roots_degree=0' in t and 'SUMMARY' in t:
        TYP_NOROOT = int(re.search(r'SUMMARY total_all=(\d+)', t).group(1)); break
if TYP_NOROOT is None and CAP:
    TYP_NOROOT = TYP_ROOT - sum(S_[n]['total'] for n in names[6:])   # derived (no no-root attempt is run in cycle.sh): the success-path total minus stages E, F, G
peaks = {n: S_[n]['peak'] for n in names}
bd = re.search(r'newton total=(\d+) arith=(\d+) \| prefix\+scale total=(\d+) \| loop steps=(\d+) total=(\d+) arith=(\d+) per-step total=(\d+) arith=(\d+)', logtxt)
assert bd, 'no powering breakdown in the ledger log (run single with verbose=1)'
NEWTON, PREFIX, STEPS, PER_STEP, PER_STEP_ARITH = L(bd.group(1)), L(bd.group(3)), bd.group(4), L(bd.group(7)), L(bd.group(8))
assert int(STEPS) == 238
ty = {}
for m_ in re.finditer(r'^TYPES', logtxt, re.M): pass
# ---- calibration
cal = open(os.path.join(HERE, os.environ.get('CALIB', os.path.join('logs', 'calib.txt')))).read()
levels = {}
for m_ in re.finditer(r'LEVEL d=(\d+) shift=(\d+) pow=(\d+) shift_abs_peak=(\d+) pow_abs_peak=(\d+)', cal):
    levels[int(m_.group(1))] = tuple(int(m_.group(i)) for i in range(2, 6))

# ---- the level schedule of the worst case
QUAD = 16000


def split_cost(start):
    sched = []
    d = start
    while d >= 3:
        sched.append(d); d //= 2
    rows = []
    total = 0
    tsum = 0
    for d in sched:
        sh, pw, pk1, pk2 = levels[d]
        t = tries(d)
        if d <= 152:
            gb = gcd_bound_cl(d, d - 1)
        else:
            gb = int(math.ceil(MARGIN * lvl(d)[0]))
        if d > 76:
            dv = int(math.ceil(MARGIN * lvl(d)[1]))
        else:
            dv = max(div_bound(d + 1, a + 1) for a in range(d // 2 + 1, d)) if d >= 3 else 0
        per_try = sh + pw + gb + dv + 100
        total += t * per_try
        tsum += t
        rows.append((d, t, sh, pw, gb, dv, t * per_try))
    total += QUAD + 100
    return total, rows, tsum


split_total, rows, tries_sum = split_cost(9 if CAP else M)
DOM_NOTE = ''
if CAP:
    _lv_all = {d_: levels[d_] for d_ in range(3, 10)}
    def _c(d_):
        return _lv_all[d_][0] + _lv_all[d_][1] + gcd_bound_cl(d_, d_ - 1) + max(div_bound(d_ + 1, a_ + 1) for a_ in range(d_ // 2 + 1, d_)) + 100
    _worst = {}
    for d0_ in range(3, CAP + 1):
        tot_, dd_ = tries(d0_) * _c(d0_), d0_ // 2
        while dd_ >= 3:
            tot_ += tries(dd_) * _c(dd_); dd_ //= 2
        _worst[d0_] = tot_ + QUAD + 100
    assert all(_lv_all[d_ + 1][0] >= _lv_all[d_][0] and _lv_all[d_ + 1][1] >= _lv_all[d_][1] for d_ in range(3, 9)), 'calibration not monotone'
    assert split_total >= max(_worst.values()), (split_total, _worst)
    DOM_NOTE = 'shift and pow are nondecreasing over d = 3..9 in the calibration, and the charged total %s is at least the largest reachable total %s (first level %d, then %d)' % (L(split_total), L(max(_worst.values())), max(_worst, key=_worst.get), max(_worst, key=_worst.get) // 2)
worst = INIT + SETUP + RAND + BUILD + POW + GCD_BOUND + SCAN_ALLOW + split_total + FINAL_ALLOW + (2 if CAP else 0)
t_exact = math.log2(worst / C)
time_claim = ceil5(t_exact)
cap_variants = {}
for cap, start in ((6, 9), (8, 9)):
    st_, _, _ = split_cost(start)
    w = INIT + SETUP + RAND + BUILD + POW + GCD_BOUND + SCAN_ALLOW + st_ + FINAL_ALLOW + 2
    cap_variants[cap] = dict(worst=w, time_log2=math.log2(w / C))

# ---- memory
size = open(os.path.join(HERE, SIZE_FILE)).read().split('\n')[1].split()
static = int(size[0]) + int(size[1]) + int(size[2])
_lv = [v for d_, v in levels.items() if (d_ <= 9 or not CAP)]
peak_pow = max(v[3] for v in _lv)
peak_shift = max(v[2] for v in _lv)
# gcd stage of the root isolation at the top level (G kept, S - 1 given away): measured by test_keep at d = 39062 (absolute peak, twiddle table included)
if CAP:
    peak_gcd = 0     # root isolation of degree > 9 never runs under the cap; the gcd of the main attempt is stage D of the ledger
else:
    kt = open(os.path.join(HERE, 'logs', 'test_keep.txt')).read()
    peak_gcd = int(re.search(r'poly_gcd_keep d=39062: .*?absolute peak (\d+) bytes', kt).group(1))
PEAK_MAIN = max(peaks.values())
HEAP = max(PEAK_MAIN, peak_pow, peak_shift, peak_gcd)
mem_bytes = HEAP + static + STACK + ALLOC
mem_log2 = ceil3(math.log2(mem_bytes))
mem_pen = round(max(0, mem_log2 - 20), 3)
score = round(time_claim + mem_pen, 5)

ledger_rows = ['| stage | arith | other | total | data-dependent |', '|---|---:|---:|---:|---|']
def row(label, nm, dd='no'):
    s = S_[nm]; ledger_rows.append('| %s | %s | %s | %s | %s |' % (label, L(s['arith']), L(s['other']), L(s['total']), dd))
row('init: twiddle table (once)', names[0])
row('setup: the line', names[1])
row('A: random centre', names[2])
row('B: 98304 evaluations (units) + inverse NTT 49152 + normalisation', names[3])
row('C: `S^((p-1)/2) mod g` (m = 39062, 238 steps)', names[4])
ledger_rows.append('| D: half-gcd, derived bound for (39062, 39061) plus the degree scan allowance (10 x 39063) | - | - | %s + %s (charged in the run: %s) | yes: bound |' % (L(GCD_BOUND), L(SCAN_ALLOW), L(GCD_STAGE)))
ledger_rows.append('| E: root isolation, worst case over the level schedule (table below), plus the quadratic end | - | - | %s | yes: bound |' % L(split_total))
ledger_rows.append('| F, G: square root, back-map, two reference hashes (success path) | - | - | %s allowance (observed %s) | no |' % (L(FINAL_ALLOW), L(FINAL_OBS)))
tab = ['| d | tries t(d) | shift(d) | pow(d) | gcd bound | div bound | t(d) x (shift + pow + gcd + div + 100) |', '|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
    tab.append('| ' + ' | '.join(L(x) for x in r) + ' |')
tab.append('| quadratic end (d = 2) and level control | | | | | | %s |' % L(QUAD + 100))
tab.append('| total | %d | | | | | %s |' % (tries_sum, L(split_total)))

WORST_FORMULA = 'init + setup + A + B + C + D bound + scan + E bound + final allowance = %s + %s + %s + %s + %s + %s + %s + %s + %s' % (
    L(INIT), L(SETUP), L(RAND), L(BUILD), L(POW), L(GCD_BOUND), L(SCAN_ALLOW), L(split_total), L(FINAL_ALLOW))
LEDGER_PY = '\n'.join([
    'from math import log2, ceil',
    'C = 237',
    'init, setup, rand, build, power = %d, %d, %d, %d, %d' % (INIT, SETUP, RAND, BUILD, POW),
    'gcd_bound, scan, split, final = %d, %d, %d, %d' % (GCD_BOUND, SCAN_ALLOW, split_total, FINAL_ALLOW),
    'N = init + setup + rand + build + power + gcd_bound + scan + split + final',
    "print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))"])

tm = re.search(r'^TYPES add=(\d+) sub=(\d+) mul=(\d+) sqr=(\d+) ld=(\d+) st=(\d+) ctl=(\d+) rnd=(\d+) perm=(\d+)', logtxt, re.M)

SRC_FILES = ['common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'attack.h', 'hgcd.h', 'gcd_bounds.h', 'ntt.c', 'gen_kern.py', 'ntt_kern.h', 'ntt_a3.h', 'poly.c', 'lean.c', 'line.c', 'split.c', 'hgcd.c', 'single.c', 'test_hgcd.c', 'test_split.c', 'test_keep.c', 'calib.c', 'gcdbound.c', 'certb_verify.py']


def appendix():
    out = []
    for fn in SRC_FILES:
        body = open(os.path.join(HERE, fn)).read().rstrip('\n')
        out.append('### ' + fn + '\n\n```' + ('python' if fn.endswith('.py') else 'c') + '\n' + body + '\n```\n')
    return '\n'.join(out)


# ---- certificates
colls = json.load(open(os.path.join(HERE, 'data', os.environ.get('COLLS', 'collisions.json'))))
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(OUT, 'certificates'))
man = []
seen = set()
k = 0
for v in colls:
    key = (v['nk1'], v['rho1'], v['nk2'], v['rho2'])
    if key in seen: continue
    nk1, rho1, nk2, rho2 = key
    ma = nk1.to_bytes(32, 'little') + rho1.to_bytes(32, 'little'); mb = nk2.to_bytes(32, 'little') + rho2.to_bytes(32, 'little')
    da, db = ref.digest_bytes(ma, 1), ref.digest_bytes(mb, 1)
    assert da == db and ma != mb
    seen.add(key); k += 1
    open(os.path.join(OUT, 'certificates', 'c%d-a.bin' % k), 'wb').write(ma)
    open(os.path.join(OUT, 'certificates', 'c%d-b.bin' % k), 'wb').write(mb)
    man.append({"id": "collision-%d" % k, "type": "hash-collision-witness-v2", "message_a": "certificates/c%d-a.bin" % k, "message_b": "certificates/c%d-b.bin" % k,
                "expected_digest": da.hex(), "target_profile": "poseidon-orchard-r1-prefix-v1"})
N_CERT = k
json.dump({"schema_version": 2, "certificates": man}, open(os.path.join(OUT, 'certificates', 'manifest.json'), 'w', newline='\n'), indent=1)

S8VALS = json.load(open(os.path.join(HERE, 'section8_vals.json')))
S8 = open(os.path.join(HERE, 'section8.md')).read()
for k_, v_ in S8VALS.items():
    S8 = S8.replace('@@%s@@' % k_, v_)
repl = {
    'SECTION8': S8,
    'TIME_LOG2': '%.5f' % time_claim, 'TIME_LOG2_EXACT': '%.5f' % t_exact,
    'MEM_LOG2': '%.3f' % mem_log2, 'MEM_BYTES': L(mem_bytes), 'MEM_PEN': '%.3f' % mem_pen, 'SCORE': '%.5f' % score,
    'PCLAIM': repr(PCLAIM), 'P_CENTRE': P_CENTRE, 'LINE': '0', 'N_CERT': str(N_CERT), 'TRIES_SUM': 'for the worst schedule %d tries' % tries_sum,
    'GCD_BOUND': L(GCD_BOUND), 'GCD_OBS': L(GCD_OBS), 'GCD_RATIO': '%.3f' % (GCD_OBS / GCD_BOUND), 'QUAD': L(QUAD),
    'DOM_NOTE': DOM_NOTE, 'VERIFY_SHORT': S8VALS['VERIFY_SHORT'],
    'LEDGER_TABLE': '\n'.join(ledger_rows) + '\n\nWorst case of the root isolation (stage E) over the level schedule of section 4.1 (starting degree 39062):\n\n' + '\n'.join(tab),
    'WORST_FORMULA': WORST_FORMULA, 'WORST_TOTAL': L(worst), 'WORST_UNITS': '{:,.1f}'.format(worst / C),
    'TYP_NOROOT': L(TYP_NOROOT) if TYP_NOROOT else 'n/a', 'TYP_ROOT': L(TYP_ROOT), 'LEDGER_PY': LEDGER_PY,
    'T_ADD': L(tm.group(1)), 'T_SUB': L(tm.group(2)), 'T_MUL': L(tm.group(3)), 'T_SQR': L(tm.group(4)), 'T_LD': L(tm.group(5)), 'T_ST': L(tm.group(6)), 'T_CTL': L(tm.group(7)), 'T_PERM': L(tm.group(9)),
    'CAP': str(CAP), 'NEWTON': NEWTON, 'PREFIX': PREFIX, 'PER_STEP': PER_STEP, 'PER_STEP_ARITH': PER_STEP_ARITH, 'POW_ARITH': L(S_[names[4]]['arith']),
    'STAGE_PEAKS': '; '.join('%s %s' % (n.split(':')[0] if ':' in n else n, L(peaks[n])) for n in names),
    'PEAK_SHIFT': L(peak_shift), 'PEAK_POW': L(peak_pow), 'PEAK_GCD': ('not applicable under the cap' if CAP else L(peak_gcd)), 'HEAP_PEAK': L(HEAP),
    'STATIC_DESC': 'text %s + data %s + bss %s = %s bytes' % (L(int(size[0])), L(int(size[1])), L(int(size[2])), L(static)),
    'FILE_ORDER': ', '.join('`%s`' % f for f in SRC_FILES), 'APPENDIX': appendix(),
}
t = open(os.path.join(HERE, 'proof_template.md' if CAP else 'proof_template_nocap.md')).read()
for key, v in repl.items():
    t = t.replace('@@%s@@' % key, v)
left = re.findall(r'@@[A-Z0-9_]+@@', t)
assert not left, left
bad = [ch for ch in t if ord(ch) >= 128]
assert not bad, bad[:5]
open(os.path.join(OUT, 'proof.md'), 'w', newline='\n').write(t)
lines = t.split('\n')


def ln(prefix):
    for i, l in enumerate(lines, 1):
        if l.startswith(prefix):
            return i
    raise KeyError(prefix)


s4, s6, s7, s8 = ln('## 4.'), ln('## 6.'), ln('## 7.'), ln('## 8.')
claim = {
    "schema_version": 3, "submission_state": "ready", "target_profile": "poseidon-orchard-r1-prefix-v1", "attack_class": "ordinary-collision", "rounds": 1,
    "claim": {"time_log2": time_claim, "time_unit": "target-compressions", "memory_log2_bytes": mem_log2,
              "preprocessing_log2": ceil3(math.log2(INIT / C)), "success_probability": PCLAIM, "nonuniform_advice_log2_bytes": 0},
    "restrictions": [
        "Applies to the selected target poseidon-orchard-r1-prefix-v1 only (one partial round plus the eight fixed full rounds); the construction uses the first two full rounds being skippable on a line and gives no claim for other round counts.",
        "One attempt of the program (one random centre, DEG_CAP = 6); the claimed success probability 0.3934 is below the lower bound 0.3934647661 proved in proof.md section 8 (per-centre bound 0.3934678683, minus the cap-6 halt loss 3.1e-6, minus the root-isolation failure 2^-36); independent uniform random words are the model primitive (ideal randomness, proof.md D18)."],
    "baseline_improved": "poseidon-orchard-r1-nominal-v2",
    "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
    "heuristics": [
        {"id": "H1-charging-rules", "role": "supporting",
         "statement": "The counts of proof.md sections 6 and 7 describe the executed program of proof.md section 10 under the stated rules: 1 per field operation, 1 per element load or store plus 1 address operation, 3 per loop iteration plus 2 per loop exit, 1 per other executed index or control operation, 237 per reduced permutation evaluation, and a register file of 18 words of 256 bits per transform block (16 data words plus two working words: the twiddle operand and the butterfly temporary) as the only register assumption.",
         "scope": "All stages of the program of proof.md section 4 at the target dimensions (m = 39062 for the main powering, N = 98304 and N' = 49152 in its transforms, 98304 evaluations of the line).",
         "extrapolation": "None for the data-independent stages (they are executed totals). The data-dependent stages (half-gcd, root isolation) are charged at derived bounds that the program asserts against its own counters at every execution.",
         "evidence_ids": ["proof:%d-%d" % (s6, s7 - 1), "proof:%d-%d" % (s7, s8 - 1)],
         "limitations": "The counts are produced by the instrumentation written into the source; the source is part of the proof text and was not run by the organizer. Word-level costs outside the stated rules (cache, bandwidth) are not part of the model."}]}
json.dump(claim, open(os.path.join(OUT, 'claim.json'), 'w', newline='\n'), indent=1)
for h in claim['heuristics']:
    for kk in ('statement', 'scope', 'extrapolation', 'limitations'):
        assert len(h[kk]) <= 4096, (h['id'], kk)
for r in claim['restrictions']:
    assert len(r) <= 1024
res = dict(time=time_claim, time_exact=t_exact, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, worst=worst, units=worst / C, split=split_total, heap=HEAP, n_cert=N_CERT,
           gcd_bound=GCD_BOUND, gcd_obs=GCD_OBS, typ_root=TYP_ROOT, typ_noroot=TYP_NOROOT, one_centre_typical_log2=math.log2(TYP_ROOT / C), cap_variants=cap_variants)
print(json.dumps(res, indent=1))
os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
json.dump(res, open(os.path.join(HERE, 'data', NUMBERS), 'w'))
exec(open(os.path.join(HERE, "note_tail.py")).read())
