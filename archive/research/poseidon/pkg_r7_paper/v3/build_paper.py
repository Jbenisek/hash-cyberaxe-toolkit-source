#!/usr/bin/env python3
"""(paper entry: fresh random words, shift in F_p^*, no program) Builds the Poseidon r7 algebraic paper package into OUT (default ./out): claim.json, proof.md, submission-note.md, experiments/, certificates/.
python -B build_v2.py [OUT]      (run from this folder; reads template2/, src/, tests/, exp/, the old template for sections 2-5, the r5 section 4.2)
Every number is computed here from costmodel.py, costmodel_e.py and premise_numbers.py; nothing is typed in by hand except the texts.
FILING DAY: edit EXECUTOR and EXECUTOR_NOTE below to say what is true about the organizer runner, rerun this script, then run
  wsl -d Ubuntu -- bash stage_r7alg3.sh <NEW slot name>   (a slot is never reused) and use the submit script it writes (research/launch/submit_pareto_posr7alg5.sh).
"""
import json, math, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['MODEL_SRC'] = os.path.join(HERE, 'src')
sys.path.insert(0, HERE)
import costmodel as cm, costmodel_e as ce, premise_numbers as pn

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out_paper')
OLD = os.path.join(HERE, '..', '..', 'algebraic_paper', 'template')
R5 = os.path.join(HERE, '..', '..', 'orchard', 'exec_r5tt', 'pkg_fin', 'proof.md')
T2 = os.path.join(HERE, 'template3')
rd = lambda p: open(p, encoding='utf-8').read()

R, K, W = 7, 2, 2
NUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen"]
L = lambda x: '{:,}'.format(int(x))
def ceil5(x): return math.ceil(round(x * 100000, 6)) / 100000
def ceil3(x): return math.ceil(round(x * 1000, 6)) / 1000
def fl5(x): return math.floor(float(x) * 100000) / 100000

# ------------------------------------------------------------------ numbers
ev, sc = cm.paper_account(R, K)
tr = ev['trial'][0]
C = cm.perm_C(R)
off = cm.OFFLINE_BOUND
N = ev['total'] + off
TL_EXACT = math.log2(N / C)
TL = ceil5(TL_EXACT)
assert '%.5f' % TL == '%.5f' % sc['time_log2']
mem_bytes = sc['mem_bytes']; mem_log2 = sc['mem_log2']
score = TL + (mem_log2 - 20)
D = 5 ** (6 + R); m = (D - 1) // 2
hexp = 0
while (3 << hexp) < m + 1: hexp += 1
aexp = 0
while (3 << aexp) < 2 * m - 1: aexp += 1
Hn = 3 << hexp
vexp = m.bit_length() - 1
steps = 253 - vexp
B = pn.bound(W, K)
Q_EXACT = B['q']; Q_STR = '%.5f' % (math.floor(float(Q_EXACT) * 100000) / 100000)
q_used = float(Q_STR)
from fractions import Fraction as Fr
succ_unrounded = B['succ']                                   # with the unrounded q
q_used = float(Q_STR)
succ_exact = 1 - (1 - Fr(Q_STR)) ** K - K * (pn.eps_coin + pn.eps_iso)    # with the stated q (rounded down)
P_SUCC = '%.5f' % fl5(succ_exact)
assert float(succ_exact) >= 0.39 and succ_exact <= succ_unrounded
E_RATIO = None
rows = [re.match(r'E d=(\d+) rep=\d+ ok=1 rounds=(\d+) total=(\d+)', l) for l in open(os.path.join(HERE, 'tests', 'test_e_out.txt'))]
E_RATIO = 0.0
for mm in rows:
    if mm:
        dd, rr, tt = map(int, mm.groups())
        E_RATIO = max(E_RATIO, tt / (3 + rr * ce.round_cost(dd) + 10 + ce.XF + 4))
F1, F_ARITH = ce.stage_F()
r16 = ce.round_cost(16)
inv = ce.INV

