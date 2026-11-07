"""Assemble the candidate folder (claim.json, proof.md, certificates/) for target r (env R, default 2) from
logs/ledger_r<R>.txt (one verbose run), logs/bound_gcd_r<R>.txt, logs/bound_root.txt, logs/size_r<R>.txt, data/sample_r<R>.json and data/collisions_r<R>.json.
Every number in proof.md, claim.json and submission-note.md is computed here.  usage: R=1 NCEN=4 python3 build_package.py"""
import json, math, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
R = int(os.environ.get('R', '2'))
NCEN = int(os.environ.get('NCEN', '4'))
FIXED = int(os.environ.get('FIXED_LINE', '0'))   # 1: every centre uses line 0
OUT = os.path.join(HERE, 'pkg_stage_r%d' % R)
LEDGER = os.path.join(HERE, 'logs', 'ledger_r%d.txt' % R)
C = 216 + 21 * R
DEGCAP = 16
SHIFTS = 40
STACK, ALLOC = 65536, 4096
FINAL_ALLOW = 200_000          # sqrt + back-map + 2 reference hashes (success path only), measured below 40,000
NL = chr(10)


def L(x):
    return '{:,}'.format(x)


def ceil3(x):
    return math.ceil(x * 1000) / 1000


def wilson_lo(k, n, z):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d


SRC_FILES = ['lean_attack.c', 'budgets.h', 'attack.h', 'common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'ntt.c', 'ntt_kern.h', 'gen_kern.py', 'poly.c', 'loop.c', 'lean.c', 'line.c',
             'euclid.c', 'hgcd.h', 'hgcd.c', 'bound_gcd.c', 'bound_root.c', 'build.sh', 'bound.sh']


def appendix():
    out = []
    for fn in SRC_FILES:
        body = open(os.path.join(HERE, fn), newline='').read().replace(chr(13) + NL, NL)
        lang = 'python' if fn.endswith('.py') else ('bash' if fn.endswith('.sh') else 'c')
        out.append('### ' + fn + NL + NL + '```' + lang + NL + body.rstrip(NL) + NL + '```' + NL)
    return NL.join(out)


# ---- dimensions
m = (5 ** (6 + R) - 1) // 2
NA = 2
while 3 * (1 << NA) < 2 * m - 1:
    NA += 1
NN = 3 * (1 << NA)
NPA = 2
while 3 * (1 << NPA) < m + 1:
    NPA += 1
NP = 3 * (1 << NPA)
H, HA = None, None
for a in range(2, 40):
    if (1 << a) >= m + 1:
        H, HA = 1 << a, '%d' % a
        break
    if 3 * (1 << a) >= m + 1:
        H, HA = 3 * (1 << a), '%d' % a
        break
H_is3 = (H % 3 == 0)
TWN = 1 << (NA - 1)
VBITS = 1
while (1 << (VBITS + 1)) <= m:
    VBITS += 1
VBITS += 1
FD = {1: ['0x1c66a426cd2d5ec686ea41cae3a27d49c8724fffa0bc4f305029be8b2cce93c3', '0x23f4f4090b603b7edbc59c1e6873df7a90d68316f73ac9517f55080764cf3905', '0x191734549b1df57af01548d1bb07d507b21fdd533a2ab8e07e0dc05e02cd900e'],
      2: ['0x13f08536819885e275e9b4b9c9c3aaaf453220a766fbe69710da897c392caa6f', '0x11f8139dcb1fab1cbfae6318d7e57bfb468080178d66cbacb1f5b30ad9a1af52', '0x059327f399f3c2fc13bdc7839b8ef36934b7f580a288ee4661c29a5988800169']}[R]
partial_idx = [4 + i for i in range(R)]
PARTIAL_LIST = ', '.join(str(i) for i in partial_idx)
PARTIAL_WORDS = ('one partial round %s' % partial_idx[0]) if R == 1 else ('%s partial rounds %d-%d' % ({2: 'two', 3: 'three'}.get(R, str(R)), partial_idx[0], partial_idx[-1]))
LAYERS = {1: 'seven', 2: 'eight'}[R]

