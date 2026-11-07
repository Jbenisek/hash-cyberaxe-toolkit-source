"""Assemble pkg_stage_exec/ (claim.json, proof.md, certificates/) and submission-note_exec.md for the executed-outcome entry (r = 1, 2 or 3, read from the log).
Every number comes from logs/exec_run.txt (the one counted run), logs/size_exec.txt (static image), logs/mem_exec.json (memmeter peak of the counted run) and data/collisions_exec.json."""
import json, math, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.environ.get('PKG_OUT', 'pkg_stage_exec'))
LEDGER = os.environ.get('LEDGER', 'exec_run.txt')
SIZE_FILE = os.environ.get('SIZE_FILE', os.path.join('logs', 'size_exec.txt'))
MEM_FILE = os.environ.get('MEM_FILE', os.path.join('logs', 'mem_exec.json'))
PROBES = os.environ.get('PROBES', '')   # e.g. '2-11': one-trial runs made concurrently with the counted run (scheduling only)
NOTE_OUT = os.environ.get('NOTE_OUT', 'submission-note_exec.md')
NUMBERS = os.environ.get('NUMBERS', 'numbers_exec.json')
COLLS = os.environ.get('COLLS', 'collisions_exec.json')
STACK = 65536
sys.path.insert(0, HERE)
import poseidon_ref as ref


def L(x): return '{:,}'.format(int(x))
def ceil5(x): return math.ceil(round(x * 100000, 6)) / 100000
def ceil3(x): return math.ceil(x * 1000) / 1000


logtxt = open(os.path.join(HERE, 'logs', LEDGER)).read()
R = int(re.search(r'^r=(\d+) line=', logtxt, re.M).group(1))
C = 216 + 21 * R
m = int(re.search(r'^r=\d+ line=\d+ m=(\d+)', logtxt, re.M).group(1))
PAR = {
    1: dict(PARTIAL='one partial round 4', PARTIAL_WORD='one partial round', PARTIALRS='4', LAYERS='seven', DEXP=7, D=78125, H=49152, HEXP=14, N2=98304, AEXP=15, VEXP=15,
            FD0='0x1c66a426cd2d5ec686ea41cae3a27d49c8724fffa0bc4f305029be8b2cce93c3'),
    2: dict(PARTIAL='two partial rounds 4 and 5', PARTIAL_WORD='two partial rounds', PARTIALRS='4, 5', LAYERS='eight', DEXP=8, D=390625, H=196608, HEXP=16, N2=393216, AEXP=17, VEXP=17,
            FD0='0x13f08536819885e275e9b4b9c9c3aaaf453220a766fbe69710da897c392caa6f'),
    3: dict(PARTIAL='three partial rounds 4, 5 and 6', PARTIAL_WORD='three partial rounds', PARTIALRS='4, 5, 6', LAYERS='nine', DEXP=9, D=1953125, H=1572864, HEXP=19, N2=3145728, AEXP=20, VEXP=19,
            FD0='0x11f9cfdeecb8c5965318cbdc58480d2e6db510f12862658af639ce81578c3e23'),
    4: dict(PARTIAL='four partial rounds 4, 5, 6 and 7', PARTIAL_WORD='four partial rounds', PARTIALRS='4, 5, 6, 7', LAYERS='ten', DEXP=10, D=9765625, H=6291456, HEXP=21, N2=12582912, AEXP=22, VEXP=22,
            FD0='0x0eae601a80e5d207e772f8ff7333c0b8f442a251f419e3ee3506ef0b5e3612a9'),
    5: dict(PARTIAL='five partial rounds 4, 5, 6, 7 and 8', PARTIAL_WORD='five partial rounds', PARTIALRS='4, 5, 6, 7, 8', LAYERS='eleven', DEXP=11, D=48828125, H=25165824, HEXP=23, N2=50331648, AEXP=24, VEXP=24,
            FD0='0x3d8a63413498ea10d01ec5a3bc7106382d152c057486fdb7dfe795da6ea4e687'),
}[R]
assert m == (PAR['D'] - 1) // 2
TARGET = 'poseidon-orchard-r%d-prefix-v1' % R

