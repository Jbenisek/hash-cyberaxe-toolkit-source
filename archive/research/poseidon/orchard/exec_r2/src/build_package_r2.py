"""Assemble pkg_stage/ (claim.json, proof.md, certificates/) and submission-note.md for the r=2 executed-outcome entry from logs/full_r2.txt.
Every number comes from that one counted run. Template: the r1 executed entry's proof text, rewritten here for r=2 and the half-unit loop rules."""
import json, math, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); EX = os.path.dirname(HERE)
TPL_R1 = os.path.join(EX, '..', 'single_r1_exec', 'proof_template_exec.md')
OUT = os.path.join(EX, 'pkg_stage'); NOTE_OUT = os.path.join(EX, 'submission-note.md')
C = 258; STACK, ALLOC = 65536, 4096
sys.path.insert(0, HERE)
import poseidon_ref as ref


def L(x): return '{:,}'.format(int(x))
def ceil5(x): return math.ceil(round(x * 100000, 6)) / 100000
def ceil3(x): return math.ceil(x * 1000) / 1000


log = open(os.path.join(EX, 'logs', 'full_r2.txt')).read()
size = open(os.path.join(EX, 'logs', 'size.txt')).read().split('\n')[1].split()
static = int(size[0]) + int(size[1]) + int(size[2])
sm = re.search(r'SUMMARY r=2 centres=(\d+) success=(\d+) total_all=(\d+) total_arith=(\d+) .*heap_peak=(\d+)', log)
TRIALS, succ, N_RUN, ARITH, HEAP = int(sm.group(1)), int(sm.group(2)), int(sm.group(3)), int(sm.group(4)), int(sm.group(5))
assert succ == 1 and 'FAULTS detected=0' in log
PROBE_BOUND = 5000 * 7 * TRIALS
N = N_RUN + PROBE_BOUND
cen = [(int(a) + 1, int(b), int(c)) for a, b, c in re.findall(r'^CENTRE (\d+) j=\d+ degG=(\d+) success=\d+ arith=\d+ all=(\d+)', log, re.M)]
assert len(cen) == TRIALS
keys = ['line_setup', 'centre c_i = i (i = 1, 2, 3, ...)', 'build g', 'S^((p-1)/2) mod g', 'gcd(g, S^h-1) (half-gcd)', 'root finding', 'sqrt + map back', 'verification (2 reference hashes)']
agg = {k: dict(arith=0, other=0, total=0, peak=0) for k in keys}
for m in re.finditer(r'^  (.+?)\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+)\s+([\d.]+)s peak=(\d+)', log, re.M):
    k = m.group(1)
    if k in agg:
        a = agg[k]; a['arith'] += int(m.group(2)); a['other'] += int(m.group(3)); a['total'] += int(m.group(4)); a['peak'] = max(a['peak'], int(m.group(6)))
im = re.search(r'^INIT arith=(\d+) other=(\d+) total=(\d+)', log, re.M)
init = dict(arith=int(im.group(1)), other=int(im.group(2)), total=int(im.group(3)))
stage_sum = init['total'] + sum(a['total'] for a in agg.values())
rounding = N_RUN - stage_sum
assert abs(rounding) <= 8 * TRIALS + 8, rounding
HC = int(re.search(r'HALFUNITS hc=(\d+)', log).group(1))
bd = re.search(r'newton total=(\d+) arith=(\d+) \| prefix\+scale total=(\d+) \| loop steps=(\d+) total=(\d+) arith=(\d+) per-step total=(\d+) arith=(\d+)', log)
assert int(bd.group(4)) == 236
tm = re.search(r'^TYPES add=(\d+) sub=(\d+) mul=(\d+) sqr=(\d+) ld=(\d+) st=(\d+) ctl=(\d+) rnd=(\d+) perm=(\d+)', log, re.M)
centre = re.search(r'COLLISION centre\s+(0x[0-9a-f]+)', log).group(1)
digest = re.search(r'COLLISION digest\s+(0x[0-9a-f]+)', log).group(1)
vals = {k: int(re.search(r'COLLISION %s\s+0x([0-9a-f]{64})' % k, log).group(1), 16) for k in ('nk1', 'rho1', 'nk2', 'rho2')}
t_exact = math.log2(N / C); time_claim = ceil5(t_exact)
mem_bytes = HEAP + static + STACK + ALLOC
mem_log2 = ceil3(math.log2(mem_bytes)); mem_pen = round(max(0, mem_log2 - 20), 3)
score = round(time_claim + mem_pen, 5)
lastc = cen[-1][0]
TRIAL_TABLE = '| trial | centre c_i | deg G | charge of the trial (operations) |\n|---:|---:|---:|---:|\n' + '\n'.join('| %d | %d | %d | %s |' % (k + 1, c, d, tt) for k, (c, d, tt) in enumerate([(a, b, L(c_)) for a, b, c_ in cen]))
labels = {'line_setup': 'setup: the line', keys[1]: 'A: centre c_i = i (all trials)',
          'build g': 'B: 393,216 evaluations (258 units each) + inverse NTT 196,608 + normalisation (all trials)',
          'S^((p-1)/2) mod g': 'C: `S^((p-1)/2) mod g` (m = 195312, 236 steps per trial, all trials)', keys[4]: 'D: half-gcd of (g, R - 1) (all trials)',
          'root finding': 'E: root of G (last trial only)', 'sqrt + map back': 'F: square root, back-map (last trial only)', keys[7]: 'G: two reference hashes (last trial only)'}