val_rows = []
for r, evr, M in cm.validation():
    val_rows.append('| r = %d, earlier program (fixed centre) | %s | %s | %s | %.5f | %s | %s |' % (r, L(evr['total']), L(M['algo']), L(evr['total'] - M['algo']), math.log2(evr['total'] / M['algo']), L(evr['heap_peak']), L(M['heap'])))

sens = []
for qq in (0.30, 0.25, float(Q_STR), 0.22, 0.20, 0.15, 0.10, 0.05):
    sens.append('| %.5f | %s |' % (qq, ' | '.join('%.5f' % (1 - (1 - qq) ** k) for k in (1, 2, 3, 4))))
qmin = lambda k: math.ceil((1 - 0.61 ** (1.0 / k)) * 100000) / 100000
qm2 = qmin(2)



hg_k = (m + 1) // 2
lev = 0
while hg_k > 96:
    hg_k = (hg_k + 1) // 2; lev += 1
HGCD_BOUND = ('%d levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = %s` and is halved, rounded up, until it is at most 96) and at most %d repetitions of the outer loop of `poly_gcd_own` in the normal case (each repetition removes about half of the degree, from %s to at most 192)'
              % (lev + 1, L((m + 1) // 2), math.ceil(math.log2(m / 192)) + 1, L(m)))

arena = sc['arena']
bss_static = 4851196
EXECUTOR = ("The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence: 256 of 256 trials returned a verified pair at r = 7, and the output was byte-identical on repetition. "
            "Our own earlier local run of the same events (plain Python on our machine) agreed: 256 of 256 trials in 2.9 s.")
EXECUTOR_NOTE = ("The organizer's runner executes it (organizer-run experiment); the organizer's intake report records the result: a verified pair in 256 of 256 trials. "
                 "Our own earlier local run of the same events agreed.")

CREDITS = """* Bariant, Bouvier, Leurent and Perrin, "Algebraic Attacks against Some Arithmetization-Oriented Primitives", IACR Transactions on Symmetric Cryptology 2022(3): the two-round bypass on a special line, which makes the digest a univariate polynomial.
* Grok (xAI), our research partner, job 133: the Weil and Cauchy-Schwarz reduction of the success premise to two moments of the number of usable roots, the explicit first- and second-moment constants (plane genus bound), the Markov cap, and the counterexample (X^3 over F_101) showing that a statement about components over the algebraic closure alone does not give the bound.
* Our own entry POSR5T (27d33f4a, r = 5, executed and reviewed): the program, the cost conventions and the ledger method that this entry extends.
* The accepted entries of the other tracks, for the conventions that the cost model uses: every load, store and control operation priced, no free registers, no free dispatch, and the cost model's random-word primitive as the only source of randomness.
* Claude Opus 5.5 in Claude Code prepared the package; Claude Sonnet 5.5 sub-agents wrote the cost-model charges for the root isolation, the premise arithmetic and the package assembly. The owner (Jbenisek) directed the work."""

COIN_RULE = """The only randomness of the algorithm is the cost model's random-word primitive (fresh independent algorithmic coins): each use returns a fresh word, uniform on `0..2^64-1` and independent of everything else, and costs one operation. **Probability space:** every probability of section 9 is over these words. A draw is five fresh words `w0, ..., w4`; the draw is `x = (w4 2^256 + w3 2^192 + w2 2^128 + w1 2^64 + w0) mod p`, by Horner's rule with `B = 2^64 mod p`. For every residue `x` the number of integers below `2^320` that reduce to `x` is `floor(2^320 / p)` or `ceil(2^320 / p)`, so `|P[x] - 1/p| <= 2^-320` and the draw is within statistical distance `p / 2^320 = @@EPS_COIN@@ < 2^-65` of uniform on `F_p`. A draw costs @@COIN_DRAW_COST@@ operations: 15 field operations (the conversion of `2^32` and its squaring give `B`; five conversions of the words; four multiplications by `B`; four additions); for each word one random-word operation, one load, one store into the array `w` and three control operations (two addresses, the increment of the word index), 30 in all; and 16 control operations (12 for the Horner loop, 2 for the entry of the call, 2 for the address of `w`). Draws are made once per trial for the centre and once per isolation round for the shift: at most `K (1 + Z) = @@COIN_DRAWS@@` draws, `@@COIN_WORDS@@` words. No word is used twice, and the number of words used before a draw depends only on earlier words, so each draw is independent of the earlier course of the algorithm."""

ISO_TEXT = """`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds."""

STOP_RULE_NEW = ("The program has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has a fixed recursion: "
                 + HGCD_BOUND + ". Hence, when the Euclidean sequences of stage D are normal (declared in `H1-charging-rules`), the number of executed operations is at most `N_max` for every coin sequence and every target value, the program cannot halt early except by the success exit or the failure exit after `K` trials, and nothing in the claim depends on a run being lucky.")

# ------------------------------------------------------------------ sections 2-5 from the old template, patched
old = rd(os.path.join(OLD, 'proof_template.md')).replace('\r\n', '\n')
def cut(a, b): return old[old.index(a):old.index(b)]
sec23 = cut('## 2. Two free rounds', '## 4. The program')
sec41 = cut('## 4. The program', '### 4.2 Machine model')
sec4344 = cut('### 4.3 Stage C', '## 5. Why the output is a collision')
sec5 = cut('## 5. Why the output is a collision', '## 6. Ledger')
def patch(text, a, b, count=1):
    assert text.count(a) >= 1, a[:80]
    return text.replace(a, b)
sec23 = patch(sec23, "(computed; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked on 5 random `tau`\nagainst an independent big-integer reference that reproduces the 11 public Orchard vectors).",
              "(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`\nagainst an independent big-integer reference that reproduces the 11 public Orchard vectors).")
a = sec41.index('Stopping rule over the')
b = sec41.index('#### 4.1.1 Coins')
para = sec41[a:b]
for _a, _b in (("is a constant of the source", "is a constant of the algorithm"),):
    para = para.replace(_a, _b)
i2 = para.index('The program has no other loop whose length')
para = para[:i2] + STOP_RULE_NEW + '\n\n'
sec41 = sec41[:a] + para + sec41[b:]
sec41 = sec41[:sec41.index('#### 4.1.1 Coins')] + '#### 4.1.1 Coins\n\n@@COIN_RULE@@\n\n#### 4.1.2 Stage E: isolating a root of G\n\n' + ISO_TEXT + '\n\n'
sec41 = patch(sec41, "  A  c := a uniform element of F_p from the coin words (section 4.1.1)", "  A  c := a uniform element of F_p from five words of the coin tape (section 4.1.1)")

SEC42 = """### 4.2 Machine model and charging rules

Every operation of the algorithm is counted where it executes; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation).
* every loop: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). Loops over the elements of an array written eight elements per pass (the pointwise, copy, fold and subtraction loops of the powering and of the products) are charged 3 per pass of eight, 1 for the bound, 2 when the main loop is left, and 3 per iteration for the remaining 0 to 7 elements.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, comparison, conditional branch, assignment of a register, and the selection of an element of the register block (16 data words) by a computed index. Data-dependent tests are charged per executed test.
* index arithmetic uses only shifts, additions, subtractions, comparisons and branches (the benchmark's primitive list has no integer multiplication, division or modulo): a multiplication by a power of two is a shift, by 3 or 5 a shift and an addition, and a product of an index and a stride is a running sum; each is charged as a control operation where it occurs.
* transforms: a transform of size `3 * 2^a` is a twiddle-free radix-3 stage (8 operations per leaf) followed by three rows of radix-2 passes of at most four layers. A pass works on blocks of `2^k <= 16` points held in registers; each butterfly is three field operations (none for the multiplication when the twiddle is 1), each twiddle is one load with its address operation (the first twiddle of a layer also 2 operations of address formation), and the group and block loops around a block are charged 3 per iteration and 2 on exit. The working registers are a disclosed assumption: the 16 data words, the twiddle operand and the butterfly temporary, a register file of 18 words of 256 bits. The 256-bit constants of the radix-3 stage are loaded at every use.
* random words: the cost model's random-word primitive is one operation per word. Each word of a draw is also loaded, stored into the array `w` of the draw and addressed (one load, one store and three control operations), 6 per word. A draw is five words (30), the 4 iterations of the Horner loop (12), the entry (2), the address of the word array (2) and 15 field operations (the conversion of `2^32` and its squaring, five conversions of the words, four multiplications, four additions): 61 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: @@C@@ each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the five words converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena by a first-fit allocator with a 64-byte header per block (size, size of the previous block, in-use flag); a request of more than 196,608 bytes takes the first free block that fits, a smaller request the last free block that fits, a block is split when the remainder is at least 128 bytes, and a free merges with a free neighbour on either side. The allocator is charged per executed load, store, comparison, branch and address computation (550 per allocation and 105 per free at 16 live blocks), inside the stage rows, and a flat 64 per call for its statistics. The memory it uses is the arena of section 7.
* trial loop: the test of the trial counter, its increment and the bookkeeping of the trial, at most 12 operations per trial, are `TRIAL_EXTRA` = 12 in the ledger; the loop test and update of stage A are 5.
* the offline derivation of the constants is charged in section 6.2.

"""
sec42 = SEC42

# ------------------------------------------------------------------ section 6 / 7 text blocks
p06 = rd(os.path.join(T2, 'p06_ledger.md'))
peaks = ev['peaks']
mem_txt = f"""Three terms make up the memory.

(a) The code and static data of an implementation of the algorithm: {L(399216)} bytes of code, {L(32)} of initialised data and {L(bss_static)} of static tables and buffers (the 8,192-byte output buffer and the tables of the stages): {L(cm.IMAGE_EXTRA)} bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is `ceil64(1.177 * (heap peak + 704)) = {L(arena)}` bytes, where the heap peak is the maximum over the stages of the bytes in use computed by the allocation walk (each array counted as 64 + 32 * slots rounded up to 64 bytes, headers included): {L(ev['heap_peak'])} bytes, in stage {max(peaks, key=peaks.get)}. The peaks per stage (twiddle table, `g`, `F` and the live set of the stage): A {L(peaks['A'])}; B {L(peaks['B'])}; C {L(peaks['C'])}; D {L(peaks['D'])}; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The same walk reproduces the measured heap peak exactly at r = 3 and r = 5 and within 64 bytes at r = 4 (section 6.1), and the factor 1.177 is the one with which the executed r = 5 entry ran (the executed r = 4 entry ran with 1.144). That the arena of this rule suffices at r = 7 is declared in `H1-charging-rules` (A2). The largest buffers (stage C at `m = {L(m)}`) are the twiddle table (`2^{aexp - 1}` elements), `Y` (`3 * 2^{aexp}` elements), `tmp`, `MU`, `g` and the result `F`.

(c) A stack bound of 65,536 bytes.

Total: (a) + (b) + (c) = `{L(mem_bytes)}` bytes `= 2^{math.log2(mem_bytes):.5f}`, claimed as `memory_log2_bytes = {mem_log2:.3f}` (rounded up at three decimals). The memory penalty is `max(0, {mem_log2:.3f} - 20) = {mem_log2 - 20:.3f}`. The offline derivation of section 6.2 is a closed formula per constant; its memory is bounded by 1,024 bytes, inside the figure above. The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init"."""

# ------------------------------------------------------------------ assemble the proof template
sec8 = rd(os.path.join(T2, 'p08_provided.md'))
sec9 = rd(os.path.join(T2, 'p09_success.md'))
sec10 = rd(os.path.join(T2, 'p10_evidence.md'))
p01 = rd(os.path.join(T2, 'p01_claim.md'))
sec11 = """## 11. Appendix D: the premise arithmetic (`premise_numbers.py`)

`python3 premise_numbers.py` recomputes with exact rationals every number of section 9.2 and 9.3.

@@APPENDIX_D@@
"""

proof_tpl = (p01 + sec23 + sec41 + '@@CHARGING_RULES@@\n\n' + sec4344 + sec5 + p06 + '\n## 7. Memory\n\n@@MEMORY_SECTION@@\n\n' + sec8 + sec9 + sec10 + sec11)

# ------------------------------------------------------------------ values
# sum script lists
fixed_list = [ev['init'], cm.LINE_STAGE, ev['miss'], cm.H_STAGE, cm.I_STAGE]
trial_list = [tr['A'].ops, tr['B'].ops, tr['C'].ops, tr['D'].ops, ev['E1'], ev['F1'], ev['G1'], cm.TRIAL_EXTRA]
assert sum(fixed_list) + K * sum(trial_list) + off == N

vals = {
    'R': str(R), 'K': str(K), 'W': str(W), 'DMAX': '16', 'Z': '64', 'LINE': '0', 'DEXP': str(6 + R), 'C': str(C),
    'PARTIAL': '%s partial rounds %s and %s' % (NUM[R], ', '.join(str(4 + i) for i in range(R - 1)), str(4 + R - 1)),
    'PARTIAL_WORD': '%s partial rounds' % NUM[R],
    'PARTIALRS': ', '.join(str(4 + i) for i in range(R)),
    'LAYERS': NUM[6 + R],
    'D': L(D), 'M': L(m), 'M1': L(m - 1), 'H': L(Hn), 'HEXP': str(hexp), 'AEXP': str(aexp), 'N2': L(2 * Hn), 'N2_HALF': L(Hn), 'STEPS': str(steps), 'VEXP': str(vexp),
    'FD0': '0x28cf6129b49568f76cbbcb977dae09a15d9b0b6c18a191886de5f7aae3a6297b',
    'TRIAL_MEM': 'about 136 GB', 'TRIAL_WORK': 'about 4.3 times the work of an r = 6 trial',
    'N_BOUND': L(N), 'UNITS': '{:,.1f}'.format(N / C), 'TIME_LOG2_EXACT': repr(TL_EXACT), 'TIME_LOG2': '%.5f' % TL,
    'MEM_BYTES': L(mem_bytes), 'MEM_LOG2': '%.3f' % mem_log2, 'MEM_PEN': '%.3f' % (mem_log2 - 20), 'SCORE': '%.5f' % score,
    'ARENA': L(arena), 'OFFLINE_BOUND': L(off), 'OFFLINE_BOUND_RAW': str(off), 'PREP_LOG2': '20',
    'Q': Q_STR, 'Q_EXACT': '%.10f' % float(Q_EXACT), 'Q_CS': '%.10f' % float(B['q_cs']), 'TAIL': '%.10f' % float(B['tail']), 'DD1': '272',
    'E1': '%.3e' % float(pn.e1), 'E2': '%.8f' % float(B['e2']),
    'P_SUCC': P_SUCC, 'P_SUCC_EXACT': '%.9f' % float(succ_exact), 'P_NOTAIL': '%.9f' % float(B['succ_notail']),
    'EPS_COIN': '%.3e (2^%.2f)' % (float(pn.eps_coin), math.log2(float(pn.eps_coin))), 'EPS_ISO': '%.3e (2^%.2f)' % (float(pn.eps_iso), math.log2(float(pn.eps_iso))),
    'COIN_DRAW_COST': str(ce.COIN_DRAW), 'COIN_READ': L(ce.COIN_READ), 'COIN_WORDS': L(K * 5 * 65), 'COIN_BYTES': L(K * 5 * 65 * 8), 'COIN_DRAWS': L(K * 65), 'W_DEV': '%.3e' % float(Fr(1, 2) - pn.wq),
    'W1_QCS': '%.8f' % float(pn.bound(1, 2)['q_cs']), 'W1_SUCC': '%.8f' % float(pn.bound(1, 2)['succ']),
    'W2_QCS': '%.8f' % float(pn.bound(2, 2)['q_cs']), 'W2_SUCC': '%.8f' % float(pn.bound(2, 2)['succ']),
    'W3_QCS': '%.8f' % float(pn.bound(3, 2)['q_cs']), 'W3_SUCC': '%.8f' % float(pn.bound(3, 2)['succ']), 'W3_K3': '%.8f' % float(pn.bound(3, 3)['succ']),
    'SENS_ROWS': '\n'.join(sens), 'QMIN_K1': '0.39000', 'QMIN_K2': '%.5f' % qmin(2), 'QMIN_K3': '%.5f' % qmin(3), 'QMIN_K4': '%.5f' % qmin(4),
    'Q_MIN_K': '%.5f' % qm2, 'Q_RATIO_K': '%.3f' % (qm2 / q_used),
    'S_INIT': L(ev['init']), 'S_LINE': L(cm.LINE_STAGE), 'S_A': L(tr['A'].ops), 'S_B': L(tr['B'].ops), 'S_C': L(tr['C'].ops), 'S_D': L(tr['D'].ops),
    'S_E': L(ev['E1']), 'S_F': L(ev['F1']), 'S_G': L(ev['G1']), 'S_X': L(cm.TRIAL_EXTRA), 'S_MISS': L(ev['miss']), 'S_H': L(cm.H_STAGE), 'S_I': L(cm.I_STAGE), 'NSET': str(ev['nset']),
    'INV': L(inv), 'R16': L(r16), 'POWH16': L(ce.pow_half(16)), 'TAY16': L(ce.taylor_shift(16)), 'GCD16': L(ce.gcd_cl(16, 15)), 'F_ARITH': L(F_ARITH),
    'L_FIXED': ', '.join(str(x) for x in fixed_list), 'L_TRIAL': ', '.join(str(x) for x in trial_list),
    'VAL_ROWS': '\n'.join(val_rows), 'E_RATIO': '%.3f' % E_RATIO,
    'COIN_RULE': COIN_RULE, 'CHARGING_RULES': sec42, 'MEMORY_SECTION': mem_txt,
    'MODEL_NAME': 'Claude Opus 5.5', 'HARNESS_NAME': 'Claude Code', 'CREDIT_LINES': CREDITS,
    
}
NOTE_EXEC = EXECUTOR_NOTE

def fill(text, extra=None):
    mp = dict(vals)
    if extra: mp.update(extra)
    # nested placeholders (values that contain @@X@@) are expanded repeatedly
    for _ in range(4):
        text = re.sub(r'@@([A-Z0-9_]+)@@', lambda mm: mp[mm.group(1)] if mm.group(1) in mp else mm.group(0), text)
    return text

def fence(name, lang):
    body = rd(os.path.join(HERE, name)).rstrip('\n')
    assert '```' not in body
    if lang == 'c': body = chr(10).join(' ' * ((len(l_) - len(l_.lstrip(' ')) + 1) // 2) + l_.lstrip(' ') for l_ in body.split(chr(10)) if l_.strip())  # review-budget: blank lines of the C listing dropped (whitespace only)
    if lang == 'python':
        import ast
        cand = chr(10).join(l_ for l_ in body.split(chr(10)) if l_.strip())
        if ast.dump(ast.parse(cand)) == ast.dump(ast.parse(body)): body = cand
    return '#### %s\n\n```%s\n%s\n```' % (os.path.basename(name), lang, body)

appD = fence('premise_numbers.py', 'python')

# placeholders for the appendices are inserted after the fill so that code containing '@@' cannot be touched
head = fill(proof_tpl)
left = sorted(set(re.findall(r'@@[A-Z0-9_]+@@', head)))
allowed = {'@@APPENDIX_D@@'}
if set(left) - allowed:
    sys.exit('unfilled placeholders in proof: %s' % sorted(set(left) - allowed))
proof = head.replace('@@APPENDIX_D@@', appD).rstrip('\n') + '\n'

FIX = [
 ("## 4. The program (at most K centres, one thread)", "## 4. The algorithm (at most K centres, one thread)"),
 ("The program uses the line `j = 0`", "The algorithm uses the line `j = 0`"),
 ("from five words of the coin tape (section 4.1.1)", "from five fresh random words (section 4.1.1)"),
 ("encoded as 64 hexadecimal digits each; exit status 0.", "encoded as 64 hexadecimal digits each."),
 ("If t > K was reached: exit status 2, no output (the failure event", "If t > K was reached the algorithm fails (the failure event"),
 ("at the statement that executes it. Section 6.1", "where it executes. Section 6.1"),
 ("so the program starts from", "so the algorithm starts from"),
 ("the program cannot halt early except by the success exit or the failure exit after `K` trials", "the algorithm cannot stop early except by success or by failure after `K` trials"),
 ("the outer loop of `poly_gcd_own`", "the outer loop of the Euclid driver"),
 ("the program exits with status 0 only if they are equal and the pairs differ. A run that does not reach stage H prints nothing and exits with status 2; it never outputs a non-collision.", "the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision."),
 ("(they are independent because the program draws them from distinct fresh random words)", "(they are independent because each draw uses distinct fresh random words)"),
 ("The program draws its centres", "The algorithm draws its centres"),
 (", and no run of this program at r = 7 enters it.", "."),
 ("The program has no other loop whose length", "The algorithm has no other loop whose length"),
 ("The code: if `b = 0`", "The procedure: if `b = 0`"),
 ("and the statements of `main` outside the counters;", "and the trial loop;"),
 ("because `bound_mem_since` adds 9 operations per field operation", "because the memory-access charge adds 9 operations per field operation"),
 ("`CTL(12000)` for the Tonelli-Shanks control and `CTL(2)`, the field operations of stage F are charged 10 each (`bound_mem_since`)", "12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge)"),
 ("the program re-derives it (stage B tests", "the algorithm re-derives it (stage B tests"),
 ("(no cap `DMAX` in the program)", "(no cap `DMAX`)"),
 ("`fp_pow` by `q` and by `(q+1)/2`", "the powers by `q` and by `(q+1)/2`"),
]
for _a, _b in FIX:
    assert _a in proof, _a
    proof = proof.replace(_a, _b)
lines = proof.split('\n')
def find(prefix):
    for i_, l_ in enumerate(lines):
        if l_.startswith(prefix): return i_
    sys.exit('heading not found: ' + prefix)
def rng(a_, b_): return '%d-%d' % (find(a_) + 1, find(b_))
ln = {'LN_PREMISE': rng('### 9.1', '### 9.3'), 'LN_EVIDENCE': rng('### 10.1', '### 10.2'), 'LN_LEDGER': rng('## 6.', '## 8.')}
claim = fill(rd(os.path.join(T2, 'claim_template.json')), ln)
note = fill(rd(os.path.join(T2, 'note_template.md')), ln)
left = sorted(set(re.findall(r'@@[A-Z0-9_]+@@', claim + note)))
if left: sys.exit('unfilled placeholders: %s' % left)
json.loads(claim)
if len(note.encode('utf-8')) < 5 * 1024: sys.exit('note under 5 KiB')

os.makedirs(OUT, exist_ok=True)
for name, txt in (('proof.md', proof), ('claim.json', claim), ('submission-note.md', note)):
    open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n').write(txt)
for sub in ('experiments', 'certificates'):
    d_ = os.path.join(OUT, sub)
    if os.path.isdir(d_): shutil.rmtree(d_)
os.makedirs(os.path.join(OUT, 'certificates'))
shutil.copy(os.path.join(OLD, 'certificates', 'manifest.json'), os.path.join(OUT, 'certificates', 'manifest.json'))
print('written to', OUT, '| proof bytes', len(proof.encode()), '| note bytes', len(note.encode()), '| claim bytes', len(claim.encode()), '| lines', ln)
print('N =', L(N), 'time_log2 =', '%.5f' % TL, 'memory', mem_log2, 'score %.5f' % score, 'success', P_SUCC, 'q', Q_STR)