names = ['init (twiddle table)', 'line setup', 'A: centre c_i = i', 'B: build g', 'C: S^((p-1)/2) mod g', 'D: gcd(g, S^h - 1) (half-gcd)', 'E: root isolation', 'F: sqrt + map back',
         'G: verification (2 reference hashes)', 'H: canonical encoding of the output', 'I: report formatting, single write, exit']
def stage(name):
    mm = re.search(r'^\s{2}' + re.escape(name) + r'\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+) peak=(\d+)', logtxt, re.M)
    assert mm, name
    return dict(arith=int(mm.group(1)), other=int(mm.group(2)), total=int(mm.group(3)), peak=int(mm.group(4)))
S_ = {n: stage(n) for n in names}
sm = re.search(r'SUMMARY total_all=(\d+) total_arith=\d+ heap_peak=(\d+)', logtxt)
N = int(sm.group(1)); HEAP = int(sm.group(2))
ar = re.search(r'^ARENA size=(\d+) extent=(\d+)', logtxt, re.M); ARENA = int(ar.group(1)); EXTENT = int(ar.group(2))
assert ARENA % 64 == 0 and EXTENT <= ARENA and HEAP <= EXTENT
PEAKSTAGE = max(names, key=lambda n: S_[n]['peak']).split(':')[0]
assert N == sum(S_[n]['total'] for n in names), 'stage totals do not add up to the run total'
assert HEAP == max(S_[n]['peak'] for n in names)
rec = re.search(r'^RECONCILE stages=(\d+) trials=(\d+) counters=(\d+) ok=(\d)', logtxt, re.M)
assert rec and rec.group(4) == '1' and int(rec.group(1)) == int(rec.group(2)) == int(rec.group(3)) == N
RECONCILE = 'stages %s = trials %s = counters %s' % (L(rec.group(1)), L(rec.group(2)), L(rec.group(3)))
assert 'RESULT found=1 success=1' in logtxt and re.search(r'^EXIT 0', logtxt, re.M)
TR = [tuple(int(x) for x in g) for g in re.findall(r'^TRIALROW (\d+) centre (\d+) degG (\d+) gcd (\d+) total (\d+)', logtxt, re.M)]
OUTSIDE = int(re.search(r'^TRIALROW 0 outside the trials \(init, line setup, output encoding, report and write\) total (\d+)', logtxt, re.M).group(1))
TRIALS = int(re.search(r'^TRIALS (\d+)', logtxt, re.M).group(1))
assert len(TR) == TRIALS and all(t[2] == 0 for t in TR[:-1]) and TR[-1][2] >= 1 and sum(t[4] for t in TR) + OUTSIDE == N
GCD_OBS = sum(t[3] for t in TR)
TRIAL_TABLE = ('| trial | centre c_i | deg G | half-gcd charge | charge of the trial (stages A to G) |\n|---:|---:|---:|---:|---:|\n'
               + '\n'.join('| %d | %d | %d | %s | %s |' % (t[0], t[1], t[2], L(t[3]), L(t[4])) for t in TR)
               + '\n| outside the trials: init, line setup, stage H | | | | %s |\n| total N | | | | %s |' % (L(OUTSIDE), L(N)))
