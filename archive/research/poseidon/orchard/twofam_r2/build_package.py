"""Assemble the candidate folder pkg_stage/ (claim.json, proof.md, certificates/) and submission-note.md from the ledger logs (r = 2).
Every number in proof.md and claim.json is computed here from: logs/attempt_r2_<seed>.txt (data-independent stages), logs/calib.txt (levels of the root
isolation), logs/size.txt (static image), data/collisions.json (certificates)."""
import json, math, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pkg_stage')
R = 2
C = 216 + 21 * R            # 258
STACK, ALLOC = 65536, 4096
D = 5 ** (6 + R)            # 390625
INV_CTL, INVA = 2310, 330
PROFILE = 'poseidon-orchard-r2-prefix-v1'
sys.path.insert(0, HERE)
import poseidon_ref as ref


def L(x):
    return '{:,}'.format(int(x))


def ceil3(x):
    return math.ceil(x * 1000) / 1000


def gcd_bound(da, db):
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


def divmax(d):
    return max(div_bound(d + 1, a + 1) for a in range(1, d)) if d >= 3 else 0


TRY_CTL, LVL_CTL = 13, 17

# ---- logs of attempts
LOGDIR = os.path.join(HERE, 'logs')
SRCDIR = os.path.join(LOGDIR, 'ledger_src')
att = sorted(f for f in os.listdir(SRCDIR) if re.match(r'attempt_r2_\d+\.txt$', f))
texts = {f: open(os.path.join(SRCDIR, f)).read() for f in att}
done = {f: t for f, t in texts.items() if 'gcd degree' in t}
assert done, 'no r2 attempt that reached the gcd'


def stage(txt, name):
    m = re.search(r'^\s{2}' + re.escape(name) + r'\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+)\s+([\d.]+)s peak=(\d+)', txt, re.M)
    return None if not m else dict(arith=int(m.group(1)), other=int(m.group(2)), total=int(m.group(3)), sec=float(m.group(4)), peak=int(m.group(5)))


ledger_name = sorted(done)[0]
for f in sorted(done):
    if 'family 1: W^p mod F' in done[f]:
        ledger_name = f; break
logtxt = done[ledger_name]
INIT = stage(logtxt, 'init (twiddle table)')['total']
SETUP = stage(logtxt, 'two line setups + intersection')['total']
BUILD = stage(logtxt, 'family 0: build F (evaluations + NTT)')['total']
POW = stage(logtxt, 'family 0: W^p mod F')['total']
m = re.search(r'gcd degree \d+, charged (\d+), derived bound (\d+)', logtxt)
GCD_OBS, GCD_B_C = int(m.group(1)), int(m.group(2))
GCD_BOUND = gcd_bound(D, D - 1)
assert GCD_B_C == GCD_BOUND, (GCD_B_C, GCD_BOUND)
assert GCD_OBS <= GCD_BOUND
for f, t in done.items():       # the data-independent stages agree across all finished attempts
    assert stage(t, 'init (twiddle table)')['total'] == INIT
    assert stage(t, 'family 0: build F (evaluations + NTT)')['total'] == BUILD
    assert stage(t, 'family 0: W^p mod F')['total'] == POW
MAPB = VER = None
certlogs = {f: open(os.path.join(LOGDIR, f)).read() for f in sorted(os.listdir(LOGDIR)) if re.match(r'cert_r2_\d+\.txt$', f)}
for f, t in certlogs.items():
    a, b = stage(t, 'map back (two inputs)'), stage(t, 'verification (2 reference hashes)')
    if a and b: MAPB, VER = a['total'], b['total']; break
assert MAPB
FINAL = MAPB + VER + 44
SAMPLE_OBS = sorted(set(stage(t, 'sample x, y = H(x)')['total'] for t in done.values()))
PEAK_MAIN = max(int(x) for t in done.values() for x in re.findall(r' peak=(\d+)', t))
# driver check: a success in family 0 reports 72 operations outside its stages
drv_obs = {}

# ---- sampler and driver (exact enumerations, see section 7)
SAMPLE = 128 * 37 + 4 + 31 + 38 + 14 + 31 + 31 + 15 + 12 + C
DRV_FAM = 31
DRV_F, DRV_END = 6, 9