shutil.rmtree(OUT, ignore_errors=True)
subprocess.run([sys.executable, '-B', os.path.join(HERE, 'make_experiment.py'), OUT, '16', 'noexp'], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, R=str(R)))
N_CERT = len(json.load(open(os.path.join(OUT, 'certificates', 'manifest.json')))['certificates'])

# ---- ledger run
txt = open(LEDGER).read()
init = re.search(r'^INIT arith=(\d+) other=(\d+) total=(\d+)', txt, re.M)
init_tot = int(init.group(3))
blocks = txt.split('CENTRE ')[1:]
LEDGER_CENTRES = len(blocks)


def stages(block):
    out = []
    for mm in re.finditer(r'^\s{2}(\S.*?)\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+)\s+([\d.]+)s', block, re.M):
        out.append((mm.group(1), int(mm.group(2)), int(mm.group(3)), int(mm.group(4))))
    return out


st0 = dict((n, (a, o, t)) for n, a, o, t in stages(blocks[0]))
pk = re.findall(r'^\s{2}(\S.*?)\s+arith=.*?peak=(\d+)\s*$', blocks[0], re.M)
stage_peaks = '; '.join('%s %s' % (n.split(' (')[0], L(int(v))) for n, v in pk)
rows = ['| stage | arith | other | total | data-dependent |', '|---|---:|---:|---:|---|']
rows.append('| init: twiddle table `rho^j` (%s entries), roots of unity (once per run) | %s | %s | %s | no |' % (L(TWN), L(int(init.group(1))), L(int(init.group(2))), L(init_tot)))
pre = 0
for key, label in [('line_setup', 'line setup (constants of the line, 1 inversion)'), ('random centre', 'random centre'),
                   ('build g', 'B: %s line evaluations (units) + inverse NTT %s + normalisation' % (L(2 * H), L(H))),
                   ('S^((p-1)/2) mod g', 'C: S^((p-1)/2) mod g (lean schedule)')]:
    a, o, t = st0[key]
    pre += t
    rows.append('| %s | %s | %s | %s | no |' % (label, L(a), L(o), L(t)))

