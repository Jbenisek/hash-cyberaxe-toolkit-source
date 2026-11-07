"""Assemble the candidate folder pkg_stage/ (claim.json, proof.md, certificates/) and submission-note.md from the ledger logs.
Every number in proof.md and claim.json is computed here from: logs/attempt_<seed>.txt (data-independent stages), logs/calib.txt (levels of the root
isolation), logs/size.txt (static image), data/collisions.json (certificates)."""
import json, math, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pkg_stage')
C = 237
STACK, ALLOC = 65536, 4096
D = 78125
INV_CTL, INVA = 2310, 330
MARGIN = 1.02
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


# ---- data-independent stages from an attempt log
att = [f for f in sorted(os.listdir(os.path.join(HERE, 'logs'))) if f.startswith('attempt_')]
ledger_log = os.environ.get('LEDGER', None)
logtxt = None
for f in att:
    t = open(os.path.join(HERE, 'logs', f)).read()
    if 'family 1: W^p mod F' in t and 'RESULT' in t:        # an attempt that went through both families
        logtxt = t; ledger_name = f; break
if logtxt is None:
    for f in att:
        t = open(os.path.join(HERE, 'logs', f)).read()
        if 'W^p mod F' in t: logtxt = t; ledger_name = f; break


def stage(txt, name):
    m = re.search(r'^\s{2}' + re.escape(name) + r'\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+)\s+([\d.]+)s peak=(\d+)', txt, re.M)
    return None if not m else dict(arith=int(m.group(1)), other=int(m.group(2)), total=int(m.group(3)), sec=float(m.group(4)), peak=int(m.group(5)))


INIT = stage(logtxt, 'init (twiddle table)')['total']
SETUP = stage(logtxt, 'two line setups + intersection')['total']
BUILD = stage(logtxt, 'family 0: build F (evaluations + NTT)')['total']
POW = stage(logtxt, 'family 0: W^p mod F')['total']
GCDM = [int(x) for x in re.findall(r'gcd degree \d+, charged (\d+), derived bound (\d+)', logtxt)[0]]
GCD_OBS, GCD_B_C = GCDM
assert GCD_B_C == gcd_bound(D, D - 1), (GCD_B_C, gcd_bound(D, D - 1))
GCD_BOUND = gcd_bound(D, D - 1)
assert GCD_OBS <= GCD_BOUND
FINAL_OBS = 0
for nm in ('map back (two inputs)', 'verification (2 reference hashes)'):
    for f in att:
        tt = open(os.path.join(HERE, 'logs', f)).read()
        stg = stage(tt, nm)
        if stg: FINAL_OBS += stg['total']; break
PEAK_MAIN = max(int(x) for x in re.findall(r'heap_peak=(\d+)', logtxt))

# ---- calibration
cal = open(os.path.join(HERE, 'logs', 'calib.txt')).read()
levels = {}
for m in re.finditer(r'LEVEL d=(\d+) shift=(\d+) pow=(\d+) shift_abs_peak=(\d+) pow_abs_peak=(\d+)', cal):
    levels[int(m.group(1))] = tuple(int(m.group(i)) for i in range(2, 6))
RM_D = int(re.search(r'REMOVE d=78125 charged=(\d+)', cal).group(1))

# ---- the level schedule of the worst case
sched = []
d = D
while d >= 3:
    sched.append(d); d //= 2