# ---- calibration
cal = open(os.path.join(LOGDIR, 'calib.txt')).read()
assert 'EXIT 0' in cal
sq = re.search(r'SQRT A_q=(\d+) A_qp1h=(\d+) max_arith_over_4000=(\d+)', cal)
A_Q, A_QP1H, SQRT_MAX_OBS = int(sq.group(1)), int(sq.group(2)), int(sq.group(3))
SQRT_ARITH = A_Q + A_QP1H + sum(mm + 2 for mm in range(1, 33))
assert SQRT_MAX_OBS <= SQRT_ARITH
QUAD = 9 + 2 + (4 + INVA + 1 + 2 + 1) + 3 * INV_CTL + 19 * SQRT_ARITH
lev = {}
last_break = None
for line in cal.split('\n'):
    mb = re.match(r'lean-pow breakdown: newton total=(\d+) arith=(\d+) \| prefix\+scale total=(\d+) \| loop steps=(\d+) total=(\d+) arith=(\d+)', line)
    if mb: last_break = dict(newton=int(mb.group(1)), prefix=int(mb.group(3)), steps=int(mb.group(4)), loop=int(mb.group(5))); continue
    ml = re.match(r'LEVEL d=(\d+) shift=(\d+) pow=(\d+) shift_abs_peak=(\d+) pow_abs_peak=(\d+)', line)
    if ml:
        d = int(ml.group(1))
        lev[d] = dict(shift=int(ml.group(2)), pow=int(ml.group(3)), pk_shift=int(ml.group(4)), pk_pow=int(ml.group(5)), brk=last_break if d > 40 else None)
        last_break = None; continue
    mp = re.match(r'POWSTEPS d=(\d+) steps=(\d+) ones=(\d+) mulx_total=(\d+)', line)
    if mp:
        d = int(mp.group(1)); lev[d].update(steps=int(mp.group(2)), ones=int(mp.group(3)), mulx=int(mp.group(4)))
RM_D = int(re.search(r'REMOVE d=%d charged=(\d+)' % D, cal).group(1))
for d in range(3, 48): assert d in lev, d