t_exact = math.log2(N / C); time_claim = ceil5(t_exact)
bd = re.search(r'newton total=(\d+) arith=(\d+) \| prefix\+scale total=(\d+) \| loop steps=(\d+) total=(\d+) arith=(\d+)', logtxt)
STEPS = int(bd.group(4)); assert STEPS == 253 - PAR['VEXP']
PER_STEP = int(bd.group(5)) // STEPS; PER_STEP_ARITH = int(bd.group(6)) // STEPS
size = open(os.path.join(HERE, SIZE_FILE)).read().split('\n')[1].split()
static = int(size[0]) + int(size[1]) + int(size[2])
assert int(size[2]) >= ARENA
MM = json.load(open(os.path.join(HERE, MEM_FILE)))
assert MM['exit'] == 0 and not MM['failed']
RSS = int(MM['peak_bytes'])                     # memmeter: max(wait4 ru_maxrss, sampled VmHWM, sampled summed VmRSS) of the counted run
SUMPARTS = static + STACK                        # the heap is the static arena inside the bss of the image
SECS = float(MM['wall_s'])
mem_bytes = max(SUMPARTS, RSS)                   # the claim takes the larger of the counted parts and the measured peak
mem_log2 = ceil3(math.log2(mem_bytes)); mem_pen = round(max(0, mem_log2 - 20), 3)
score = round(time_claim + mem_pen, 5)
pk = re.search(r'^PEAKLIVE allocations=(\d+) payload=(\d+) headers=(\d+)', logtxt, re.M)
PEAK_LIVE, PEAK_PAY, HDR = int(pk.group(1)), int(pk.group(2)), int(pk.group(3))
MEM_BASIS = ('the larger of the two is the measured peak' if RSS > SUMPARTS else 'the measured peak is below the counted sum, so the claim takes the sum')
tm = re.search(r'^TYPES add=(\d+) sub=(\d+) mul=(\d+) sqr=(\d+) ld=(\d+) st=(\d+) ctl=(\d+) rnd=(\d+) perm=(\d+)', logtxt, re.M)
centre = re.search(r'COLLISION centre\s+(0x[0-9a-f]+)', logtxt).group(1)
digest = re.search(r'COLLISION digest\s+(0x[0-9a-f]+)', logtxt).group(1)

rows = ['| stage | arith | other | total |', '|---|---:|---:|---:|']
labels = ['init: twiddle table (once)', 'setup: the line', 'A: centre c_i = i (all trials)',
          'B: %s evaluations (%d units each) + inverse NTT %s + normalisation (all trials)' % (L(PAR['N2']), C, L(PAR['H'])),
          'C: `S^((p-1)/2) mod g` (m = %d, %d steps per trial, all trials)' % (m, STEPS), 'D: half-gcd of (g, R - 1) (all trials)', 'E: root of G (last trial only)',
          'F: square root, back-map (last trial only)', 'G: two reference hashes (last trial only)', 'H: canonical encoding of the output (6 conversions, 384 hexadecimal digits)', 'I: formatting of the report buffer (bound), the single write, exit_group, entry (constants)']
for lab, n in zip(labels, names):
    s = S_[n]; rows.append('| %s | %s | %s | %s |' % (lab, L(s['arith']), L(s['other']), L(s['total'])))
rows.append('| total N | | | %s |' % L(N))
LEDGER_PY = '\n'.join(['from math import log2, ceil', 'C = %d' % C,
                       'stages = [%s]   # init, line setup, A, B, C, D, E, F, G, H' % ', '.join(str(S_[n]['total']) for n in names),
                       'trials = [%s]   # stages A to G of each trial' % ', '.join(str(t[4]) for t in TR),
                       'outside = %d     # init, line setup, stage H' % OUTSIDE,
                       'N = sum(stages)', 'assert N == sum(trials) + outside',
                       "print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))"])

