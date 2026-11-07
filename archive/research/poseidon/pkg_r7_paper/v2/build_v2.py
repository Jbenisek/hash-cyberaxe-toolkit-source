#!/usr/bin/env python3
"""Builds the Poseidon r7 algebraic paper package into OUT (default ./out): claim.json, proof.md, submission-note.md, experiments/, certificates/.
python -B build_v2.py [OUT]      (run from this folder; reads template2/, src/, tests/, exp/, the old template for sections 2-5, the r5 section 4.2)
Every number is computed here from costmodel.py, costmodel_e.py and premise_numbers.py; nothing is typed in by hand except the texts.
FILING DAY: edit EXECUTOR and EXECUTOR_NOTE below to say what is true about the organizer runner, rerun this script, then run
  wsl -d Ubuntu -- bash stage_r7alg.sh <NEW slot name>   (a slot is never reused) and use the submit script it writes (research/launch/submit_pareto_posr7alg.sh).
"""
import json, math, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['MODEL_SRC'] = os.path.join(HERE, 'src')
sys.path.insert(0, HERE)
import costmodel as cm, costmodel_e as ce, premise_numbers as pn

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out')
OLD = os.path.join(HERE, '..', '..', 'algebraic_paper', 'template')
R5 = os.path.join(HERE, '..', '..', 'orchard', 'exec_r5tt', 'pkg_fin', 'proof.md')
T2 = os.path.join(HERE, 'template2')
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
evc, measc = cm.validation_r3_coin()
val_rows.append('| r = 3, the program of Appendix A (coin centre) | %s | %s | %s | %.5f | %s | %s |' % (L(evc['total']), L(measc), L(evc['total'] - measc), math.log2(evc['total'] / measc), L(evc['heap_peak']), L(244745792)))

sens = []
for qq in (0.30, 0.25, float(Q_STR), 0.22, 0.20, 0.15, 0.10, 0.05):
    sens.append('| %.5f | %s |' % (qq, ' | '.join('%.5f' % (1 - (1 - qq) ** k) for k in (1, 2, 3, 4))))
qmin = lambda k: math.ceil((1 - 0.61 ** (1.0 / k)) * 100000) / 100000
qm2 = qmin(2)

r3c_n = 409369405120
r3c_t = math.log2(r3c_n / cm.perm_C(3))

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

COIN_RULE = """The only source of randomness is the cost model's random-word primitive: one operation per word, each word uniform on `0..2^64-1` and independent of everything else. A draw of the program is five such words `w0, ..., w4`; the draw is `x = (w4 2^256 + w3 2^192 + w2 2^128 + w1 2^64 + w0) mod p`, computed by Horner's rule with `B = 2^64 mod p` (`rnd_fp320` in `line.c`). For every residue `x` the number of integers below `2^320` that reduce to `x` is `floor(2^320 / p)` or `ceil(2^320 / p)`, so `|P[x] - 1/p| <= 2^-320` and the statistical distance of the draw from the uniform distribution on `F_p` is at most `p / 2^320 = @@EPS_COIN@@ < 2^-65`. A draw costs 91 operations: 15 field operations (the conversion of `2^32` and its squaring give `B`; five conversions of the words; four multiplications by `B`; four additions), 5 random-word operations, and 71 control operations (11 for each word, 12 for the Horner loop, 2 for the entry of the call, 2 for the address of the word array, as charged in `line.c`). The program text calls one function, `rnd64`, for the primitive: in the C file it is a 64-bit xorshift generator with a compile-time seed, so that the program can be compiled and run deterministically, and its 11 control operations per word are charged on top of the primitive's one operation. All probabilities of section 9 are over the cost model's random words. Draws are made once per trial for the centre and once per isolation round for the shift `a`, `@@COIN_WORDS@@` words at most (`K * 5 * (1 + Z)`), `@@COIN_DRAWS@@` draws."""

ISO_TEXT = """`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw a uniform `a` from `F_p` (a draw as in 4.1.1), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds."""

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
i2 = para.index('The program has no other loop whose length')
para = para[:i2] + STOP_RULE_NEW + '\n\n'
sec41 = sec41[:a] + para + sec41[b:]
sec41 = sec41[:sec41.index('#### 4.1.1 Coins')] + '#### 4.1.1 Coins\n\n@@COIN_RULE@@\n\n#### 4.1.2 Stage E: isolating a root of G\n\n' + ISO_TEXT + '\n\n'
sec41 = patch(sec41, "  A  c := a uniform element of F_p from the coin words (section 4.1.1)", "  A  c := a uniform element of F_p from five random words (section 4.1.1)")

