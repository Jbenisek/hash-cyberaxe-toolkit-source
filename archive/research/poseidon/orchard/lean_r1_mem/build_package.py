"""Assemble the candidate folder (claim.json, proof.md, certificates/, experiments/) in pkg_stage/ from the ledger run,
the campaign statistics and the stored collisions.  Every number in proof.md and claim.json is computed here."""
import json, math, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pkg_stage')
LEDGER = os.environ.get('LEDGER', os.path.join(HERE, 'logs', 'final_ledger.txt'))
BUDGET_GCD, BUDGET_ROOT, GCD_SCAN = 800_000_000, 10_000_000, 100_000
FINAL_ALLOW = 200_000          # sqrt + back-map + 2 reference hashes, twice (success path only): measured about 18,400 each
C = 237
STACK, ALLOC = 65536, 4096


def L(x):
    return '{:,}'.format(x)


def extract(fn, sig):
    src = open(os.path.join(HERE, fn)).read().split(chr(10))
    for i, l in enumerate(src):
        if re.match(sig, l):
            j = i
            while not src[j].startswith('}'):
                j += 1
            return chr(10).join(src[i:j + 1])
    raise KeyError(sig)


def appendix():
    parts = [('lean.c', r'static void newton_lean', 'lean.c: Newton iteration for MU (row-wise products)'), ('lean.c', r'void powx_lean', 'lean.c: stage C, the lean powering loop'),
             ('ntt.c', r'static inline void blk_fwd', 'ntt.c: one 16-element register block (forward layers)'), ('ntt.c', r'static void pass_fwd', 'ntt.c: one forward pass'),
             ('ntt.c', r'static void pass_fused', 'ntt.c: last forward pass + pointwise product + first inverse pass'),
             ('ntt.c', r'static void stageA_row', 'ntt.c: one row of the radix-3 stage of the second operand'), ('ntt.c', r'void conv_mulc_otf', 'ntt.c: product with a row-wise generated operand'),
             ('ntt.c', r'void conv_sum_otf', 'ntt.c: sum of products with row-wise generated operands (used by the half-gcd)'),
             ('hgcd.c', r'static void apply_inv', 'hgcd.c: application of the inverse matrix'), ('hgcd.c', r'void hgcd\(', 'hgcd.c: half-gcd recursion'),
             ('hgcd.c', r'size_t poly_gcd_fast_own', 'hgcd.c: gcd driver (inputs given away)'),
             ('line.c', r'void tail_eval', 'line.c: one line evaluation F_j(W) (stage B, charged as one unit)'), ('line.c', r'void build_g', 'line.c: stage B')]
    out = []
    for fn, sig, title in parts:
        out.append('### ' + title + chr(10) + chr(10) + '```c' + chr(10) + extract(fn, sig) + chr(10) + '```' + chr(10))
    return chr(10).join(out)


shutil.rmtree(OUT, ignore_errors=True)
subprocess.run([sys.executable, '-B', os.path.join(HERE, 'make_experiment.py'), OUT, '16', 'noexp'], check=True, stdout=subprocess.DEVNULL)
N_CERT = len(json.load(open(os.path.join(OUT, 'certificates', 'manifest.json')))['certificates'])
txt = open(LEDGER).read()

init = re.search(r'^INIT arith=(\d+) other=(\d+) total=(\d+)', txt, re.M)
init_tot = int(init.group(3))
blocks = txt.split('CENTRE ')[1:]


def stages(block):
    out = []
    for m in re.finditer(r'^\s{2}(\S.*?)\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+)\s+([\d.]+)s', block, re.M):
        out.append((m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))))
    return out


st0 = dict((n, (a, o, t)) for n, a, o, t in stages(blocks[0]))
pk = re.findall(r'^\s{2}(\S.*?)\s+arith=.*?peak=(\d+)\s*$', blocks[0], re.M)
stage_peaks = '; '.join('%s %s' % (n.split(' (')[0], L(int(v))) for n, v in pk) if pk else 'not recorded in this log'
det = [('line_setup', 'line setup (constants of the line, 1 inversion)'), ('random centre', 'random centre'),
       ('build g', 'B: 98304 line evaluations (units) + inverse NTT 49152 + normalisation'),
       ('S^((p-1)/2) mod g', 'C: S^((p-1)/2) mod g (lean schedule)')]