SRC_FILES = ['outbuf.h', 'nolibc.c', 'common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'attack.h', 'hgcd.h', 'ntt.c', 'gen_kern.py', 'ntt_kern.h', 'ntt_a3.h', 'poly.c', 'lean.c', 'line.c', 'split.c', 'hgcd.c', 'single.c']
def appendix():
    out = []
    for fn in SRC_FILES:
        body = open(os.path.join(HERE, fn)).read().rstrip('\n')
        out.append('### ' + fn + '\n\n```' + ('python' if fn.endswith('.py') else 'c') + '\n' + body + '\n```\n')
    return '\n'.join(out)
# the sites of the unrolled-loop macro (outside its definition)
f8 = {}
for fn in SRC_FILES:
    if fn.endswith('.c') or fn.endswith('.h'):
        k = sum(1 for line in open(os.path.join(HERE, fn)) if 'FOR8(' in line and '#define FOR8' not in line)
        if k: f8[fn] = k
FOR8_LIST = 'The sites of `FOR8` are: ' + ', '.join('`%s` (%d lines)' % (fn, k) for fn, k in f8.items()) + '.'
FOR8_SHORT = 'sites in ' + ', '.join('%s: %d' % (fn, k) for fn, k in f8.items())
assert f8

colls = json.load(open(os.path.join(HERE, 'data', COLLS)))
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(os.path.join(OUT, 'certificates'))
v = colls[0]
nk1, rho1, nk2, rho2 = v['nk1'], v['rho1'], v['nk2'], v['rho2']
ma = nk1.to_bytes(32, 'little') + rho1.to_bytes(32, 'little'); mb = nk2.to_bytes(32, 'little') + rho2.to_bytes(32, 'little')
da, db = ref.digest_bytes(ma, R), ref.digest_bytes(mb, R)
assert da == db and ma != mb
open(os.path.join(OUT, 'certificates', 'c1-a.bin'), 'wb').write(ma); open(os.path.join(OUT, 'certificates', 'c1-b.bin'), 'wb').write(mb)
json.dump({"schema_version": 2, "certificates": [{"id": "collision-1", "type": "hash-collision-witness-v2", "message_a": "certificates/c1-a.bin", "message_b": "certificates/c1-b.bin",
                                                   "expected_digest": da.hex(), "target_profile": TARGET}]},
          open(os.path.join(OUT, 'certificates', 'manifest.json'), 'w', newline='\n'), indent=1)

a_ = PAR['AEXP']
SIM_EXTENT = int(os.environ['SIM_EXTENT'])
ARENA_MARGIN = 'the replay reached an extent of %s bytes, and `ARENA` adds a margin of %s bytes to it' % (L(SIM_EXTENT), L(ARENA - SIM_EXTENT))
assert ARENA >= SIM_EXTENT
LAST_DEG = TR[-1][2]
if LAST_DEG == 1:
    SPLIT_SENTENCE = 'The root isolation of `split.c` for `deg G >= 2` is not executed by this run (the run has `deg G = 1`).'
else:
    SPLIT_SENTENCE = 'The root isolation of `split.c` runs in the last trial of this run (`deg G = %d`); its random shifts come from the generator seeded with the constant 1, and every operation it executed is in stage E.' % LAST_DEG
if PROBES:
    _pr = PROBES.replace('-', ' to ')
    PROBE_SENTENCE = (' Monitoring experiments: one-trial runs of centres %s were made alongside this run, after the order of the centres was fixed in the source; they select nothing, change no parameter, and the result of the counted run does not depend on them. The algorithm is the single counted run; their work is not part of `N`.' % _pr)
    PROBE_NOTE = (' Monitoring experiments: one-trial runs of centres %s were made alongside the counted run, after the order of the centres was fixed in the source; they select nothing, change no parameter, and the result of the counted run does not depend on them. The algorithm is the single counted run; their work is not part of N.' % _pr)
else:
    PROBE_SENTENCE = PROBE_NOTE = ''
MEM_TOTAL = ('Total: the larger of (a) + (c) = `%s` bytes (the heap is inside (a)) and the measured peak of the run, `%s` bytes (below): `%s` bytes `= 2^%.3f` (rounded up at three decimals); %s. The memory penalty is `max(0, %.3f - 20) = %.3f`.'
             % (L(SUMPARTS), L(RSS), L(mem_bytes), mem_log2, MEM_BASIS, mem_log2, mem_pen))
repl = {
    'R': str(R), 'C': str(C), 'M': str(m), 'M1': str(m - 1), 'D': str(PAR['D']), 'DEXP': str(PAR['DEXP']), 'H': str(PAR['H']), 'HEXP': str(PAR['HEXP']), 'N2': str(PAR['N2']),
    'PARTIAL': PAR['PARTIAL'], 'PARTIALRS': PAR['PARTIALRS'], 'LAYERS': PAR['LAYERS'], 'FD0': PAR['FD0'], 'STEPS': str(STEPS), 'VEXP': str(PAR['VEXP']),
    'TIME_LOG2': '%.5f' % time_claim, 'TIME_LOG2_EXACT': '%.5f' % t_exact, 'N': L(N), 'UNITS': '{:,.1f}'.format(N / C),
    'MEM_LOG2': '%.3f' % mem_log2, 'MEM_BYTES': L(mem_bytes), 'MEM_PEN': '%.3f' % mem_pen, 'SCORE': '%.5f' % score,
    'CENTRE': centre, 'TRIALS': str(TRIALS), 'TRIAL_TABLE': TRIAL_TABLE, 'LASTC': str(TR[-1][1]), 'DIGEST': digest, 'LINE': '0', 'GCD_OBS': L(GCD_OBS), 'LEDGER_TABLE': '\n'.join(rows), 'LEDGER_PY': LEDGER_PY,
    'T_ADD': L(tm.group(1)), 'T_SUB': L(tm.group(2)), 'T_MUL': L(tm.group(3)), 'T_SQR': L(tm.group(4)), 'T_LD': L(tm.group(5)), 'T_ST': L(tm.group(6)), 'T_CTL': L(tm.group(7)), 'T_PERM': L(tm.group(9)),
    'NEWTON': L(bd.group(1)), 'PREFIX': L(bd.group(3)), 'PER_STEP': L(PER_STEP), 'PER_STEP_ARITH': L(PER_STEP_ARITH), 'POW_ARITH': L(S_[names[4]]['arith']),
    'STAGE_PEAKS': '; '.join('%s %s' % (n.split(':')[0] if ':' in n else n, L(S_[n]['peak'])) for n in names), 'HEAP_PEAK': L(HEAP),
    'ARENA': L(ARENA), 'EXTENT': L(EXTENT), 'BSS': L(int(size[2])), 'PEAK_STAGE': PEAKSTAGE, 'ARENA_MARGIN': ARENA_MARGIN,
    'STATIC_DESC': 'text %s + data %s + bss %s = %s bytes' % (L(int(size[0])), L(int(size[1])), L(int(size[2])), L(static)),
    'PEAK_LIVE': str(PEAK_LIVE), 'PEAK_PAY': L(PEAK_PAY), 'HDR': L(HDR), 'RSS': L(RSS), 'RECONCILE': RECONCILE, 'FOR8_LIST': FOR8_LIST, 'SECS': str(int(round(SECS, -1))),
    'TWEXP': str(a_ - 2), 'AEXP': str(a_), 'TWB': L((1 << (a_ - 2)) * 32), 'YB': L(3 * (1 << a_) * 32), 'TMPB': L((1 << a_) * 32), 'MUB': L((m - 1) * 32), 'GB': L((m + 1) * 32), 'FB': L(m * 32),
    'FILE_ORDER': ', '.join('`%s`' % f for f in SRC_FILES), 'SPLIT_SENTENCE': SPLIT_SENTENCE, 'PROBE_SENTENCE': PROBE_SENTENCE, 'MEM_TOTAL': MEM_TOTAL,
    'APPENDIX': appendix(),
}
t = open(os.path.join(HERE, 'proof_template_exec.md')).read()
for key, val in repl.items(): t = t.replace('@@%s@@' % key, val)
left = re.findall(r'@@[A-Z0-9_]+@@', t); assert not left, left
bad = [ch for ch in t if ord(ch) >= 128]; assert not bad, bad[:5]
open(os.path.join(OUT, 'proof.md'), 'w', newline='\n').write(t)

lines = t.split(chr(10))
def ln(prefix):
    for i, l in enumerate(lines, 1):
        if l.startswith(prefix): return i
    raise KeyError(prefix)
claim = {
    "schema_version": 3, "submission_state": "ready", "target_profile": TARGET, "attack_class": "ordinary-collision", "rounds": R,
    "claim": {"time_log2": time_claim, "time_unit": "target-compressions", "memory_log2_bytes": mem_log2,
              "preprocessing_log2": 0, "success_probability": 1, "nonuniform_advice_log2_bytes": 0},
    "restrictions": [
        "Applies to the selected target %s only (%s plus the eight fixed full rounds); the construction uses the first two full rounds being skippable on a line and gives no claim for other round counts." % (TARGET, PAR['PARTIAL_WORD']),
        "Success probability 1 means: one deterministic procedure (centres c_i = i tried in the order i = 1, 2, 3, ... until the first collision, at most 64 trials, a cap not reached) was executed once from the start on the fixed target and stopped with a collision after %d trials; the time is the executed operation count of that run with every trial charged, failed ones included, and the memory its executed peak. It is not a probability over centres; no start was selected beforehand." % TRIALS],
    "baseline_improved": "poseidon-orchard-r%d-nominal-v2" % R,
    "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
    "heuristics": [
        {"id": "H1-charging-rules", "role": "supporting",
         "statement": "The counts of proof.md sections 6 and 7 describe the executed program of proof.md section 9 under the stated rules: 1 per field operation (a Montgomery conversion is one multiplication), 1 per element load or store plus 1 address operation, 3 per loop iteration plus 2 per loop exit (the loops written with the macro FOR8 are unrolled eight times in the source and charged 3 per pass of eight; the generated kernels are straight-line), 1 per other executed index or control operation, %d per reduced permutation evaluation, and a register file of 18 words of 256 bits per transform block (16 data words plus two working words: the twiddle operand and the butterfly temporary) as the only register assumption; the allocator (`xalloc`, `xfree`) is charged per executed operation, and the report formatting, the single write and the exit are charged in stage I." % C,
         "scope": "All stages of the executed run of proof.md section 4 at the target dimensions (m = %d for the powering, N = %d and N' = %d in its transforms, %d evaluations of the line)." % (m, PAR['N2'], PAR['H'], PAR['N2']),
         "extrapolation": "None. The time is the executed total of one run of the shipped source, with every trial charged and the output stage and stage I included; the only bounds in it are the stated constants of stage I and of the stage bookkeeping (proof.md section 4.2); no estimate or other run enters it.",
         "evidence_ids": ["proof:%d-%d" % (ln('## 4.'), ln('## 5.') - 1), "proof:%d-%d" % (ln('## 6.'), ln('## 7.') - 1)],
         "limitations": "The counts are produced by the instrumentation written into the source; the source is part of the proof text and was not run by the organizer. Word-level costs outside the stated rules (cache, bandwidth) are not part of the model."}]}
for r_ in claim['restrictions']: assert len(r_) <= 1024
for h in claim['heuristics']:
    for kk in ('statement', 'scope', 'extrapolation', 'limitations'): assert len(h[kk]) <= 4096
json.dump(claim, open(os.path.join(OUT, 'claim.json'), 'w', newline='\n'), indent=1)

res = dict(time=time_claim, time_exact=t_exact, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, N=N, units=N / C, heap=HEAP, static=static, gcd_obs=GCD_OBS, rss=RSS, peak_live=PEAK_LIVE, secs=SECS, trials=TRIALS)
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(HERE, 'data', NUMBERS), 'w'))