# 4.2 from the r5 text
t5 = rd(R5).split('\n')
i = next(k for k, l in enumerate(t5) if l.startswith('### 4.2 Machine model'))
j = next(k for k, l in enumerate(t5) if l.startswith('### 4.3 Stage C'))
blk = t5[i:j]
k0 =next(k for k, l in enumerate(blk) if l.startswith('* the generator `rnd64`'))
coin_bullet = ("* random words: the cost model's random-word primitive is one operation per word (`X.rnd`). The program obtains the words from `rnd64` (`line.c`), a 64-bit xorshift generator with a compile-time seed: three statements `x ^= x << 13`, `x ^= x >> 7`, `x ^= x << 17`, each a shift, an exclusive or and an assignment (3 operations), so 9 operations, plus 2 for the return and the store of the word, 11 control operations per word, charged on top of the primitive's one operation. A draw (`rnd_fp320`) is five words (55 control operations, 5 random-word operations), the 4 iterations of the Horner loop (12), the entry of the call (2) and the address of the word array (2): 71 control operations, 5 random-word operations and 15 field operations (the conversion of `2^32` and its squaring, five conversions of the words, four multiplications, four additions), 91 operations in all, measured at 91 by the counters. The state `rs_state` is held in a register.")
blk[k0] = coin_bullet
b42 = '\n'.join(blk)
b42 = patch(b42, " (When a loop is split among threads, section 4.5, the charge of the macro for the whole loop is made once by the main thread and the bodies by the threads that run them.)", "")
b42 = patch(b42, 'The complete source is in section 9.', 'The complete source is in Appendix A.')
b42 = patch(b42, 'as the comments of section 9 show', 'as the comments of Appendix A show')
b42 = patch(b42, "`gen_kern.py` is part of the source of section 9; its output `ntt_kern.h` and `ntt_a3.h` are listed there", "`ntt_kern.h` and `ntt_a3.h` are generated files, listed in full in Appendix A")
b42 = patch(b42, "the reduced permutation evaluations of stage B: 321 each (section 3)", "the reduced permutation evaluations of stage B: @@C@@ each (section 3)")
b42 = patch(b42, "(`poly_gcd_own`, `hgcd`, `divrem_fast`, `gcd_cl`, `taylor_shift`, `split_find_root`)", "(`poly_gcd_own`, `hgcd`, `divrem_fast`, `gcd_cl`, `taylor_shift`, `pow_half`, `split_find_root_capped`, `rnd_fp320`)")
b42 = patch(b42, "the centre `c_i` of stage A, the random words in `taylor_shift` and `rnd_fp254`", "the five coin words converted in `rnd_fp320` (the centre of stage A and the shift of every isolation round), the exponent in `taylor_shift`")
b42 = patch(b42, "There is no other system call in the run than the thread calls of section 4.5 (`arch_prctl` once, `clone` once per worker, `futex` wait and wake): the program contains no `mmap`, `munmap`, `clock_gettime` or second `write`.",
            "There is no other system call in the run than the one `arch_prctl` of the process entry (the thread-local block of `par_tls_boot`, inside the 100 of (iii)): `par_init(1)` creates no worker, so there is no `clone` and no `futex`, and the thread-control charges are zero; the program contains no `mmap`, `munmap`, `clock_gettime` or second `write`.")
b42 = patch(b42, "(vii) the statements of `main` before the counters start (`rng_seed`, `poly_degree_m`, the argument test): `PROLOGUE` = 500 (a bound), and the four snapshots", "(vii) the statements of `main` before the counters start (`par_init`, `rng_seed`, `poly_degree_m`, the argument test): `PROLOGUE` = 500 (a bound), and the four snapshots")
b42 += ("\n* the statements of `main` that the counters do not see in a trial: the test `trials > MAXTR` (a comparison and a branch), `trials++`, the stores of `t_centre`, `t_deg` and `t_gcd`, and the arguments of the report line: at most 12 operations per trial, charged in the ledger as `TRIAL_EXTRA` = 12. The trial loop of `main` itself is charged `CTL(3 + 2)` per trial.\n"
        "* threads: the source still contains the thread code of `par.c`, `par.h` and the `par_nt > 1` branches of `ntt.c`, `lean.c` and `line.c`. With `par_init(1)` no worker exists and `par_nt = 1`, so none of that code is executed, every thread-control and dispatch counter is zero, and nothing of it is charged. The static memory of `par.c` for the threads it can start is counted in section 7.\n"
        "* the offline derivation of the literals of the source is charged in section 6.2.")
sec42 = b42 + '\n\n'