rows = ['| stage | arith | other | total | data-dependent |', '|---|---:|---:|---:|---|']
rows.append('| init: twiddle table `rho^j` (16384 entries), roots of unity (once per run) | %s | %s | %s | no |' % (L(int(init.group(1))), L(int(init.group(2))), L(init_tot)))
pre = 0
for key, label in det:
    a, o, t = st0[key]
    pre += t
    rows.append('| %s | %s | %s | %s | no |' % (label, L(a), L(o), L(t)))
ga, go, gt = st0['gcd(g, S^h-1) (half-gcd)']
rows.append('| D: gcd(g, R-1) (half-gcd), as observed in this run (includes the scan for the degree of R-1, 78,126 ops) | %s | %s | %s | yes: budget %s |' % (L(ga), L(go), L(gt), L(BUDGET_GCD)))
rows.append('| E: root finding (deg G <= 8), at most 40 shifts per centre | - | - | 5 (one root) to 761,102 (320 planted tests, d <= 8) | yes: budget %s in total |' % L(BUDGET_ROOT))
rows.append('| F, G: sqrt, 6 powers by e, 2 reference hashes (success path only) | - | - | about 18,300 observed | allowance %s for two executions |' % L(FINAL_ALLOW))
gaps = re.search(r'^GAPS gcd=(\d+) root=(\d+)', txt, re.M)
GAP_GCD = int(gaps.group(1))
GAP_GCD_BOUND = math.ceil(GAP_GCD * 1.25 / 1_000_000) * 1_000_000
GAP_ROOT_BOUND = 1_000_000
per_centre_budget = pre + BUDGET_GCD + GAP_GCD_BOUND + GCD_SCAN
worst = init_tot + 2 * per_centre_budget + BUDGET_ROOT + GAP_ROOT_BOUND + FINAL_ALLOW
one = init_tot + per_centre_budget + BUDGET_ROOT + GAP_ROOT_BOUND + FINAL_ALLOW
t_exact, t_one = math.log2(worst / C), math.log2(one / C)

LEDGER_PY = chr(10).join([
 "from math import ceil, log2",
 "C = 237",
 "init = %d" % init_tot,
 "line, rnd, build, power = %d, %d, %d, %d" % tuple(st0[k][2] for k in ('line_setup', 'random centre', 'build g', 'S^((p-1)/2) mod g')),
 "d_budget, d_gap, scan = %d, %d, %d" % (BUDGET_GCD, GAP_GCD_BOUND, GCD_SCAN),
 "e_budget, e_gap, fg = %d, %d, %d" % (BUDGET_ROOT, GAP_ROOT_BOUND, FINAL_ALLOW),
 "per_centre = line + rnd + build + power + d_budget + d_gap + scan",
 "N = init + 2 * per_centre + e_budget + e_gap + fg",
 "print('N =', format(N, ','))",
 "print('units =', round(N / C, 1))",
 "print('time_log2 =', '%.5f' % log2(N / C), ' claimed', ceil(log2(N / C) * 1000) / 1000)"])



def ceil3(x):
    return math.ceil(x * 1000) / 1000