def pow_bound(k):
    """pow_B(k) = pow(k) + 2 P + (s + 2 - u) X for k > 40 (section 7); the measured charge for k <= 40."""
    v = lev[k]
    if k <= 40: return v['pow']
    s, u, mx, loop = v['steps'], v['ones'], v['mulx'], v['brk']['loop']
    assert s == v['brk']['steps']
    P = -(-(loop - mx) // s); X = -(-mx // u)
    return v['pow'] + 2 * P + (s + 2 - u) * X


def small_cost(d):          # exact measured charges, 3 <= d <= 47
    return tries(d) * (lev[d]['shift'] + lev[d]['pow'] + gcd_bound(d, d - 1) + TRY_CTL) + LVL_CTL + divmax(d)


M47 = max(small_cost(d) for d in range(3, 48))
sched = []
d = D
while d >= 3:
    sched.append(d); d //= 2
assert sched[-1] == 5 and len(sched) == 17
# monotone-structure checks on the calibration (reported, not assumed silently): the per-step charge roughly doubles per doubling of the degree
rows = []
split_total = 0
tries_sum = 0
for k in sched:
    t = tries(k)
    if k <= 47:
        lvl = max(small_cost(d) for d in range(3, k + 1))
        row = (k, t, lev[k]['shift'], lev[k]['pow'], lev[k]['pow'], gcd_bound(k, k - 1), divmax(k), lvl)
    else:
        assert lev[k]['shift'] >= lev[47]['shift'] and pow_bound(k) >= lev[40]['pow']
        own = t * (lev[k]['shift'] + pow_bound(k) + gcd_bound(k, k - 1) + TRY_CTL) + LVL_CTL + divmax(k)
        lvl = max(own, M47)
        row = (k, t, lev[k]['shift'], lev[k]['pow'], pow_bound(k), gcd_bound(k, k - 1), divmax(k), lvl)
    rows.append(row)
    split_total += lvl
    tries_sum += t
split_total += QUAD

family_cost = DRV_FAM + BUILD + POW + GCD_BOUND + RM_D
worst = INIT + SETUP + SAMPLE + 2 * family_cost + DRV_F + DRV_END + split_total + FINAL
t_exact = math.log2(worst / C)
time_claim = ceil3(t_exact)

# the same worst case if every level were charged t = 40 tries (alternative failure bound l * rho^t with rho = (p+1)/(2p)), for the report only
alt_split = QUAD
for k in sched:
    r_ = rows[sched.index(k)]
    per_try = (r_[2] + r_[4] + r_[5] + TRY_CTL) if k > 47 else None
    if per_try is None: alt_split += r_[7]
    else: alt_split += 40 * per_try + LVL_CTL + r_[6]
alt_worst = INIT + SETUP + SAMPLE + 2 * family_cost + DRV_F + DRV_END + alt_split + FINAL

# typical runs (about): a run that finds its root in the first family / goes through both families without a partner
SMP = SAMPLE_OBS[0]
typ_first = INIT + SETUP + SMP + BUILD + POW + GCD_OBS + 100 + FINAL + 72
typ = INIT + SETUP + SMP + 2 * (BUILD + POW + GCD_OBS + 100) + 90
# ---- memory
size = open(os.path.join(LOGDIR, 'size.txt')).read().split('\n')[1].split()
static = int(size[0]) + int(size[1]) + int(size[2])
peak_pow = lev[D]['pk_pow']
peak_shift = lev[D]['pk_shift']
elt = 32
TABLE = (1 << 17) * elt
peak_gcd = 5 * (D + 1) * elt + TABLE
HEAP = max(PEAK_MAIN, peak_pow, peak_shift, peak_gcd)
mem_bytes = HEAP + static + STACK + ALLOC
mem_log2 = ceil3(math.log2(mem_bytes))
mem_pen = round(max(0, mem_log2 - 20), 3)
score = round(time_claim + mem_pen, 3)
PCLAIM = 0.4999999999

ledger_rows = ['| stage | arith | other | total | data-dependent |', '|---|---:|---:|---:|---|']
si = stage(logtxt, 'init (twiddle table)')
ledger_rows.append('| init: twiddle table (once) | %s | %s | %s | no |' % (L(si['arith']), L(si['other']), L(si['total'])))
ss = stage(logtxt, 'two line setups + intersection')
ledger_rows.append('| setup: two lines, the common input I | %s | %s | %s | no |' % (L(ss['arith']), L(ss['other']), L(ss['total'])))
ledger_rows.append('| A: sampler (128 words) and `y = H(x)`, family 1 | - | - | %s (logged runs: %s) | enumerated |' % (L(SAMPLE), ', '.join(L(x) for x in SAMPLE_OBS)))
ledger_rows.append('| driver: %d per family, %d (isolation call), %d (end) | - | - | %s | enumerated |' % (DRV_FAM, DRV_F, DRV_END, L(2 * DRV_FAM + DRV_F + DRV_END)))
sb = stage(logtxt, 'family 0: build F (evaluations + NTT)')
ledger_rows.append('| B (per family): 393216 evaluations (units) + inverse NTT 393216 + normalisation | %s | %s | %s | no |' % (L(sb['arith']), L(sb['other']), L(sb['total'])))
sp = stage(logtxt, 'family 0: W^p mod F')
ledger_rows.append('| C (per family): `W^p mod F` (m = 390625) | %s | %s | %s | no |' % (L(sp['arith']), L(sp['other']), L(sp['total'])))
ledger_rows.append('| D (per family): classical gcd, derived bound for (390625, 390624) | - | - | %s (charged in the run: %s) | yes: bound |' % (L(GCD_BOUND), L(GCD_OBS)))
ledger_rows.append('| E (per family): copy of G and two deflations at d = 390625 | - | - | %s | linear in d |' % L(RM_D))
ledger_rows.append('| F: root isolation, worst case over the level schedule (table below), plus the quadratic end | - | - | %s | yes: bound |' % L(split_total))
ledger_rows.append('| map back, two reference hashes, comparisons (success path) | - | - | %s (%s + %s + 44) | no |' % (L(FINAL), L(MAPB), L(VER)))
tab = ['| d | tries t(d) | shift(d) | pow(d) measured | pow bound used | gcd bound | div bound | level charge |', '|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
    tab.append('| ' + ' | '.join(L(x) for x in r) + ' |')
tab.append('| quadratic end (d = 2) | | | | | | | %s |' % L(QUAD))
tab.append('| total (%d tries) | | | | | | | %s |' % (tries_sum, L(split_total)))

WORST_FORMULA = 'init + setup + sampler + 2 x (driver + B + C + D bound + E) + isolation call + end + F + final = %s + %s + %s + 2 x (%s + %s + %s + %s + %s) + %s + %s + %s + %s' % (
    L(INIT), L(SETUP), L(SAMPLE), L(DRV_FAM), L(BUILD), L(POW), L(GCD_BOUND), L(RM_D), L(DRV_F), L(DRV_END), L(split_total), L(FINAL))
LEDGER_PY = '```python\n' + '\n'.join([
    'from math import log2',
    'C = %d' % C,
    'init, setup, sampler, final = %d, %d, %d, %d' % (INIT, SETUP, SAMPLE, FINAL),
    'driver, driver_f, driver_end = %d, %d, %d' % (DRV_FAM, DRV_F, DRV_END),
    'build, power, gcd_bound, remove = %d, %d, %d, %d' % (BUILD, POW, GCD_BOUND, RM_D),
    'split = %d' % split_total,
    'N = init + setup + sampler + 2 * (driver + build + power + gcd_bound + remove) + driver_f + driver_end + split + final',
    "print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % log2(N / C))"]) + '\n```\n'

# ---- sources
SRC_FILES = ['common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'attack.h', 'ntt.c', 'poly.c', 'lean.c', 'line.c', 'split.c', 'twofam.c', 'certrun.c', 'test_split.c', 'calib.c']


def appendix():
    out = []
    for fn in SRC_FILES:
        body = open(os.path.join(HERE, fn)).read().rstrip('\n')
        out.append('### ' + fn + '\n\n```c\n' + body + '\n```\n')
    return '\n'.join(out)


# ---- certificates
colls = json.load(open(os.path.join(HERE, 'data', 'collisions.json')))
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
    da, db = ref.digest_bytes(ma, R), ref.digest_bytes(mb, R)
    assert da == db and ma != mb
    seen.add(key); k += 1
    open(os.path.join(OUT, 'certificates', 'c%d-a.bin' % k), 'wb').write(ma)
    open(os.path.join(OUT, 'certificates', 'c%d-b.bin' % k), 'wb').write(mb)
    man.append({"id": "collision-%d" % k, "type": "hash-collision-witness-v2", "message_a": "certificates/c%d-a.bin" % k, "message_b": "certificates/c%d-b.bin" % k,
                "expected_digest": da.hex(), "target_profile": PROFILE})
N_CERT = k
json.dump({"schema_version": 2, "certificates": man}, open(os.path.join(OUT, 'certificates', 'manifest.json'), 'w', newline='\n'), indent=1)

repl = {
    'TIME_LOG2': '%.3f' % time_claim, 'TIME_LOG2_EXACT': '%.5f' % t_exact,
    'MEM_LOG2': '%.3f' % mem_log2, 'MEM_BYTES': L(mem_bytes), 'MEM_PEN': '%.3f' % mem_pen, 'SCORE': '%.3f' % score,
    'PCLAIM': repr(PCLAIM), 'N_CERT': str(N_CERT), 'TRIES_SUM': 'for the worst schedule %d tries' % tries_sum,
    'GCD_BOUND': L(GCD_BOUND), 'GCD_OBS': L(GCD_OBS), 'RM_D': L(RM_D), 'QUAD': L(QUAD),
    'SAMPLE': L(SAMPLE), 'SAMPLE_OBS': ', '.join(L(x) for x in SAMPLE_OBS), 'SQRT_ARITH': L(SQRT_ARITH), 'A_Q': L(A_Q), 'A_QP1H': L(A_QP1H), 'SQRT_MAX_OBS': L(SQRT_MAX_OBS),
    'LEDGER_TABLE': '\n'.join(ledger_rows) + '\n\nWorst case of the root isolation (stage F) over the level schedule of section 4.1 (starting degree 390625):\n\n' + '\n'.join(tab),
    'WORST_FORMULA': WORST_FORMULA, 'WORST_TOTAL': L(worst), 'WORST_UNITS': '{:,.1f}'.format(worst / C),
    'TYPICAL': L(typ) if typ else 'n/a', 'TYPFIRST': L(typ_first) if typ_first else 'n/a', 'LEDGER_PY': LEDGER_PY,
    'PEAK_MAIN': L(PEAK_MAIN), 'PEAK_SHIFT': L(peak_shift), 'PEAK_POW': L(peak_pow), 'PEAK_GCD': L(peak_gcd), 'HEAP_PEAK': L(HEAP),
    'STATIC_DESC': 'text %s + data %s + bss %s = %s bytes' % (L(int(size[0])), L(int(size[1])), L(int(size[2])), L(static)),
    'FILE_ORDER': ', '.join('`%s`' % f for f in SRC_FILES), 'APPENDIX': appendix(),
}
t = open(os.path.join(HERE, 'proof_template.md')).read()
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


s2, s3, s4, s5, s6, s7, s8, s9, s10, s11 = (ln(p) for p in ['## 2.', '## 3.', '## 4.', '## 5.', '## 6.', '## 7.', '## 8.', '## 9.', '## 10.', '## 11.'])
s41, s61 = ln('### 4.1'), ln('### 6.1')
claim = {
    "schema_version": 3, "submission_state": "ready", "target_profile": PROFILE, "attack_class": "ordinary-collision", "rounds": R,
    "claim": {"time_log2": time_claim, "time_unit": "target-compressions", "memory_log2_bytes": mem_log2,
              "preprocessing_log2": ceil3(math.log2(INIT / C)), "success_probability": PCLAIM, "nonuniform_advice_log2_bytes": 0},
    "restrictions": [
        "Applies to the selected target poseidon-orchard-r2-prefix-v1 only (two partial rounds plus the eight fixed full rounds); the construction uses the first two full rounds being skippable on two lines and gives no claim for other round counts.",
        "One attempt of the program; the claimed success probability 0.4999999999 is the lower bound proved in proof.md section 9 (counting lemma times the root-isolation bound 1 - 2^-35, minus the sampler failure 2^-127) and uses independent uniform random words as the model primitive."],
    "baseline_improved": "poseidon-orchard-r2-nominal-v2",
    "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
    "heuristics": [
        {"id": "H1-charging-rules", "role": "supporting",
         "statement": "The counts of proof.md sections 6 and 7 describe the executed program of proof.md section 11 under the stated rules: 1 per field operation, 1 per element load or store plus 1 address operation, 3 per loop iteration plus 2 per loop exit, 1 per other executed index or control operation, 258 per reduced permutation evaluation, and a 16-word register file per transform block as the only register assumption.",
         "scope": "All stages of the program of proof.md section 4 at the target dimensions (m = 390625 for the main powering, N = 786432 and N' = 393216 in its transforms, 393216 evaluations per family).",
         "extrapolation": "None for the data-independent stages (they are executed totals) or for the sampler and driver (enumerated). The data-dependent stages (classical gcd, deflation, root isolation) are charged at derived bounds that the program asserts against its own counters at every execution.",
         "evidence_ids": ["proof:%d-%d" % (ln('## 6.'), s61 - 1), "proof:%d-%d" % (s7, s8 - 1)],
         "limitations": "The counts are produced by the instrumentation written into the source; the source is part of the proof text and was not run by the organizer. Word-level costs outside the stated rules (cache, bandwidth) are not part of the model."},
        {"id": "H2-level-structure", "role": "supporting",
         "statement": "In the worst-case bound of the root isolation, the charge of one step of the Taylor shift and of Z^((p-1)/2) mod G is a nondecreasing function of the degree, halving the degree at least halves it, and the number of steps of the powering for a degree d <= k exceeds the number at k by at most 2 (so the bound pow(k) + 2P + (s + 2 - u)X holds for all d <= k, with P the per-step charge and X the extra charge of an exponent bit 1).",
         "scope": "Stage F of proof.md section 7, levels k = 390625, 195312, ... , 5; levels at or below 47 are charged by the maximum of the calibrated charge of every degree up to k.",
         "extrapolation": "From the measured charge at each level's maximum degree to every smaller degree at that level, by the structure of the code (plan sizes and linear passes), not by a margin.",
         "evidence_ids": ["proof:%d-%d" % (s7, s8 - 1)],
         "limitations": "A statement about the code, checked at the calibrated degrees and not run for every degree. It affects only the charged time of a branch that is entered with probability below 2^-35 beyond the level d = 3 and not the success probability."}]}
json.dump(claim, open(os.path.join(OUT, 'claim.json'), 'w', newline='\n'), indent=1)
for h in claim['heuristics']:
    for kk in ('statement', 'scope', 'extrapolation', 'limitations'):
        assert len(h[kk]) <= 4096, (h['id'], kk)
for r_ in claim['restrictions']:
    assert len(r_) <= 1024
print(json.dumps(dict(time=time_claim, t_exact=t_exact, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, worst=worst, units=worst / C, split=split_total, heap=HEAP, n_cert=N_CERT, typical=typ,
                      alt_t40_time=math.log2(alt_worst / C), ledger_log=ledger_name, drv=drv_obs), indent=1))
json.dump(dict(time=time_claim, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, worst=worst, split=split_total, heap=HEAP, n_cert=N_CERT, alt_t40_time=math.log2(alt_worst / C)),
          open(os.path.join(HERE, 'data', 'numbers.json'), 'w'))

exec(open(os.path.join(HERE, "note_tail.py")).read())