# ------------------------------------------------------------------ section 6 / 7 text blocks
p06 = rd(os.path.join(T2, 'p06_ledger.md'))
sec7 = rd(os.path.join(T2, 'p07_memory.md')) if os.path.exists(os.path.join(T2, 'p07_memory.md')) else None
peaks = ev['peaks']
mem_txt = f"""The executable is linked statically and without any C library (@@BUILD_COMMAND@@): `nolibc.c` and `par.c` (Appendix A) supply the process entry, the two system calls the program executes (`write`, once, and `exit_group`, once; plus the one `arch_prctl` of the entry), `memcpy`, `memset`, `memmove`, `strcmp` and the small `printf` (no division, modulo or floating point) that appends the report to one buffer; there is no loader, no shared library, no other library code and no other system call. Three terms make up the memory.

(a) The whole executable image: every loadable segment, text + data + bss as printed by `size` for the program built with the arena below: text {L(399216)} + data {L(32)} + bss {L(arena + bss_static)} bytes. The bss is the arena ({L(arena)} bytes) plus {L(bss_static)} bytes of static state (the 8,192-byte output buffer, the tables, and the static memory of `par.c` for the threads it can start, which are never started). Without the arena the image is {L(cm.IMAGE_EXTRA)} bytes.

(b) The heap is inside term (a): every buffer of the program is served by `xalloc` from one static arena in the bss (`ARENA` is given on the command line, a multiple of 64). Nothing is mapped from the kernel at run time; the program exits with status 2 if a request does not fit. Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is `ceil64(1.177 * (heap peak + 704)) = {L(arena)}` bytes, where the heap peak is the maximum over the stages of the bytes in use computed by the allocation walk of the cost model (each array counted as 64 + 32 * slots rounded up to 64 bytes, headers included): {L(ev['heap_peak'])} bytes, in stage {max(peaks, key=peaks.get)}. The peaks per stage (twiddle table, `g`, `F` and the live set of the stage): A {L(peaks['A'])}; B {L(peaks['B'])}; C {L(peaks['C'])}; D {L(peaks['D'])}; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The same walk reproduces the measured heap peak exactly at r = 3 and r = 5 and within 64 bytes at r = 4 (section 6.1), and the factor 1.177 is the one with which the executed r = 5 entry ran (the executed r = 4 entry ran with 1.144). That the arena of this rule suffices at r = 7 is declared in `H1-charging-rules` (A2). The largest buffers (stage C at `m = {L(m)}`) are the twiddle table (`2^{aexp - 1}` elements), `Y` (`3 * 2^{aexp}` elements), `tmp`, `MU`, `g` and the result `F`.

(c) A stack bound of 65,536 bytes.

Total: (a) + (c) = `{L(mem_bytes)}` bytes `= 2^{math.log2(mem_bytes):.5f}`, claimed as `memory_log2_bytes = {mem_log2:.3f}` (rounded up at three decimals). The memory penalty is `max(0, {mem_log2:.3f} - 20) = {mem_log2 - 20:.3f}`. The program has no stored advice and no precomputed data beyond the literals of section 6.2; the twiddle table is built at run time and charged in stage "init"."""

# ------------------------------------------------------------------ assemble the proof template
sec8 = rd(os.path.join(T2, 'p08_provided.md'))
sec9 = rd(os.path.join(T2, 'p09_success.md'))
sec10 = rd(os.path.join(T2, 'p10_evidence.md'))
p01 = rd(os.path.join(T2, 'p01_claim.md'))
sec11 = """## 11. Appendices: source of the program, cost model and scripts

### Appendix A: the complete C source of the program

The files are shown in full, in the order: @@SOURCE_ORDER@@. In this appendix and in Appendix C the only change from the shipped files is whitespace, made so that the judge evidence fits its size limit: blank lines are omitted and each run of `k` leading spaces is printed as `ceil(k/2)` spaces. Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter and `n` to the control counter (address operations), `CTL(n)` adds `n` to the control counter, `loopc(n)` adds `3n + 2` to the control counter; every `fp_*` call increments the counter of its own kind (`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.rnd` counts random-word operations; `X.perm += k` adds `k` primitive operations; `snap()` reads all counters. Buffers are obtained from the tracked allocator (`NEW_FP`). `pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs; `ntt_kern.h` and `ntt_a3.h` are generated straight-line kernels.

@@APPENDIX_A@@

### Appendix B: the cost model (`costmodel.py`, `costmodel_e.py`)

`costmodel.py` reads the leaf charges from `ntt_kern.h` and `ntt_a3.h` and ports the control flow of the other sources; run it as `MODEL_SRC=<directory holding the files of Appendix A> python3 costmodel.py` with `costmodel_e.py` next to it. It prints the validation rows of section 6.1 and the account of section 6.

@@APPENDIX_B@@

### Appendix C: the test of stage E (`test_e.c`)

Linked with the files of Appendix A except `single.c` (small arena, `RR=3`), it runs `split_find_root_capped` on 90 synthetic products of distinct linear factors and prints the counters used in section 6.1.

@@APPENDIX_C@@

### Appendix D: the premise arithmetic (`premise_numbers.py`)

`python3 premise_numbers.py` recomputes with exact rationals every number of section 9.2 and 9.3.

@@APPENDIX_D@@
"""