# ---- derived budgets
bg = open(os.path.join(HERE, 'logs', 'bound_gcd_r%d.txt' % R)).read()
mb = re.search(r'BOUND_D r=\d+ m=(\d+) derived_total=(\d+) extra=(\d+) maxgap=(\d+)', bg)
DERIVED_D, EXTRA_D, MAXGAP_D = int(mb.group(2)), int(mb.group(3)), int(mb.group(4))
BUDGET_GCD = math.ceil((DERIVED_D + EXTRA_D) * 1.10 / 1_000_000) * 1_000_000
GAP_GCD_BOUND = math.ceil(MAXGAP_D * 1.25 / 1_000_000) * 1_000_000
W_SHIFT = int(re.search(r'cost=(\d+)', open(os.path.join(HERE, 'logs', 'bound_root.txt')).read()).group(1))
BUDGET_ROOT = NCEN * SHIFTS * W_SHIFT
open(os.path.join(HERE, 'budgets_r%d.txt' % R), 'w').write('%d %d\n' % (BUDGET_GCD, BUDGET_ROOT))
ga, go, gt = st0['gcd(g, S^h-1) (half-gcd)']
rows.append('| D: gcd(g, R-1) (half-gcd), as observed in the ledger run (includes the scan for the degree of R-1) | %s | %s | %s | yes: halt budget %s |' % (L(ga), L(go), L(gt), L(BUDGET_GCD)))
rows.append('| E: root finding (deg G <= %d), at most %d shifts per centre | - | - | one shift costs at most %s | yes: halt budget %s in total |' % (DEGCAP, SHIFTS, L(W_SHIFT), L(BUDGET_ROOT)))
rows.append('| F, G: sqrt, 6 powers by e, 2 reference hashes (success path only) | - | - | about 40,000 observed | allowance %s |' % L(FINAL_ALLOW))
gaps = re.search(r'^GAPS gcd=(\d+) root=(\d+)', txt, re.M)
real_gap_d = int(gaps.group(1))
assert real_gap_d <= GAP_GCD_BOUND, (real_gap_d, GAP_GCD_BOUND)
assert gt <= BUDGET_GCD, (gt, BUDGET_GCD)
per_centre_budget = pre + BUDGET_GCD + GAP_GCD_BOUND
worst = init_tot + NCEN * per_centre_budget + BUDGET_ROOT + W_SHIFT + FINAL_ALLOW
one = init_tot + per_centre_budget + SHIFTS * W_SHIFT + W_SHIFT + FINAL_ALLOW
t_exact, t_one = math.log2(worst / C), math.log2(one / C)
time_claim, time_one = ceil3(t_exact), ceil3(t_one)
LEDGER_PY = NL.join([
    "from math import ceil, log2",
    "C = %d" % C,
    "init = %d" % init_tot,
    "line, rnd, build, power = %d, %d, %d, %d" % tuple(st0[k][2] for k in ('line_setup', 'random centre', 'build g', 'S^((p-1)/2) mod g')),
    "d_budget, d_gap = %d, %d" % (BUDGET_GCD, GAP_GCD_BOUND),
    "e_budget, e_gap, fg, centres = %d, %d, %d, %d" % (BUDGET_ROOT, W_SHIFT, FINAL_ALLOW, NCEN),
    "per_centre = line + rnd + build + power + d_budget + d_gap",
    "N = init + centres * per_centre + e_budget + e_gap + fg",
    "print('N =', format(N, ','))",
    "print('units =', round(N / C, 1))",
    "print('time_log2 =', '%.5f' % log2(N / C), ' claimed', ceil(log2(N / C) * 1000) / 1000)"])

# ---- memory
summ = re.search(r'SUMMARY .*heap_peak=(\d+)', txt)
heap = int(summ.group(1))
size = open(os.path.join(HERE, 'logs', 'size_r%d.txt' % R)).read().split(NL)[1].split()
static = int(size[0]) + int(size[1]) + int(size[2])
mem_bytes = heap + static + STACK + ALLOC
mem_log2 = ceil3(math.log2(mem_bytes))
mem_pen = round(max(0, mem_log2 - 20), 3)
score = round(time_claim + mem_pen, 3)
tabrows = [('twiddle table `rho^j`, `j < 2^%d`' % (NA - 1), TWN), ('`Y` (transform buffer, `3 * 2^%d`)' % NA, NN), ('`tmp` (one transform row, `2^%d`)' % NA, 1 << NA),
           ('`MU`', m - 1), ('`g`', m + 1), ('`F` (fold / result)', m)]
MEM_TABLE = NL.join(['| item | elements | bytes |', '|---|---:|---:|'] + ['| %s | %d | %d |' % (n, e, 32 * e) for n, e in tabrows])
stage_c_sum = sum(32 * e for _, e in tabrows)
types = dict(re.findall(r'(\w+)=(\d+)', re.search(r'^TYPES (.*)$', txt, re.M).group(1)))
bm = re.search(r'newton total=(\d+) arith=(\d+) \| prefix\+scale total=(\d+) \| loop steps=(\d+) total=(\d+) arith=(\d+) per-step total=(\d+) arith=(\d+)', txt)

# ---- success sample
S = json.load(open(os.path.join(HERE, 'data', 'sample_r%d.json' % R)))
Z = 2.576
perline = []
for j in ([0] if FIXED else range(3)):
    k, n = S['by_j'][str(j)]
    perline.append((j, k, n, wilson_lo(k, n, 1.96), wilson_lo(k, n, Z)))