rows = ['| stage | arith | other | total |', '|---|---:|---:|---:|', '| init: twiddle table (once) | %s | %s | %s |' % (L(init['arith']), L(init['other']), L(init['total']))]
for k in keys:
    a = agg[k]; rows.append('| %s | %s | %s | %s |' % (labels[k], L(a['arith']), L(a['other']), L(a['total'])))
rows.append('| rounding: half units are rounded up once for the run, not once per stage line | | | %s |' % L(rounding))
rows.append('| total of the counted run | | | %s |' % L(N_RUN))
rows.append('| uncounted self-checks (section 4.2, stated bound) | | | %s |' % L(PROBE_BOUND))
rows.append('| total N | | | %s |' % L(N))
stages = [init['total']] + [agg[k]['total'] for k in keys] + [rounding]
assert sum(stages) == N_RUN
LEDGER_PY = '\n'.join(['from math import log2, ceil', 'C = 258', 'stages = [%s]' % ', '.join(str(x) for x in stages),
                       'run = sum(stages)', 'probe_bound = %d' % PROBE_BOUND, 'N = run + probe_bound',
                       "print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))"])
SRC_FILES = ['common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'attack.h', 'hgcd.h', 'budgets.h', 'gen_kern.py', 'ntt_kern.h', 'ntt.c', 'poly.c', 'loop.c', 'lean.c', 'line.c', 'euclid.c', 'hgcd.c', 'lean_attack.c']


def appendix():
    out = []
    for fn in SRC_FILES:
        body = open(os.path.join(HERE, fn), newline='').read().replace('\r\n', '\n').rstrip('\n')
        assert all(ord(ch) < 128 for ch in body), fn
        out.append('### ' + fn + '\n\n```' + ('python' if fn.endswith('.py') else 'c') + '\n' + body + '\n```\n')
    return '\n'.join(out)


shutil.rmtree(OUT, ignore_errors=True); os.makedirs(os.path.join(OUT, 'certificates'))
ma = vals['nk1'].to_bytes(32, 'little') + vals['rho1'].to_bytes(32, 'little')
mb = vals['nk2'].to_bytes(32, 'little') + vals['rho2'].to_bytes(32, 'little')
da, db = ref.digest_bytes(ma, 2), ref.digest_bytes(mb, 2)
assert da == db and ma != mb and int.from_bytes(da, 'little') == int(digest, 16)
open(os.path.join(OUT, 'certificates', 'c1-a.bin'), 'wb').write(ma)
open(os.path.join(OUT, 'certificates', 'c1-b.bin'), 'wb').write(mb)
manifest = {"schema_version": 2, "certificates": [{"id": "collision-1", "type": "hash-collision-witness-v2", "message_a": "certificates/c1-a.bin",
            "message_b": "certificates/c1-b.bin", "expected_digest": da.hex(), "target_profile": "poseidon-orchard-r2-prefix-v1"}]}
json.dump(manifest, open(os.path.join(OUT, 'certificates', 'manifest.json'), 'w', newline='\n'), indent=1)

t = open(TPL_R1).read()
i42 = t.index('### 4.2 Machine model'); i43 = t.index('### 4.3 Stage C'); i9 = t.index('## 9. Complete source')
new42 = open(os.path.join(HERE, 'rules_r2.md')).read()
t = t[:i42] + new42 + '\n' + t[i43:i9] + open(os.path.join(HERE, 'sec9_r2.md')).read()
t = re.sub(r"on the deployed constants it is nonzero for the line used:\n`f_D\(0\) = 0x[0-9a-f]+`\n\(computed; so `deg F = D` exactly\)\. For random `tau`, `F\(tau\^5\)` equals the reference hash of the canonical inputs built from `tau` \(checked on 5 random `tau`\nagainst an independent big-integer reference that reproduces the 11 public Orchard vectors\)\.",
           "if it vanished on the line used, `g_c` would have lower degree; the program inverts the computed leading coefficient and every output is checked by the reference hash.", t)
reps = [('poseidon-orchard-r1-prefix-v1', 'poseidon-orchard-r2-prefix-v1'), ('Orchard Poseidon, r = 1', 'Orchard Poseidon, r = 2'), ('`C(1) = 237`', '`C(2) = 258`'), ('C(1) = 237', 'C(2) = 258'),
        ('one partial round 4,', 'two partial rounds 4 and 5,'), ('5^7 = D = 78125', '5^8 = D = 390625'), ('`5^7`', '`5^8`'), ('78125', '390625'),
        ('39062', '195312'), ('39061', '195311'), ('98304', '393216'), ('49152', '196608'), ('238', '236'), ('237', '258'),
        ('Rounds 2, 3 (full), 4 (partial, r = 1), 60, 61, 62, 63 (full) put seven S-box layers', 'Rounds 2, 3 (full), 4, 5 (partial, r = 2), 60, 61, 62, 63 (full) put eight S-box layers'),
        ('one partial round', 'two partial rounds'), ('`single 1`', '`exec_attack 2 8 1 0 1 0 0 1`'), ('single 1', 'exec_attack 2 8 1 0 1 0 0 1'),
        ('about 90 s per trial', 'about 20 to 40 minutes per trial'), ('(r = 1)', '(r = 2)'), ('S^v` with `v = 2^15 < m', 'S^v` with `v = 2^17 < m'),
        ('the 15 bits after the leading one are zero', 'the 17 bits after the leading one are zero'), ('15 of the 253 squarings, 15 + 236 = 253', '17 of the 253 squarings, 17 + 236 = 253')]
for a, b in reps:
    t = t.replace(a, b)
repl = {'TIME_LOG2': '%.5f' % time_claim, 'TIME_LOG2_EXACT': '%.5f' % t_exact, 'N': L(N), 'UNITS': '{:,.1f}'.format(N / C), 'MEM_LOG2': '%.3f' % mem_log2, 'MEM_BYTES': L(mem_bytes),
        'MEM_PEN': '%.3f' % mem_pen, 'SCORE': '%.5f' % score, 'CENTRE': centre, 'TRIALS': str(TRIALS), 'TRIAL_TABLE': TRIAL_TABLE, 'LASTC': str(lastc), 'DIGEST': digest, 'LINE': '0',
        'GCD_OBS': L(agg[keys[4]]['total']), 'LEDGER_TABLE': '\n'.join(rows), 'LEDGER_PY': LEDGER_PY, 'T_ADD': L(tm.group(1)), 'T_SUB': L(tm.group(2)), 'T_MUL': L(tm.group(3)),
        'T_SQR': L(tm.group(4)), 'T_LD': L(tm.group(5)), 'T_ST': L(tm.group(6)), 'T_CTL': L(tm.group(7)), 'T_HC': L(HC), 'T_PERM': L(tm.group(9)), 'NEWTON': L(bd.group(1)),
        'PREFIX': L(bd.group(3)), 'PER_STEP': L(bd.group(7)), 'PER_STEP_ARITH': L(bd.group(8)), 'POW_ARITH': L(agg[keys[3]]['arith']),
        'STAGE_PEAKS': '; '.join('%s %s' % (labels[k].split(':')[0], L(agg[k]['peak'])) for k in keys), 'HEAP_PEAK': L(HEAP),
        'STATIC_DESC': 'text %s + data %s + bss %s = %s bytes' % (L(int(size[0])), L(int(size[1])), L(int(size[2])), L(static)),
        'FILE_ORDER': ', '.join('`%s`' % f for f in SRC_FILES), 'APPENDIX': appendix(), 'PROBE_BOUND': L(PROBE_BOUND)}
for key, val in repl.items():
    t = t.replace('@@%s@@' % key, val)
left = re.findall(r'@@[A-Z0-9_]+@@', t)
assert not left, left
bad = [ch for ch in t if ord(ch) >= 128]
assert not bad, bad[:5]
stale = [s for s in ('39062', '78125', '98304', ' 237', 'C(1)', 'single.c', 'split.c', 'ntt_a3', 'r = 1') if s in t.replace(repl['APPENDIX'], '')]
open(os.path.join(OUT, 'proof.md'), 'w', newline='\n').write(t)
print('stale tokens in proof text:', stale)
lines = t.split('\n')


def ln(prefix):
    for i, l in enumerate(lines, 1):
        if l.startswith(prefix):
            return i
    raise KeyError(prefix)


claim = {"schema_version": 3, "submission_state": "ready", "target_profile": "poseidon-orchard-r2-prefix-v1", "attack_class": "ordinary-collision", "rounds": 2,
         "claim": {"time_log2": time_claim, "time_unit": "target-compressions", "memory_log2_bytes": mem_log2, "preprocessing_log2": 0, "success_probability": 1,
                   "nonuniform_advice_log2_bytes": 0},
         "restrictions": [
             "Applies to the selected target poseidon-orchard-r2-prefix-v1 only (two partial rounds plus the eight fixed full rounds); the construction uses the first two full rounds being skippable on a line and gives no claim for other round counts.",
             "Success probability 1 means: one deterministic procedure (centres c_i = i tried in the order i = 1, 2, 3, ... until the first collision) was executed once from the start on the fixed target and stopped with a collision after %d trials; the time is the executed operation count of that run with every trial charged, failed ones included, and the memory its executed peak. It is not a probability over centres; no start was selected beforehand." % TRIALS],
         "baseline_improved": "poseidon-orchard-r2-nominal-v2", "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
         "heuristics": [{"id": "H1-charging-rules", "role": "supporting",
                         "statement": "The counts of proof.md sections 6 and 7 describe the executed program of proof.md section 9 under the stated rules: 1 per field operation, 1 per element load or store, 1/2 per butterfly and per element of an unrolled loop for loop and address work, 1 per other executed index or control operation, 258 per reduced permutation evaluation, and a register file of 18 words of 256 bits per transform block (16 data words plus two working words: the twiddle operand and the butterfly temporary) as the only register assumption.",
                         "scope": "All stages of the executed run of proof.md section 4 at the target dimensions (m = 195312 for the powering, N = 393216 and N' = 196608 in its transforms, 393216 evaluations of the line).",
                         "extrapolation": "None. The time is the executed total of one run of the shipped source plus a stated bound of %s operations for uncounted self-checks, with every trial charged; no other bound, estimate or run enters it." % L(PROBE_BOUND),
                         "evidence_ids": ["proof:%d-%d" % (ln('### 4.2'), ln('### 4.3') - 1), "proof:%d-%d" % (ln('## 6.'), ln('## 7.') - 1)],
                         "limitations": "The counts are produced by the instrumentation written into the source; the source is part of the proof text and was not run by the organizer. Word-level costs outside the stated rules (cache, bandwidth) are not part of the model."}]}
for r in claim['restrictions']:
    assert len(r) <= 1024
json.dump(claim, open(os.path.join(OUT, 'claim.json'), 'w', newline='\n'), indent=1)
res = dict(time=time_claim, time_exact=t_exact, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, N=N, N_run=N_RUN, trials=TRIALS, last_centre=lastc, heap=HEAP, per_step=int(bd.group(7)))
print(json.dumps(res, indent=1)); json.dump(res, open(os.path.join(EX, 'logs', 'numbers.json'), 'w'))
note = open(os.path.join(HERE, 'note_r2.md')).read()
sub = dict(TRIALS=TRIALS, LASTC=lastc, TIME='%.5f' % time_claim, N=L(N), UNITS='{:,.1f}'.format(N / C), MEM_BYTES=L(mem_bytes), MEM_LOG2='%.3f' % mem_log2, SCORE='%.5f' % score,
           TABLE='\n'.join(rows), TRIAL_TABLE=TRIAL_TABLE, HEAP=L(HEAP), STATIC=L(static), GCD=L(agg[keys[4]]['total']), PER_STEP=L(bd.group(7)), PROBE=L(PROBE_BOUND))
for k, v in sub.items():
    note = note.replace('@@%s@@' % k, str(v))
assert not re.findall(r'@@[A-Z_]+@@', note) and all(ord(c) < 128 for c in note) and len(note.encode()) >= 5 * 1024, len(note.encode())
open(NOTE_OUT, 'w', newline='\n').write(note)
print('note bytes', len(note.encode()))