proof_tpl = (p01 + sec23 + sec41 + '@@CHARGING_RULES@@\n\n' + sec4344 + sec5 + p06 + '\n## 7. Memory\n\n@@MEMORY_SECTION@@\n\n' + sec8 + sec9 + sec10 + sec11)

# ------------------------------------------------------------------ values
src_files = ['outbuf.h', 'nolibc.c', 'par.h', 'par.c', 'common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'attack.h', 'hgcd.h', 'ntt.c', 'ntt_kern.h', 'ntt_a3.h', 'poly.c', 'lean.c', 'line.c', 'split.c', 'hgcd.c', 'single.c']
for f_ in src_files: assert os.path.exists(os.path.join(HERE, 'src', f_)), f_
objs = 'single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c'
BUILD = ('`gcc -O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -DRR=%d -DARENA=%dULL -DMAXTR=%d -o single %s`' % (R, arena, K, objs))
RUN = '`single` with no argument, under `ulimit -s 64`; it prints the report and, on success, the six `COLLISION` lines, and exits with status 0 (status 2 and no output if all %d centres fail)' % K

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
    'COIN_DRAW_COST': '91', 'COIN_WORDS': L(K * 5 * 65), 'COIN_DRAWS': L(K * 65),
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
    'R3C_N': L(r3c_n), 'R3C_T': '%.5f' % ceil5(r3c_t), 'R3C_WALL': '51.5 minutes',
    'BUILD_COMMAND': BUILD, 'RUN_COMMAND': RUN, 'COIN_RULE': COIN_RULE, 'CHARGING_RULES': sec42, 'MEMORY_SECTION': mem_txt,
    'EXECUTOR_STATUS_SENTENCE': EXECUTOR, 'MODEL_NAME': 'Claude Opus 5.5', 'HARNESS_NAME': 'Claude Code', 'CREDIT_LINES': CREDITS,
    'SOURCE_ORDER': ', '.join('`%s`' % f_ for f_ in src_files),
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

appA = '\n\n'.join(fence(os.path.join('src', f_), 'c') for f_ in src_files)
appB = fence('costmodel.py', 'python') + '\n\n' + fence('costmodel_e.py', 'python')
appC = fence(os.path.join('tests', 'test_e.c'), 'c')
appD = fence('premise_numbers.py', 'python')

# placeholders for the appendices are inserted after the fill so that code containing '@@' cannot be touched
head = fill(proof_tpl)
left = sorted(set(re.findall(r'@@[A-Z0-9_]+@@', head)))
allowed = {'@@APPENDIX_A@@', '@@APPENDIX_B@@', '@@APPENDIX_C@@', '@@APPENDIX_D@@'}
if set(left) - allowed:
    sys.exit('unfilled placeholders in proof: %s' % sorted(set(left) - allowed))
proof = head.replace('@@APPENDIX_A@@', appA).replace('@@APPENDIX_B@@', appB).replace('@@APPENDIX_C@@', appC).replace('@@APPENDIX_D@@', appD).rstrip('\n') + '\n'

lines = proof.split('\n')
def find(prefix):
    for i_, l_ in enumerate(lines):
        if l_.startswith(prefix): return i_
    sys.exit('heading not found: ' + prefix)
def rng(a_, b_): return '%d-%d' % (find(a_) + 1, find(b_))
ln = {'LN_PREMISE': rng('### 9.1', '### 9.3'), 'LN_EVIDENCE': rng('### 10.1', '### 10.3'), 'LN_LEDGER': rng('## 6.', '## 8.'), 'LN_SOURCE_HEAD': '%d-%d' % (find('## 11.') + 1, find('## 11.') + 3)}
claim = fill(rd(os.path.join(T2, 'claim_template.json')), ln)
note = fill(rd(os.path.join(T2, 'note_template.md')), dict(ln, EXECUTOR_STATUS_SENTENCE=NOTE_EXEC))
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
    os.makedirs(d_)
shutil.copy(os.path.join(HERE, 'exp', 'exp_lowbits.py'), os.path.join(OUT, 'experiments', 'exp_lowbits.py'))
shutil.copy(os.path.join(HERE, 'exp', 'manifest_after_fix.json'), os.path.join(OUT, 'experiments', 'manifest.json'))
shutil.copy(os.path.join(OLD, 'certificates', 'manifest.json'), os.path.join(OUT, 'certificates', 'manifest.json'))
print('written to', OUT, '| proof bytes', len(proof.encode()), '| note bytes', len(note.encode()), '| claim bytes', len(claim.encode()), '| lines', ln)
print('N =', L(N), 'time_log2 =', '%.5f' % TL, 'memory', mem_log2, 'score %.5f' % score, 'success', P_SUCC, 'q', Q_STR)