PMIN = min(x[4] for x in perline)
PMIN_LINE = [x[0] for x in perline if x[4] == PMIN][0]
PRUN = 1 - (1 - PMIN) ** NCEN
PCLAIM = math.floor(PRUN * 100) / 100
assert PCLAIM >= 0.39 or os.environ.get('ALLOW_LOW'), PCLAIM
PERLINE_TABLE = NL.join(['| line j | successes | executions | success fraction | lower limit, z = 1.96 | lower limit, z = 2.576 (used) |', '|---:|---:|---:|---:|---:|---:|'] +
                        ['| %d | %d | %d | %.3f | %.4f | %.4f |' % (j, k, n, k / n, l1, l2) for j, k, n, l1, l2 in perline])

repl = {
    'R': str(R), 'C': str(C), 'EXPO': str(6 + R), 'DEG': str(5 ** (6 + R)), 'M': str(m), 'NN': str(NN), 'NA': str(NA), 'NP': str(NP), 'NPA': str(NPA), 'H': str(H), 'HA': HA, 'H2': str(2 * H), 'TWN': str(TWN),
    'VBITS': str(VBITS), 'FD0': FD[0], 'FD1': FD[1], 'FD2': FD[2], 'PARTIAL_LIST': PARTIAL_LIST, 'PARTIAL_WORDS': PARTIAL_WORDS, 'LAYERS': LAYERS,
    'NCEN': str(NCEN), 'NCEN_M1': str(NCEN - 1), 'DEGCAP': str(DEGCAP), 'N_CERT': str(N_CERT),
    'LEDGER_PY': LEDGER_PY, 'APPENDIX': appendix(),
    'TIME_LOG2': '%.3f' % time_claim, 'TIME_LOG2_ONE': '%.3f' % time_one, 'TIME_LOG2_EXACT': '%.5f' % t_exact,
    'MEM_LOG2': '%.3f' % mem_log2, 'MEM_BYTES': L(mem_bytes), 'MEM_PEN': '%.3f' % mem_pen, 'SCORE': '%.3f' % score,
    'LEDGER_TABLE': NL.join(rows),
    'WORST_FORMULA': 'init + %d x (line + random + B + C + D budget + D gap bound) + E budget + E gap + F,G allowance = %s + %d x %s + %s + %s + %s' % (NCEN, L(init_tot), NCEN, L(per_centre_budget), L(BUDGET_ROOT), L(W_SHIFT), L(FINAL_ALLOW)),
    'WORST_TOTAL': L(worst), 'WORST_UNITS': '{:,.1f}'.format(worst / C), 'ONE_TOTAL': L(one), 'LEDGER_CENTRES': str(LEDGER_CENTRES),
    'T_ADD': L(int(types['add'])), 'T_SUB': L(int(types['sub'])), 'T_MUL': L(int(types['mul'])), 'T_SQR': L(int(types['sqr'])), 'T_LD': L(int(types['ld'])),
    'T_ST': L(int(types['st'])), 'T_CTL': L(int(types['ctl'])), 'T_RND': L(int(types['rnd'])), 'T_PERM': L(int(types['perm'])),
    'NEWTON': L(int(bm.group(1))), 'PREFIX': L(int(bm.group(3))), 'STEPS': bm.group(4), 'PER_STEP': L(int(bm.group(7))), 'PER_STEP_ARITH': L(int(bm.group(8))),
    'MEM_TABLE': MEM_TABLE, 'STAGE_PEAKS': stage_peaks, 'HEAP_PEAK': L(heap), 'SCALAR_BYTES': L(heap - stage_c_sum),
    'STATIC_DESC': 'text %s + data %s + bss %s = %s bytes' % (L(int(size[0])), L(int(size[1])), L(int(size[2])), L(static)),
    'BUDGET_GCD': L(BUDGET_GCD), 'BUDGET_ROOT': L(BUDGET_ROOT), 'GAP_GCD_BOUND': L(GAP_GCD_BOUND), 'W_SHIFT': L(W_SHIFT),
    'DERIVED_D': L(DERIVED_D), 'EXTRA_D': L(EXTRA_D), 'MAXGAP_D': L(MAXGAP_D),
    'LINE_EXPR': ('line j = 0' if FIXED else 'line j = k mod 3'), 'LINE_RULE': ('every centre works on line 0' if FIXED else 'centre `k` works on line `j = k mod 3`'),
    'PMIN_WORDS': ('the lower limit of line 0, the only line the run uses' if FIXED else 'the smallest of the three per-line lower limits of section 8, since the run uses all three lines'),
    'LINES_USED': ('the run uses line 0 only' if FIXED else 'the run uses the three lines in turn'),
    'SAMPLE_DESC': S['desc'], 'PERLINE_TABLE': PERLINE_TABLE, 'PMIN': '%.4f' % PMIN, 'PMIN_LINE': str(PMIN_LINE), 'PRUN': '%.4f' % PRUN, 'PCLAIM': '%.2f' % PCLAIM,
}
t = open(os.path.join(HERE, 'proof_template.md')).read().replace(chr(13) + NL, NL)
for k, v in repl.items():
    t = t.replace('@@%s@@' % k, v)