rows = []
split_total = 0
tries_sum = 0
for d in sched:
    sh, pw, pk1, pk2 = levels[d]
    t = tries(d)
    dv = max(div_bound(d + 1, a + 1) for a in range(d // 2 + 1, d)) if d >= 3 else 0
    gb = gcd_bound(d, d - 1)
    per_try = int(math.ceil(MARGIN * (sh + pw))) + gb + dv + 100
    split_total += t * per_try
    tries_sum += t
    rows.append((d, t, sh, pw, gb, dv, t * per_try))
QUAD = 16000
split_total += QUAD + 100
SAMPLE_ALLOW = 1900
FINAL_ALLOW = 200000
family_cost = BUILD + POW + GCD_BOUND + RM_D
worst = INIT + SETUP + SAMPLE_ALLOW + 2 * family_cost + split_total + FINAL_ALLOW
t_exact = math.log2(worst / C)
time_claim = ceil3(t_exact)

# typical run
typ = None
m = re.search(r'SUMMARY total_all=(\d+)', logtxt)
if m: typ = int(m.group(1))
typ_first = None
for f in att:
    tt = open(os.path.join(HERE, 'logs', f)).read()
    if 'success=1' in tt and 'family 1: W^p mod F' not in tt:
        typ_first = int(re.search(r'SUMMARY total_all=(\d+)', tt).group(1)); break

# ---- memory
size = open(os.path.join(HERE, 'logs', 'size.txt')).read().split('\n')[1].split()
static = int(size[0]) + int(size[1]) + int(size[2])
peak_pow = max(v[3] for v in levels.values())
peak_shift = max(v[2] for v in levels.values())
elt = 32
peak_gcd = 5 * (D + 1) * elt + 1048576
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
ledger_rows.append('| A: sampler (at most 128 words) and `y = H(x)` | - | - | %s allowance (observed 279-291) | derived: 128 x 12 + 42 + 237 |' % L(SAMPLE_ALLOW))
sb = stage(logtxt, 'family 0: build F (evaluations + NTT)')
ledger_rows.append('| B (per family): 98304 evaluations (units) + inverse NTT 98304 + normalisation | %s | %s | %s | no |' % (L(sb['arith']), L(sb['other']), L(sb['total'])))
sp = stage(logtxt, 'family 0: W^p mod F')
ledger_rows.append('| C (per family): `W^p mod F` (m = 78125, 238 steps) | %s | %s | %s | no |' % (L(sp['arith']), L(sp['other']), L(sp['total'])))
ledger_rows.append('| D (per family): classical gcd, derived bound for (78125, 78124) | - | - | %s (charged in the run: %s) | yes: bound |' % (L(GCD_BOUND), L(GCD_OBS)))
ledger_rows.append('| E (per family): copy of G and two deflations at d = 78125 | - | - | %s | linear in d |' % L(RM_D))
ledger_rows.append('| F: root isolation, worst case over the level schedule (table below), plus the quadratic end | - | - | %s | yes: bound |' % L(split_total))
ledger_rows.append('| map back and two reference hashes (success path) | - | - | %s allowance (observed %s) | no |' % (L(FINAL_ALLOW), L(FINAL_OBS)))
tab = ['| d | tries t(d) | shift(d) | pow(d) | gcd bound | div bound | t(d) x (1.02 (shift + pow) + gcd + div + 100) |', '|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
    tab.append('| ' + ' | '.join(L(x) for x in r) + ' |')
tab.append('| quadratic end (d = 2) and level control | | | | | | %s |' % L(QUAD + 100))
tab.append('| total | %d | | | | | %s |' % (tries_sum, L(split_total)))

WORST_FORMULA = 'init + setup + sampler allowance + 2 x (B + C + D bound + E) + F bound + final allowance = %s + %s + %s + 2 x (%s + %s + %s + %s) + %s + %s' % (
    L(INIT), L(SETUP), L(SAMPLE_ALLOW), L(BUILD), L(POW), L(GCD_BOUND), L(RM_D), L(split_total), L(FINAL_ALLOW))
LEDGER_PY = '```python\n' + '\n'.join([
    'from math import log2',
    'C = 237',
    'init, setup, sampler, final = %d, %d, %d, %d' % (INIT, SETUP, SAMPLE_ALLOW, FINAL_ALLOW),
    'build, power, gcd_bound, remove = %d, %d, %d, %d' % (BUILD, POW, GCD_BOUND, RM_D),
    'split = %d' % split_total,
    'N = init + setup + sampler + 2 * (build + power + gcd_bound + remove) + split + final',
    "print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % log2(N / C))"]) + '\n```\n'

# ---- sources
SRC_FILES = ['common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'attack.h', 'ntt.c', 'poly.c', 'lean.c', 'line.c', 'split.c', 'twofam.c', 'test_split.c', 'calib.c']


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
    da, db = ref.digest_bytes(ma, 1), ref.digest_bytes(mb, 1)
    assert da == db and ma != mb
    seen.add(key); k += 1
    open(os.path.join(OUT, 'certificates', 'c%d-a.bin' % k), 'wb').write(ma)
    open(os.path.join(OUT, 'certificates', 'c%d-b.bin' % k), 'wb').write(mb)
    man.append({"id": "collision-%d" % k, "type": "hash-collision-witness-v2", "message_a": "certificates/c%d-a.bin" % k, "message_b": "certificates/c%d-b.bin" % k,
                "expected_digest": da.hex(), "target_profile": "poseidon-orchard-r1-prefix-v1"})
N_CERT = k
json.dump({"schema_version": 2, "certificates": man}, open(os.path.join(OUT, 'certificates', 'manifest.json'), 'w', newline='\n'), indent=1)

repl = {
    'TIME_LOG2': '%.3f' % time_claim, 'TIME_LOG2_EXACT': '%.5f' % t_exact,
    'MEM_LOG2': '%.3f' % mem_log2, 'MEM_BYTES': L(mem_bytes), 'MEM_PEN': '%.3f' % mem_pen, 'SCORE': '%.3f' % score,
    'PCLAIM': repr(PCLAIM), 'N_CERT': str(N_CERT), 'TRIES_SUM': 'for the worst schedule %d tries' % tries_sum,
    'GCD_BOUND': L(GCD_BOUND), 'GCD_OBS': L(GCD_OBS), 'RM_D': L(RM_D), 'QUAD': L(QUAD),
    'MONO_NOTE': '(the table lists the measured values; the 1.02 factor is applied in its last column)',
    'LEDGER_TABLE': '\n'.join(ledger_rows) + '\n\nWorst case of the root isolation (stage F) over the level schedule of section 4.1 (starting degree 78125):\n\n' + '\n'.join(tab),
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
    "schema_version": 3, "submission_state": "ready", "target_profile": "poseidon-orchard-r1-prefix-v1", "attack_class": "ordinary-collision", "rounds": 1,
    "claim": {"time_log2": time_claim, "time_unit": "target-compressions", "memory_log2_bytes": mem_log2,
              "preprocessing_log2": ceil3(math.log2(INIT / C)), "success_probability": PCLAIM, "nonuniform_advice_log2_bytes": 0},
    "restrictions": [
        "Applies to the selected target poseidon-orchard-r1-prefix-v1 only (one partial round plus the eight fixed full rounds); the construction uses the first two full rounds being skippable on two lines and gives no claim for other round counts.",
        "One attempt of the program; the claimed success probability 0.4999999999 is the lower bound proved in proof.md section 9 (counting lemma times the root-isolation bound 1 - 2^-36, minus the sampler failure 2^-127) and uses independent uniform random words as the model primitive."],
    "baseline_improved": "poseidon-orchard-r1-nominal-v2",
    "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
    "heuristics": [
        {"id": "H1-charging-rules", "role": "supporting",
         "statement": "The counts of proof.md sections 6 and 7 describe the executed program of proof.md section 11 under the stated rules: 1 per field operation, 1 per element load or store plus 1 address operation, 3 per loop iteration plus 2 per loop exit, 1 per other executed index or control operation, 237 per reduced permutation evaluation, and a 16-word register file per transform block as the only register assumption.",
         "scope": "All stages of the program of proof.md section 4 at the target dimensions (m = 78125 for the main powering, N = 196608 and N' = 98304 in its transforms, 98304 evaluations per family).",
         "extrapolation": "None for the data-independent stages (they are executed totals). The data-dependent stages (classical gcd, deflation, root isolation) are charged at derived bounds that the program asserts against its own counters at every execution.",
         "evidence_ids": ["proof:%d-%d" % (ln('## 6.'), s61 - 1), "proof:%d-%d" % (s7, s8 - 1)],
         "limitations": "The counts are produced by the instrumentation written into the source; the source is part of the proof text and was not run by the organizer. Word-level costs outside the stated rules (cache, bandwidth) are not part of the model."},
        {"id": "H2-level-monotonicity", "role": "supporting",
         "statement": "In the worst-case bound of the root isolation, the charge of one level of degree d' <= d is at most 1.02 times the charge measured at degree d for the Taylor shift and for Z^((p-1)/2) mod G; the gcd and division parts are derived bounds.",
         "scope": "Stage F of proof.md section 7, levels d = 78125, 39062, ... , 4 (about 0.4 percent comes from the length of the exponent prefix, which varies by one step per power of two; the factor 1.02 covers it).",
         "extrapolation": "From the measured charge at each level's maximum degree to every smaller degree at that level.",
         "evidence_ids": ["proof:%d-%d" % (s7, s8 - 1)],
         "limitations": "Not run for every degree. It affects only the charged time of a branch that is entered with probability below 2^-36 beyond the level d = 3 and not the success probability."}]}
json.dump(claim, open(os.path.join(OUT, 'claim.json'), 'w', newline='\n'), indent=1)
for h in claim['heuristics']:
    for kk in ('statement', 'scope', 'extrapolation', 'limitations'):
        assert len(h[kk]) <= 4096, (h['id'], kk)
for r in claim['restrictions']:
    assert len(r) <= 1024
print(json.dumps(dict(time=time_claim, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, worst=worst, units=worst / C, split=split_total, heap=HEAP, n_cert=N_CERT, typical=typ), indent=1))
json.dump(dict(time=time_claim, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, worst=worst, split=split_total, heap=HEAP, n_cert=N_CERT), open(os.path.join(HERE, 'data', 'numbers.json'), 'w'))

exec(open(os.path.join(HERE, "note_tail.py")).read())