time_claim, time_one = ceil3(t_exact), ceil3(t_one)
summ = re.search(r'SUMMARY .*heap_peak=(\d+)', txt)
heap = int(summ.group(1))
size = open(os.path.join(HERE, 'logs', 'size.txt')).read().split('\n')[1].split()
static = int(size[0]) + int(size[1]) + int(size[2])
mem_bytes = heap + static + STACK + ALLOC
mem_log2 = ceil3(math.log2(mem_bytes))
mem_pen = round(max(0, mem_log2 - 20), 3)
score = round(time_claim + mem_pen, 3)
types = dict(re.findall(r'(\w+)=(\d+)', re.search(r'^TYPES (.*)$', txt, re.M).group(1)))
stats = json.load(open(os.path.join(HERE, 'data', 'stats.json')))
bd = txt
bm = re.search(r'newton total=(\d+) arith=(\d+) \| prefix\+scale total=(\d+) \| loop steps=(\d+) total=(\d+) arith=(\d+) per-step total=(\d+) arith=(\d+)', bd)
hist = ', '.join('%s root%s: %d' % (k, '' if k == '1' else 's', v) for k, v in sorted(stats['degG_histogram'].items(), key=lambda kv: int(kv[0])))
vals = stats['all_values']
gcd_vals = stats['gcd_values']
def xcheck_text(per_step_arith):
    def dense(a):
        n = 2 ** a
        mults = 3 * (a * n // 2 - (n - 1))
        adds = 3 * a * n
        stage_a = 8 * n
        return mults, adds, stage_a, mults + adds + stage_a
    m15, a15, s15, t15 = dense(15)
    m14, a14, s14, t14 = dense(14)
    sq = 2 * t15 + 98304
    quo = 3 * t15 + 98304
    qg = 3 * t14 + 49152
    misc = 2 * 39062 + 2 * 45 * 39062 // 238
    tot = sq + quo + qg + misc
    return (
        'Analytic cross-check of the arithmetic of a step (a reader can recompute it). A dense forward or inverse transform of size 3 * 2^a does, in its three rows of length 2^a, '
        '3 (a 2^(a-1) - (2^a - 1)) multiplications (the butterflies with twiddle index 0 are free) and 3 a 2^a additions or subtractions, and its radix-3 stage 8 * 2^a operations. '
        'For a = 15 this is %s + %s + %s = %s operations, for a = 14 it is %s. A step has a square (forward + inverse at a = 15, plus %s pointwise squarings), '
        'a quotient product (forward of the operand, row-wise forward of MU, inverse: three transforms at a = 15, plus %s pointwise products) and the product with g at a = 14 (three transforms, plus %s pointwise products), '
        'plus about %s operations of folding, subtraction and shifts. Upper estimate: %s + %s + %s + %s = %s arithmetic operations per step, against %s measured; the measured value is lower because the radix-3 stage skips the zero '
        'part of the padded operands and the inverse radix-3 stage computes only the needed outputs.'
        % (L(m15), L(a15), L(s15), L(t15), L(t14), L(98304), L(98304), L(49152), L(misc), L(sq), L(quo), L(qg), L(misc), L(tot), L(per_step_arith)))


repl = {
    'LEDGER_PY': LEDGER_PY,
    'APPENDIX': appendix(),
    'XCHECK': xcheck_text(int(bm.group(8))),
    'TIME_LOG2': '%.3f' % time_claim, 'TIME_LOG2_ONE': '%.3f' % time_one, 'TIME_LOG2_EXACT': '%.5f' % t_exact,
    'MEM_LOG2': '%.3f' % mem_log2, 'MEM_BYTES': L(mem_bytes), 'MEM_PEN': '%.3f' % mem_pen, 'SCORE': '%.3f' % score,
    'LEDGER_TABLE': '\n'.join(rows),
    'WORST_FORMULA': 'init + 2 x (line + random + B + C + D budget + D gap bound + scan) + E budget + E gap bound + F,G allowance = %s + 2 x %s + %s + %s + %s' % (L(init_tot), L(per_centre_budget), L(BUDGET_ROOT), L(GAP_ROOT_BOUND), L(FINAL_ALLOW)),
    'WORST_TOTAL': L(worst), 'WORST_UNITS': '{:,.1f}'.format(worst / C), 'ONE_TOTAL': L(one),
    'N_RUNS': str(stats['n_build_B']), 'MIN_ALL': L(min(vals)), 'MAX_ALL': L(max(vals)), 'MARGIN': L(one - max(vals)),
    'T_ADD': L(int(types['add'])), 'T_SUB': L(int(types['sub'])), 'T_MUL': L(int(types['mul'])), 'T_SQR': L(int(types['sqr'])), 'T_LD': L(int(types['ld'])),
    'T_ST': L(int(types['st'])), 'T_CTL': L(int(types['ctl'])), 'T_RND': L(int(types['rnd'])), 'T_PERM': L(int(types['perm'])),
    'NEWTON': L(int(bm.group(1))), 'PREFIX': L(int(bm.group(3))), 'STEPS': bm.group(4), 'PER_STEP': L(int(bm.group(7))), 'PER_STEP_ARITH': L(int(bm.group(8))),
    'STAGE_PEAKS': stage_peaks, 'HEAP_PEAK': L(heap), 'SCALAR_BYTES': L(heap - 8468544),
    'STATIC_DESC': 'text %s + data %s + bss %s = %s bytes' % (L(int(size[0])), L(int(size[1])), L(int(size[2])), L(static)),
    'N_CENTRES': str(stats['centres']), 'N_A': str(stats['n_build_A']), 'N_B': str(stats['n_build_B']), 'N_SUCC': str(stats['successes']), 'RATE': '%.3f' % stats['rate'],
    'WLO': '%.3f' % stats['wilson95'][0], 'WHI': '%.3f' % stats['wilson95'][1], 'HIST': hist,
    'BUDGET_GCD': L(BUDGET_GCD), 'BUDGET_ROOT': L(BUDGET_ROOT), 'GAP_GCD': L(GAP_GCD), 'GAP_GCD_BOUND': L(GAP_GCD_BOUND), 'GAP_ROOT_BOUND': L(GAP_ROOT_BOUND), 'GCD_MIN': L(min(gcd_vals)), 'GCD_MAX': L(max(gcd_vals)), 'N_CERT': str(N_CERT),
}
t = open(os.path.join(HERE, 'proof_template.md')).read()
for k, v in repl.items():
    t = t.replace('@@%s@@' % k, v)
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


s2, s3, s4, s41, s42, s5, s6, s7, s8, s9 = (ln(p) for p in ['## 2.', '## 3.', '## 4.', '### 4.1', '### 4.2', '## 5.', '## 6.', '## 7.', '## 8.', '## 9.'])
h1, hx, h3, h2 = ln('**H1'), ln('**Halts and caps'), ln('**H3'), ln('**H2')
claim = {
    "schema_version": 3, "submission_state": "ready", "target_profile": "poseidon-orchard-r1-prefix-v1", "attack_class": "ordinary-collision", "rounds": 1,
    "claim": {"time_log2": time_claim, "time_unit": "target-compressions", "memory_log2_bytes": mem_log2,
              "preprocessing_log2": ceil3(math.log2(init_tot / C)), "success_probability": 0.60, "nonuniform_advice_log2_bytes": 0},
    "restrictions": [
        "Applies to the selected target poseidon-orchard-r1-prefix-v1 only (one partial round plus the eight fixed full rounds); the construction relies on the first two full rounds being skippable on a line and gives no claim for other round counts.",
        "The run is probabilistic: at most two independent centres on two different lines; the claimed success probability is for the whole run, with the implemented halts of proof.md section 4 counted as failures."],
    "baseline_improved": "poseidon-orchard-r1-nominal-v2",
    "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
    "heuristics": [
        {"id": "H1-root-count-model", "role": "score-critical",
         "statement": "For a centre c uniform in [0, 2^254) and line j in {0,1,2}, the number K of nonzero squares among the F_p-roots of the monic odd-part polynomial g_c (degree 39062) is Poisson with mean 1/2, independent across centres and lines, so one centre succeeds with probability 1 - exp(-1/2) = 0.3935 and two centres with probability 0.632 (claimed: 0.60, which needs a per-centre probability of only 0.37).",
         "scope": "Odd-part polynomials of the Orchard r = 1 digest along the three lines of proof.md section 2 over the Pallas base field; the program of proof.md section 4 with at most two centres; algorithmic random words modelled as independent uniform.",
         "extrapolation": "From %d complete single-centre executions at the selected target (%d successes) and from earlier toy analogues over a 38-bit prime (degrees 125 to 15625, up to 600,000 centres, rate 0.3937 +- 0.001) to the full field; the target-size sample cannot separate 0.3935 from nearby rates at its width and is used only to support the weaker per-centre bound 0.37." % (stats['centres'], stats['successes']),
         "evidence_ids": ["proof:%d-%d" % (s8, hx - 1)],
         "limitations": "No proof that g_c behaves like a random polynomial for the root count; the toy rates and the target-size rate are measurements, not a bound; the certificates show only that found roots yield collisions and say nothing about their frequency; the random words of the program come from a deterministic generator."},
        {"id": "H2-charging-rules", "role": "supporting",
         "statement": "The counts of proof.md sections 6 and 7 are the totals of an instrumented execution of the described program under the stated rules: 1 per field operation, 1 per element load or store, 4 control operations per 16 elements of a straight loop (12 per 16-element transform block), 237 per reduced permutation evaluation of stage B, and 16-element register blocks as the only register assumption.",
         "scope": "All stages of the program of proof.md section 4 at the target dimensions (m = 39062, N = 98304, N' = 49152, H = 49152).",
         "extrapolation": "None beyond the executed dimensions; the worst case for two centres is formed from the measured data-independent stages and the implemented budgets of the data-dependent stages.",
         "evidence_ids": ["proof:%d-%d" % (s41, s42 - 1), "proof:%d-%d" % (s6, s7 - 1)],
         "limitations": "The instrumented source is not shipped (candidate files are restricted to declared Python experiments), so the totals cannot be recomputed from the package; word-level costs outside the stated rules (cache, address arithmetic beyond the control charges) are not part of the model."},
        {"id": "H3-gcd-budget", "role": "supporting",
         "statement": "The half-gcd stage on (g, R - 1) stays within " + L(BUDGET_GCD) + " charged operations; the stage has this budget as an implemented halt and a halt counts as a failure of the run.",
         "scope": "Stage D of proof.md section 4 for inputs produced by stages B and C.",
         "extrapolation": "From %d executions (stage totals %s to %s) to all inputs; exceeding the budget requires a non-normal remainder sequence (probability about 1/p per step) or a gcd of large degree." % (stats['centres'], L(min(gcd_vals)), L(max(gcd_vals))),
         "evidence_ids": ["proof:%d-%d" % (h3, h2 - 1)],
         "limitations": "Cost concentration is observed and argued, not proved; the budget itself bounds the loss."}]}
json.dump(claim, open(os.path.join(OUT, 'claim.json'), 'w', newline='\n'), indent=1)
for h in claim['heuristics']:
    for k in ('statement', 'scope', 'extrapolation', 'limitations'):
        assert len(h[k]) <= 4096, (h['id'], k)
for r in claim['restrictions']:
    assert len(r) <= 1024
print(json.dumps(dict(time=time_claim, time_one=time_one, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, worst=worst, per_centre_budget=per_centre_budget), indent=1))

note = """Orchard Poseidon, r = 1 (poseidon-orchard-r1-prefix-v1): known method, exact finite ledger, low memory.

Method (not new): on a line in the (nk, rho) input plane the first two full rounds cost no degree, so the digest is a polynomial F(W) of degree 5^7 = 78125.
For a random centre c, the odd part of F(c+s) - F(c-s) is a polynomial g in S = s^2 of degree 39062; each nonzero square root S of g gives the collision W = c +- sqrt(S).
g is built by 98,304 line evaluations (charged as target-compression units) and one inverse NTT of size 49,152; S^((p-1)/2) mod g is computed with an in-place
NTT schedule that stores no spectra (row-wise operand transforms); gcd(g, S^((p-1)/2) - 1) by half-gcd; root splitting, sqrt, back-map and two reference hashes.

Numbers: time_log2 %s (worst-case budget of at most two independent centres; one centre: %s), memory %s bytes (log2 %s), normalized cost %s, claimed success probability 0.60
(0.632 under the Poisson root-count heuristic H1, which is the one score-critical heuristic). %d verified collisions of the target are included as certificates.

What is not shown: the instrumented C source is not shipped (candidate files are limited to declared Python experiments); its executed code is quoted in proof.md section 10.
No Python experiment is declared because the organizer's experiment runner sizes the digest with digest(b"") and the Orchard digest rejects the empty message.
"""
note = note % (repl['TIME_LOG2'], repl['TIME_LOG2_ONE'], repl['MEM_BYTES'], repl['MEM_LOG2'], repl['SCORE'], N_CERT)
note += chr(10) + "Ledger (primitive operations, C(1) = 237; full table and rules in proof.md sections 4 and 6):" + chr(10) + chr(10) + chr(10).join(rows) + chr(10)
note += chr(10) + "Worst case for two centres: " + repl['WORST_FORMULA'] + " = " + repl['WORST_TOTAL'] + " operations = " + repl['WORST_UNITS'] + " units." + chr(10)
note += chr(10) + "Memory: " + repl['STATIC_DESC'] + " plus heap peak " + repl['HEAP_PEAK'] + ", stack bound 65,536 B, allocator slack 4,096 B." + chr(10)
note += chr(10) + "Heuristics declared in claim.json: H1 (score-critical): root count of the odd-part polynomial is Poisson(1/2) (one centre 0.3935, two centres 0.632; claimed 0.60); H2 (supporting): the charging rules describe the executed program; H3 (supporting): the half-gcd stage stays within its implemented budget." + chr(10)
note += chr(10) + "Campaign: " + repl['N_CENTRES'] + " complete single-centre executions at the target, " + repl['N_SUCC'] + " successes (rate " + repl['RATE'] + ", Wilson 95% [" + repl['WLO'] + ", " + repl['WHI'] + "]); every success verified by a big-integer reference and the organizer's hash; root-count histogram " + repl['HIST'] + "." + chr(10)
note += chr(10) + "Limits: the C source is not shipped; the per-element address arithmetic is assumed free (specialised pass kernels with constant strides) and registers are charged as 16-element blocks; the success claim rests on H1 and not on the sample." + chr(10)
hi = t.index("Implemented halts"); hj = t.index("### 4.1")
mi = t.index("| item | elements | bytes |"); mj = t.index("Tracked peak per stage")
note += chr(10) + t[hi:hj] + chr(10) + t[mi:mj] + chr(10)
open(os.path.join(HERE, 'submission-note.md'), 'w', newline='\n').write(note)