left = re.findall(r'@@[A-Z0-9_]+@@', t)
assert not left, left
bad = [ch for ch in t if ord(ch) >= 128]
assert not bad, bad[:5]
open(os.path.join(OUT, 'proof.md'), 'w', newline=NL).write(t)
lines = t.split(NL)


def ln(prefix):
    for i, l in enumerate(lines, 1):
        if l.startswith(prefix):
            return i
    raise KeyError(prefix)


s2, s3, s4, s41, s42, s43, s44, s5, s6, s7, s8, s9 = (ln(p) for p in ['## 2.', '## 3.', '## 4.', '### 4.1', '### 4.2', '### 4.3', '### 4.4', '## 5.', '## 6.', '## 7.', '## 8.', '## 9.'])
claim = {
    "schema_version": 3, "submission_state": "ready", "target_profile": "poseidon-orchard-r%d-prefix-v1" % R, "attack_class": "ordinary-collision", "rounds": R,
    "claim": {"time_log2": time_claim, "time_unit": "target-compressions", "memory_log2_bytes": mem_log2,
              "preprocessing_log2": ceil3(math.log2(init_tot / C)), "success_probability": PCLAIM, "nonuniform_advice_log2_bytes": 0},
    "restrictions": [
        "Applies to the selected target poseidon-orchard-r%d-prefix-v1 only (%s plus the eight fixed full rounds); the construction relies on the first two full rounds being skippable on a line and gives no claim for other round counts." % (R, PARTIAL_WORDS),
        "The run is probabilistic: at most %d independent centres on %s; the claimed success probability is for the whole run, with the implemented halts of proof.md section 4 counted as failures." % (NCEN, "line 0" if FIXED else "the three lines in turn")],
    "baseline_improved": "poseidon-orchard-r%d-nominal-v2" % R,
    "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
    "heuristics": [
        {"id": "H1-per-line-success-rate", "role": "score-critical",
         "statement": "For each line j used by the run, one centre c uniform in [0, 2^254) ends with a verified output without a halt with probability at least L_j, where L_j is the Wilson lower limit (z = 2.576) of the measured success fraction of the program on that line; the centres of a run are independent. The smallest limit is %.4f, so a run of %d centres succeeds with probability at least %.4f (claimed %.2f)." % (PMIN, NCEN, PRUN, PCLAIM),
         "scope": "The program of proof.md section 4 at the selected target, centres on %s, algorithmic random words modelled as independent uniform; every halt of the program active in every counted execution." % ("line 0" if FIXED else "lines 0, 1, 2 in turn"),
         "extrapolation": "From the per-line executions of proof.md section 8 to the true per-line success probability, by the stated confidence limit only. No model of the number of roots of the odd-part polynomial is used.",
         "evidence_ids": ["proof:%d-%d" % (s8, s9 - 1)],
         "limitations": "A statistical limit, not a proof: each line's limit holds with confidence about 99.5 percent, the samples come from a deterministic generator, and the sample sizes are small (about 20 executions per line); the certificates show only that found roots yield collisions and say nothing about their frequency."},
        {"id": "H2-charging-rules", "role": "supporting",
         "statement": "The counts of proof.md sections 6 and 7 are the totals of an instrumented execution of the program whose complete source is in proof.md section 10: 1 per field operation, 1 per element load or store, every executed integer, comparison, branch, shift and address operation charged where it occurs, %d per reduced permutation evaluation of stage B, and 16-element register blocks as the only register assumption." % C,
         "scope": "All stages of the program of proof.md section 4 at the target dimensions (m = %d, N = %d, N' = %d, H = %d)." % (m, NN, NP, H),
         "extrapolation": "None beyond the executed dimensions; the worst case for %d centres is formed from the measured data-independent stages and the halt budgets of the data-dependent stages." % NCEN,
         "evidence_ids": ["proof:%d-%d" % (s41, s42 - 1), "proof:%d-%d" % (s6, s7 - 1)],
         "limitations": "Word-level costs outside the stated rules (cache, bandwidth) are not part of the model; the charges are written next to the statements of the source and are not an independent count of machine instructions."},
        {"id": "H3-stage-budgets", "role": "supporting",
         "statement": "Stages D and E stop the program when their work exceeds the halt budgets of proof.md section 4.4 (%s and %s operations); the work between two checks is bounded by %s and %s operations." % (L(BUDGET_GCD), L(BUDGET_ROOT), L(GAP_GCD_BOUND), L(W_SHIFT)),
         "scope": "Stages D and E of proof.md section 4.",
         "extrapolation": "None: the budgets are enforced by the executed program, and a halt is a failure counted in H1. The budgets are derived by running the shipped node procedures on the sizes of the normal-case recursion tree (bound_gcd.c, bound_root.c).",
         "evidence_ids": ["proof:%d-%d" % (s44, s5 - 1)],
         "limitations": "The gap bound between two checks is measured on the shipped procedures at the largest node sizes with all checks active, and the factor 1.25 and the 10 percent budget margin are design choices."}]}