nt = open(os.path.join(HERE, 'note_template.md')).read()
nrepl = {'R': str(R), 'PARTIAL_WORD': PAR['PARTIAL_WORD'], 'TRIALS': str(TRIALS), 'LASTC': str(TR[-1][1]), 'DEXP': str(PAR['DEXP']), 'D': str(PAR['D']), 'M': str(m), 'N2': str(PAR['N2']), 'C': str(C), 'H': str(PAR['H']),
         'STEPS': str(STEPS), 'TIME': '%.5f' % time_claim, 'N': L(N), 'UNITS': '{:,.1f}'.format(N / C), 'MEM_BYTES': L(mem_bytes), 'MEM_LOG2': '%.3f' % mem_log2, 'SCORE': '%.5f' % score,
         'PER_STEP': L(PER_STEP), 'TABLE': '\n'.join(rows), 'TRIAL_TABLE': TRIAL_TABLE, 'RECONCILE': RECONCILE, 'GCD_OBS': L(GCD_OBS), 'FOR8_SHORT': FOR8_SHORT, 'STATIC_BYTES': L(static),
         'PEAK_LIVE': str(PEAK_LIVE), 'HDR': L(HDR), 'HEAP': L(HEAP), 'PEAK_PAY': L(PEAK_PAY), 'AEXP': str(a_), 'RSS': L(RSS), 'SUMPARTS': L(SUMPARTS), 'PROBE_NOTE': PROBE_NOTE}
for key, val in nrepl.items(): nt = nt.replace('@@%s@@' % key, val)
left = re.findall(r'@@[A-Z0-9_]+@@', nt); assert not left, left
assert len(nt.encode()) >= 5 * 1024, len(nt.encode())
assert all(ord(ch) < 128 for ch in nt)
open(os.path.join(HERE, NOTE_OUT), 'w', newline='\n').write(nt)
print('note bytes', len(nt.encode()))