json.dump(claim, open(os.path.join(OUT, 'claim.json'), 'w', newline=NL), indent=1)
for h in claim['heuristics']:
    for k in ('statement', 'scope', 'extrapolation', 'limitations'):
        assert len(h[k]) <= 4096, (h['id'], k)
for r in claim['restrictions']:
    assert len(r) <= 1024
summary = dict(R=R, time=time_claim, time_one=time_one, mem_bytes=mem_bytes, mem_log2=mem_log2, score=score, worst=worst, per_centre_budget=per_centre_budget,
               budget_gcd=BUDGET_GCD, budget_root=BUDGET_ROOT, gap=GAP_GCD_BOUND, pmin=PMIN, prun=PRUN, pclaim=PCLAIM, real_gap_d=real_gap_d, gt=gt, heap=heap)
print(json.dumps(summary, indent=1))

# ---- submission note
note = """Orchard Poseidon, r = %(R)d (poseidon-orchard-r%(R)d-prefix-v1): known method, finite ledger from the shipped source, low memory.

Method (not new). On a line in the (nk, rho) input plane the first two full rounds cost no degree, so the digest is a polynomial F(W) of degree 5^%(EXPO)d = %(DEG)d.
For a random centre c, the odd part of F(c+s) - F(c-s) is a polynomial g in S = s^2 of degree %(M)d; each nonzero square root S of g gives the collision W = c +- sqrt(S).
g is built by %(H2)s line evaluations (each charged as one target-compression unit of %(C)d operations) and one inverse NTT of size %(H)s; S^((p-1)/2) mod g is computed with an in-place
NTT schedule that stores no spectra (row-wise operand transforms); gcd(g, S^((p-1)/2) - 1) by half-gcd; root finding on the gcd of degree at most %(DEGCAP)d; square root, back-map and two reference hashes.

Numbers. time_log2 %(TL)s (a run of at most %(NCEN)d centres charged at its halt budgets; one centre: %(TO)s), memory %(MB)s bytes (log2 %(ML)s), normalized cost %(SC)s,
claimed success probability %(PC).2f. %(NC)d verified collisions of the target are included as certificates.

Success probability. Per line, the success fractions of the program with all halts active, and their Wilson lower limits (z = 2.576), are in proof.md section 8 (smallest limit %(PM).4f, line %(PL)d).
%(NCEN)d independent centres give at least 1 - (1 - %(PM).4f)^%(NCEN)d = %(PR).4f. No model of the number of roots of g enters the claim or any budget.

Per-line sample (proof.md section 8):

%(PLT)s

%(SDESC)s

Budgets. Stage D (half-gcd) and stage E (root finding) are halts: the program stops when their charged work exceeds %(BG)s and %(BR)s operations. The stage D budget is the cost of the normal-case recursion tree
(%(DD)s operations, computed by bound_gcd.c from the shipped node procedures at the sizes of each node) plus the scan, plus 10 percent. Stage E: %(NCEN)d x %(SH)d shifts x %(WS)s operations per shift (bound_root.c).
The work between two checks is at most %(GG)s (stage D) and %(WS)s (stage E). A halt is a failure and is counted inside the per-line fractions.

Ledger (primitive operations, C(%(R)d) = %(C)d; full table and rules in proof.md sections 4 and 6):

%(TABLE)s

Worst case for %(NCEN)d centres: %(WF)s = %(WT)s operations = %(WU)s units.

Memory: %(SD)s plus heap peak %(HP)s, stack bound 65,536 B (the run was executed with a 64 KiB stack limit), allocator slack 4,096 B.

%(MEMT)s

Charging rules. Field operations, 256-bit loads and stores, and every executed integer, comparison, branch, shift and address operation are charged 1 each, next to the statement that executes them.
The transform passes are blocks of up to four butterfly layers in a 16-element register block; straight loops are charged 8 per element; the radix-3 stage is charged per element for the loop, the rotation
update, the mask lookup and the addresses. The complete source of the executed program (section 10 of proof.md) is shipped, including the generator of the kernel header.

Heuristics declared in claim.json: H1 (score-critical): per-line success fractions bound the per-line success probability, centres independent; H2 (supporting): the charging rules describe the executed program;
H3 (supporting): the stage budgets of proof.md section 4.4 are enforced halts.

Limits. The success claim is a statistical lower limit from about 20 executions per line, not a proof; the leading coefficient of the digest polynomial, the interpolation and the collision criterion are exact and
verified by the executed program (collisions produced and checked by the organizer's hash). No Python experiment is declared because the organizer's experiment runner sizes the digest with digest(b"") and the Orchard
digest rejects the empty message. Cache and bandwidth effects are outside the cost model.
""" % dict(R=R, EXPO=6 + R, DEG=5 ** (6 + R), M=m, H2=L(2 * H), H=L(H), C=C, DEGCAP=DEGCAP, TL='%.3f' % time_claim, NCEN=NCEN, TO='%.3f' % time_one, MB=L(mem_bytes), ML='%.3f' % mem_log2, SC='%.3f' % score,
           PC=PCLAIM, NC=N_CERT, PM=PMIN, PL=PMIN_LINE, PR=PRUN, BG=L(BUDGET_GCD), BR=L(BUDGET_ROOT), DD=L(DERIVED_D), SH=SHIFTS, WS=L(W_SHIFT), GG=L(GAP_GCD_BOUND), TABLE=NL.join(rows),
           WF=repl['WORST_FORMULA'], PLT=PERLINE_TABLE, SDESC=S['desc'], WT=L(worst), WU=repl['WORST_UNITS'], SD=repl['STATIC_DESC'], HP=L(heap), MEMT=MEM_TABLE)
assert len(note.encode()) >= 5120, len(note.encode())
open(os.path.join(OUT, 'submission-note.md'), 'w', newline=NL).write(note)
print('note bytes', len(note.encode()))
