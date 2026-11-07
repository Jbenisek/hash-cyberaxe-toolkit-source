"""Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the blake3-r5 entry (rolled round body, ported from B3R7c) from the program's own numbers.
Run:  python -B build_all.py   (after stats_out.txt, appA.out, organizer_summary.txt, gen_c/cport.json exist)."""
import sys, json, os, string, math
from math import log2, exp, log, ceil
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "pkg")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(PKG, "blake3", "experiments"))
import bsrho as b

p = b.plan(256); lg = b.ledger(p); ls = b.loss(p); st = b.step256()
ph, filt, body, code, tmax = b.machine_constants(st)
PH7 = b.packed_circuit(st.qwords)[1]
UNIT = b.UNIT
assert UNIT == 14 + 208 * 5 and b.ROUNDS == 5
N = lg["total"]
TLraw = log2(N / UNIT)
TL = ceil(TLraw * 100000) / 100000
assert TL >= TLraw and TL - TLraw < 1e-5
TL3 = 124.8123
TL1 = 125.35348
TL4 = 125.06000
PRED = {'TL': 125.00951, 'MT': 0.37855, 'SC': 125.38806, 'ops': 31606, 'code': 1221192, 'Rw': 'five', 'label': 'B3R5c', 'id': '4a9f31b8-0ac7-475d-a73d-583a41298226', 'predlabel': 'B3R5b', 'TLs': '125.00951', 'MTlog': '20.37855', 'MTs': '0.37855', 'SCs': '125.38806'}
TL7, SC7, MT7 = PRED['TL'], PRED['SC'], PRED['MT']
parts = lg["parts"]
pk2 = ls["cut_halt"]
L = p["L"]; Q = p["Q"]
kfin = ls["nmax"] - 256
sumloss = ls["sum"]
assert ls["P_lower"] >= 0.39
_orig = b._lossq
sens = []
for e in (0.01, 0.05, 0.10, 0.25):
    b._lossq = (lambda r: (lambda *a, **k: _orig(*a, **dict(k, rate=r))))(1 - e)
    b._B.clear()
    pe = b.plan(256); lge = b.ledger(pe)
    sens.append((e, log2(lge["total"] / lg["total"]), pe["Tp"]))
b._lossq = _orig; b._B.clear()
assert b.plan(256)["B"] == p["B"]
sens_txt = "; ".join("%.4f bit for eps = %.2f (Tp %d)" % (x[1], x[0], x[2]) for x in sens)
sens_short = ", ".join("%.4f bit for eps = %.2f" % (x[1], x[0]) for x in sens)
eps = 0.0
fm = lambda v: "{:,}".format(int(v))
stats_txt = open(os.path.join(HERE, "stats_out.txt")).read().strip().split("\n")
appA = open(os.path.join(HERE, "appA.py")).read().rstrip("\n")
appOut = open(os.path.join(HERE, "appA.out")).read().rstrip("\n")
orgsum = open(os.path.join(HERE, "organizer_summary.txt")).read().strip().split("\n")
timing = json.load(open(os.path.join(HERE, "timing.json")))
sc = b.gen_scratch()
_ml = b.MEM_LIMIT
_base = code + b.REGFILE + b.COUNTERS + b.ADVICE
scanrows = []
for _tm in (4000, 8000, 12000, tmax):
    b.MEM_LIMIT = _base + b.SPARE + b.ENTRY * _tm
    _p = b.plan(256)
    _lg = b.ledger(_p)
    scanrows.append((_p["tmax"], log2(_lg["total"] / UNIT)))
b.MEM_LIMIT = _ml
assert [r[1] for r in scanrows] == sorted((r[1] for r in scanrows), reverse=True)
scan = "; ".join("%d entries: %.5f" % r for r in scanrows)
CPORT = json.load(open(os.path.join(HERE, "gen_c", "cport.json")))
NATIVE = json.load(open(os.path.join(HERE, "gen_c", "native", "native.json")))
assert CPORT["identical"] and CPORT["instructions"] == st.instr and CPORT["registers"] == st.regs and CPORT["calls"] == 2 * st.gen_calls
assert CPORT["wasm_instructions"] == b.GEN_CODE and CPORT["code_region"] == code and CPORT["scratch"] == sc[0] and CPORT["nodes"] + 1 == sc[2]
assert NATIVE["identical"]
ph1, ph2 = b.phase_bytes(code, tmax)
mem = b.ENTRY * tmax + code + b.REGFILE + b.COUNTERS + b.ADVICE
memlog2 = ceil(log2(mem) * 100000) / 100000
memterm = max(0, memlog2 - 20)
assert memterm == 0 and mem <= 2 ** 20
assert b.MEM_LIMIT >= mem and b.MEM_LIMIT - mem <= 64 + b.ENTRY - 1
assert max(ph1, ph2) <= b.MEM_LIMIT and mem == ph2
genimg = b.GEN_CODE * b.INSTR_BYTES
assert sc[0] + genimg <= b.gen_idle(tmax)
measured = ("(i) the circuit generator written in freestanding C (source embedded in `experiments/bsrho.py` as `GEN_C`, printed by `python3 bsrho.py --gen-c`, %s bytes) compiled to WebAssembly (clang -Os, 2,048-byte shadow stack) and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes (the memory budget 2^20) emits the identical program: "
            "%s instructions, %d registers, %s nodes (larger segment), %s primitive calls (both passes of both segments), q = 0, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total %s bytes (the final code region %s, the counters %s, its own scratch %s); the guest uses %d pages (highest nonzero byte %s) (the generator's code image, charged in the model at %s bytes, lies outside the guest memory in this sandbox). It needs %s wasm operations, below the %s word operations the ledger charges for the generator. "
            "(ii) The same C program as a static x86-64 binary without libc (a %s-byte text segment, %s bytes of bss) runs under `prlimit --as=%s` (its whole address space capped at 2^20 bytes) and writes the identical program (sha256 equal); it does not start under %s of address space. "
            "(iii) The entry's generator is the C program of (i) and (ii), run within the caps shown; the Python generator in `experiments/bsrho.py` is only the reference whose output text the C program reproduces (sha256 equal)." % (
                fm(CPORT["src_bytes"]), fm(CPORT["instructions"]), CPORT["registers"], fm(CPORT["nodes"]), fm(CPORT["calls"]), fm(CPORT["static_total"]), fm(CPORT["code_region"]), fm(CPORT["counters"]), fm(CPORT["scratch"]),
                CPORT["pages"], fm(CPORT["highest_nonzero_byte"]), fm(genimg), fm(CPORT["fuel"]), fm(lg["gen"]), fm(NATIVE["text"]), fm(NATIVE["bss"]), fm(NATIVE["as_ok"]), fm(NATIVE["as_fail"])))
statslines = "\n".join("    " + s.rstrip() for s in stats_txt)
orgl = "\n".join("    " + s for s in orgsum)
preclaim = ceil(log2((b.SETUP_FIXED + lg["gen"]) / UNIT) * 10) / 10
vals = dict(
    PH=fm(st.ops), perlane=st.ops / 256, tmax=fm(tmax), Tp=p["Tp"], log2L=log2(L), Lnum=L.numerator, Lden=L.denominator, B=p["B"], Qratio=Q / 2 ** 128,
    e2max=p["e2max"], c=p["c"], log2c=log2(p["c"]), regs=b.REGISTERS, usedregs=st.regs, spareregs=b.REGISTERS - st.regs, regbytes=fm(b.REGFILE), tempbody=st.regs - b.TB, PH7=PH7, PH7p=PH7 + b.RECOVER_EXTRA,
    unit=st.ops / 256 / UNIT, filt=filt, body=body, setupfixed=fm(b.SETUP_FIXED), gencalls=fm(2 * st.gen_calls), gencalls1=fm(st.gen_calls), gen=fm(lg["gen"]), setupall=fm(b.SETUP_FIXED + lg["gen"]),
    log2setup=log2((b.SETUP_FIXED + lg["gen"]) / UNIT), instr=fm(st.instr + filt + b.LOOP_OPS + b.other_code(st)), main=fm(parts["main"]), mainsci="%.4e" % float(parts["main"]),
    slices_sci="%.3e" % float(parts["slices"]), hits_sci="%.4e" % float(parts["stage1_hits"]), events=fm(parts["events"]), log2capr=log2(p["capr"]), log2capr1=log2(p["capr"]), rec_sci="%.4e" % float(parts["recovery"]),
    gencode=fm(b.GEN_CODE), gencodebytes=fm(genimg), nodes=fm(sc[2]), usesbytes=fm(sc[1]), scratch=fm(sc[0]), srcbytes=fm(CPORT["src_bytes"]), recov=fm(PH7 + b.RECOVERY_CODE),
    ph1=fm(ph1), memspare=fm(b.MEM_LIMIT - ph2), region=fm(b.gen_idle(tmax)), genneed=fm(genimg + sc[0]), N=fm(N), Nsci="%.6e" % N, Nunits="%.4e" % (N / UNIT), log2N=TLraw,
    TL=TL, TL3=TL3, dr3=TL - TL3, TL1=TL1, dr1=TL1 - TL, dTL=TL - 125.02375, dTL7=TL - TL7, dSC7=TL + memterm - SC7, mem7term=MT7, TL4=TL4, dr4=TL - TL4, memlog2=memlog2, memterm=memterm, score=TL + memterm, memlimit=fm(b.MEM_LIMIT), scan=scan, slack=TL - TLraw, pmain=100 * float(parts["main"]) / float(N), prec=100 * float(parts["recovery"]) / float(N), 
    trails=ls["trails"], pk2=pk2, kappa=b.KAPPA_256, cmax=b.CMAX, kfin=kfin, nmax=ls["nmax"], theta=ls["theta"], emain=ls["main"], zst=ls["z"], zfrac=ls["z"] / (ls["trails"] ** 2 / 2), kap=ls["kap"], wfac=ls["w"],
    destroy=ls["collision_on_path"], epsn=b.EPS, longf=ls["long_finish"], others=sumloss - ls["main"], sumall=sumloss, tfull=tmax - 59, sens=sens_txt, sens_short=sens_short, k10=9 * pk2, sparereq=b.SPARE,
    kb=p["kb"], fb=p["fb"], keytop=p["D"] + p["kb"] - 1, log2keys=p["kb"] + log2(p["Tp"]), keyfm=ls["key_false_match"], tmaxp1=fm(tmax + 1), log2cap=log2(ls["table_capacity"]), cap=ls["table_capacity"],
    mu2=float(Q) / 2 ** 32, mu2c=float(Q) / 2 ** 32 * (2 * log(2) - 1),
    sumloss=sumloss, Pl=ls["P_lower"], margin=ls["P_lower"] - 0.39, eps=eps, eps_cost=0.5 * log2(1 / 0.99), statslines=statslines, orgsum=orgl, B18=b.plan(18)["B"], t18=timing["t18"], t21=timing["t21"],
    tablebytes=fm(tmax * b.ENTRY), codebytes=fm(code), mem=fm(mem), appA=appA, appOut=appOut, qweight=bin(st.qint).count("1"), measured=measured, preclaim=preclaim,
    nchk=2000, nref_scalar=300, nref_step=fm(8192), nref_packed=448, 
    gain=0, spare=b.MEM_LIMIT - mem, epsp=100 * eps, stats1=stats_txt[0], stats2=stats_txt[1], cpst=fm(CPORT["static_total"]), genfuel=fm(CPORT["fuel"]), genops=fm(lg["gen"]),
)
_g = b.Gen(256)
_zero = b._constw(0)
_m = [_zero] * 8 + [[_g.inputs[32 * i + k] for k in range(32)] for i in range(8)]
_v = [b._constw(w) for w in b.IV] + [b._constw(w) for w in b.IV[:4]] + [_zero, _zero, b._constw(64), b._constw(b.FLAGS)]
b._rounds(_g, _v, _m, 1)
r1 = len(_g.nodes) - 1 - 256
_L = st.L
A_, B_, M_, F_ = _L["A"], _L["B"], _L["M"], _L["F"]
nots = sum(1 for c in A_ if c[0] == "~"); winit = sum(1 for c in A_ if c[0] in "z=")
Agates = len(A_) - nots - winit
r2 = Agates - r1
assert r2 == 7184 and len(B_) == 8416 and len(M_) == 576 and len(F_) == 256 and st.ops == len(A_) + 1 + b.LOOPS * (len(B_) + 3) + (b.LOOPS - 1) * (len(M_) + 1) + len(F_)
cnt = lambda ch, o: sum(1 for c in ch if c[0] == o)
xorn = cnt(A_, "^") + b.LOOPS * cnt(B_, "^") + cnt(F_, "^"); andn = cnt(A_, "&") + b.LOOPS * cnt(B_, "&"); orn = cnt(A_, "|") + b.LOOPS * cnt(B_, "|")
loopc = 1 + 3 * b.LOOPS + (b.LOOPS - 1)
movn = nots + winit + (b.LOOPS - 1) * len(M_)
assert xorn + andn + orn + movn + loopc == st.ops, (xorn, andn, orn, movn, loopc, st.ops)
vals.update(r1=fm(r1), r2=fm(r2), Agates=fm(Agates), nots=nots, winit=winit, Bn=fm(len(B_)), Mn=len(M_), Mtot=fm((b.LOOPS - 1) * len(M_)), Fn=len(F_), loopc=loopc, Lctl=5, xorn=fm(xorn), andn=fm(andn), orn=fm(orn),
            movn=fm(movn), ctln=loopc, Alen=fm(len(A_)), stepinstr=fm(st.instr), PH1=fm(PRED['ops']), codebytes1=fm(PRED['code']), savedinstr=fm(PRED['ops'] - st.instr), PHdiff=fm(st.ops - PRED['ops']), PHpct=100 * (st.ops / PRED['ops'] - 1),
            nrolled=fm(16384), n0=fm(_L["nodes"]), n1=fm(1 + 1024 + len(B_)), Nunused=0)
# ---- Lemma 2 v2 values (text_v2_blake3.py) ----
import re as _re
from math import expm1, log1p, exp as _exp, ceil as _ceil
Pcert = _re.search(r"certified \(exact rationals, 60-digit decimals\) = ([\d.]+)", appOut).group(1)
assert float(Pcert) >= 0.39
kk = ls["k"]; n2 = kk + 256 + 1; _kp = b.KAPPA_256; _pp = _exp(-_kp)
_q = float(ls["trails"]); _l2n = float(L * L / (1 << 256)); _s0 = _q * _q / 2
hq = _s0 * _l2n; ql = _q * _l2n
pbin = -expm1(n2 * log1p(-_pp)) - n2 * _pp * _exp((n2 - 1) * log1p(-_pp))
ES = ql; EX = ql * (2 + _kp) * _exp(-_kp / 2) + hq * _pp * (1 + _kp); EJ2a = 2 * ql * hq; EJ2b = hq * _pp * (1 + _kp); EY = hq * _pp
assert abs(pbin + ES + EX + EJ2a + EJ2b + EY - pk2) < 1e-12 * pk2 + 1e-18, (pbin + ES + EX + EJ2a + EJ2b + EY, pk2)
Mnum = float(p["c"] + (1 << 48)); Qnum = float(Q)
assert 240 * Mnum <= Qnum
_tiny = [Qnum * 2 ** 16 / 2.0 ** 256, Qnum * kk / 2.0 ** 256, kk * kk * float(L) / 2.0 ** 256, _exp(-300 + (_exp(5) - 1) * hq), 2.0 ** -99]
assert max(_tiny) < 2.0 ** -96 * 1.0001 and sum(_tiny) < 2.0 ** -90, _tiny
padded = _ceil(tmax / 4) * 32 + _ceil(tmax / 16) * 32; padx = padded - 10 * tmax
_memfit = mem + padx
termextra = 3800 + 3 * tmax
slackops = int(N * (2.0 ** (TL - TLraw) - 1))
lblbody = fm(lg["parts"]["main"] // p["B"])
V2 = dict(Pcert=Pcert, kk=kk, Hq=hq, pbin=pbin, ES=ES, EX=EX, EJ2a=EJ2a, EJ2b=EJ2b, EY=EY, Mnum=Mnum, Qnum=Qnum, twoeps=2 * b.EPS,
          oldTL='125.29018', oldTp=229, pred='8fbecd8a', padded=fm(padded), padx=padx, memfit=fm(_memfit), termextra=fm(termextra), slackops=fm(slackops), lblbody=lblbody, body=body)

vals.update(V2)
vals.update(Rn=b.ROUNDS, Rw=PRED['Rw'], LOOPS=b.LOOPS, LOOPSm1=b.LOOPS - 1, label=PRED['label'], predid=PRED['id'], pred8=PRED['id'][:8], predlabel=PRED['predlabel'], TLpred=PRED['TLs'], MTpredlog=PRED['MTlog'],
            MTpred=PRED['MTs'], SCpred=PRED['SCs'], UNIT=UNIT, UNITf=fm(UNIT), unitlist=", ".join(fm(14 + 208 * k) for k in range(1, b.ROUNDS + 1)))
def need(text, label):
    names_ = {f[1] for f in string.Formatter().parse(text) if f[1]}
    missing = sorted(n for n in names_ if n not in vals)
    assert not missing, (label, missing)
tpl = open(os.path.join(HERE, "proof_t8.md"), encoding="utf-8").read()
note = open(os.path.join(HERE, "note_t8.md"), encoding="utf-8").read()
need(tpl, "proof_t"); need(note, "note_t")
text = tpl.format(**vals)
w = lambda path, t: open(path, "w", newline="\n", encoding="utf-8").write(t)
w(os.path.join(PKG, "blake3", "proof.md"), text)
print("proof bytes", len(text.encode()))
lines = text.split("\n")


def span(head, nxt):
    a = next(i for i, l in enumerate(lines) if l.startswith(head)); z = next(i for i, l in enumerate(lines) if i > a and l.startswith(nxt))
    return "proof:%d-%d" % (a + 1, z)


S1 = span("## 1.", "## 2."); S2 = span("## 2.", "## 3."); S31 = span("### 3.1", "### 3.2"); S32 = span("### 3.2", "### 3.3"); S33 = span("### 3.3", "### 3.4"); S34 = span("### 3.4", "### 3.5")
S35 = span("### 3.5", "### 3.6"); S36 = span("### 3.6", "### 3.7"); S4 = span("## 4.", "## 5."); S5 = span("## 5.", "## 6."); S6 = span("## 6.", "## 7."); S7 = span("## 7.", "## 8."); S8 = span("## 8.", "## Appendix A")
Tp = p["Tp"]

H1 = dict(
    id="H1-random-function-model", role="score-critical",
    statement=("Model premise, four clauses. Let F be a uniformly random function from 256-bit values to 256-bit values. For the fixed target, the probability that the single attempt of the search succeeds, with the walk g(x) = f(x) XOR q (f(x) = the complete 5-round digest of the 64-byte message 0^32 || x, q = 0 the digest-plane mask of the generated program), "
               "is at least the probability P_F, over the fresh word r and a uniformly random F, that the same search succeeds when every evaluation of g is replaced by F (lazy sampling). Clauses: (a) distinct evaluated inputs collide with probability 2^-256, uniform and independent outputs; (b) the iterates from r + t have the first-collision law of a random mapping; "
               "(c) a point is a distinguished point (low 32 bits zero and the next 90 bits below %d) with probability %d / 2^122, independently of the collision events; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of g; given the whole history of the run and which later outputs are distinguished points, a fresh evaluation equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard of F). "
               "Proof.md Section 4 (Lemma 2) proves P_F >= %.4f for F from the hazard alone, by a supermartingale over the evaluations, with no conditioning on which trails finish and no fixed-size birthday step; (d) is the premise that g has that hazard. This is a comparison of two success events, not a statement about the entropy of r. Nothing else in the success bound is heuristic." % (Tp, Tp, ls["P_lower"])),
    scope=("The fixed target blake3-r5-prefix-v1 restricted to 64-byte messages 0^32 || x, the fixed mask q, the 2^128-scale evaluation of g along about %d trails of mean length 2^%.2f started from r + t, 256 trails at a time. Not claimed for other messages, other round counts, or evaluations beyond this scale." % (round(ls["trails"], -2), log2(L))),
    extrapolation=("Declared and not proved: an assumption, no proof is known. The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. The organizer experiments bsrho-n18 and proj-k0-w256 run this program on the real target at reduced width (the search at width 18) and at full width for 2048 points with 21-bit projections; they are program checks, no number of the claim is estimated from their counts, and no sampling premise is used. "
                   "Extrapolation from these sizes to width 256 and 2^128 evaluations is by the premise only. If the collision hazard is (1 - eps) / N instead of 1 / N (clause (d), or a deficit eps in clause (a)), the plan of this program needs, to restore 0.39: %s." % sens_short),
    evidence_ids=["experiment:bsrho-n18", "experiment:proj-k0-w256", S4, S5, S6],
    limitations=("A model premise about one fixed function, not a theorem: on the target the run is a deterministic function of r. It cannot be tested at width 256; the experiments reach width 18 and 21-bit projections of 2048 points per trial and do not measure collision structure at 2^128 evaluations. "
                 "The bound has no margin above 0.39 (B is the least multiple of 10^24 that reaches it), so any hazard deficit is repaired by extra time, priced above: %s." % sens_txt),
)
H3 = dict(
    id="H3-machine-convention", role="supporting",
    statement=("Declared machine convention of this entry (supporting; a convention, not a claim about the benchmark; the register-file convention of our 0a9640ed and a2e94df7, here with %d registers). The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = %d registers of 256 bits, counted as %s bytes of memory, and charges every operation, load, store and register move. The main loop (one batch of 256 trails, %d operations: the %s-operation generated step, a %d-operation stage-1 test and 3 loop operations) "
               "has no load or store; it has the register moves of the message permutation (576 plane copies after each of the first two iterations of the round loop), the setup of the message slots (%d operations), the complements (%d) and the loop control (%d operations), all counted. The generated program uses %d registers; the rest are for the loop counters and handlers. The organizer's reference count C(r5) = 1054 is used only as the unit. Every instruction is charged 36 bytes of code, also the three-register ones and the loop-control ones (no decode is free), and the code of the circuit generator is charged at 36 bytes per instruction of its compiled form (%d instructions, proof.md 3.6)." % (b.REGISTERS, b.REGISTERS, fm(b.REGFILE), body, fm(st.ops), filt, winit, nots, loopc, st.regs, b.GEN_CODE)),
    scope="The loop body of one batch of 256 lanes, its stage-1 test and the handlers; table accesses, recovery, events and setup are charged at the stated bounds including loads and stores of their words.",
    extrapolation="A machine with fewer than %d registers would add loads and stores to the loop body; that cost is not priced for the rolled program (proof.md 3.5) and not claimed. The claim assumes the declared %d." % (st.regs, b.REGISTERS),
    evidence_ids=[S31, S32, S33, S35, S36, S7],
    limitations="The benchmark profile does not fix a register count or an instruction set; the declaration is this entry's own, as is the reading of the loop (counted loop-control operations and instructions, register moves for the message permutation, no free decode or re-indexing). The counts (%s operations, %s instructions, %d registers) are produced by the generator in the program (a C port emits the identical program in a memory-capped sandbox, proof 3.6); smaller register files are not priced." % (fm(st.ops), fm(st.instr), st.regs),
)
R = []
R.append("Two distinct 64-byte messages 0^32 || x and 0^32 || y (x != y, 256-bit little-endian integers): one chunk of one block, chaining value IV, counter 0, length 64, flags 11 (CHUNK_START|CHUNK_END|ROOT), 5 rounds, unkeyed, the complete 256-bit digest (blake3-r5-prefix-v1). They are found as a collision g(x) = g(y) of the walk g(x) = f(x) XOR q, f(x) = digest(0^32 || x), q = 0 here (the digest planes are stored upright); g(x) = g(y) iff f(x) = f(y). Plain birthday search; no differential or structural property of the 5 rounds is used.")
R.append("Machine, a declared convention of this entry (H3, supporting): a classical load/store machine with 256-bit words, 256-bit immediates and %d registers under collision-frontier-v5 (the profile fixes the word size and charges loads and stores, not a register count); 1054 operations (C of blake3-r5) to the unit. Charged: every add, AND, OR, XOR, shift, compare, branch, register move, load, store and the random word. The main loop evaluates 256 trails bit-sliced with pivot full adders: %d operations per batch (a rolled step of %s operations: rounds 1-2 straight, rounds 3-5 as 3 iterations of one generic round, with %d register moves of the message permutation after each of 2 iterations, %d loop-control operations, no zero-message folding in the loop; a %d-operation stage-1 test, 3 loop operations); it needs %d registers. Every instruction is charged 36 bytes, loop control included. Smaller register files are not priced." % (b.REGISTERS, body, fm(st.ops), len(M_), loopc, filt, st.regs))
R.append("time_log2 is an upper bound: every term of proof.md Section 3.4 is enforced by a halt of the program (B batches, e2max stage-1 hits, %d table keys, 1 cut trail, a recovery of two passes of at most c + 2^48 batches each, one recovery), and the bound charges each at its limit. The attempt is single: one fresh uniform 256-bit word r, no restart, no amplification, no stored collision, no advice; m0..m7 = 0. Distinguished points: low 32 bits zero and the next 90 bits below %d (density %d / 2^122). The generator that builds the circuit at setup is charged (%s operations)." % (tmax, Tp, Tp, fm(lg["gen"])))
R.append("Memory: %d table entries of 10 bytes (%d bytes) plus %d bytes of code (%d instructions of 36 bytes, the rolled step %d of them) plus 16,384 bytes of counters and the plane copy plus %s bytes for the %d registers: %d bytes = 2^%.5f; claimed as 20, the log2 of the 2^20-byte budget (the scalar policy adds 0 to time_log2). The circuit generator that runs at setup is a two-pass C program charged at %d compiled instructions (%d bytes) and %d bytes of scratch, held in the region that the table and the register file occupy once the search runs: setup phase %d bytes, search phase %d (proof 3.6). It was run in a sandbox capped at 1,048,576 bytes of guest memory and as a native binary with its address space capped at 2^20 bytes; both emit the identical program." % (tmax, b.ENTRY * tmax, code, st.instr + filt + b.LOOP_OPS + b.other_code(st), st.instr, fm(b.REGFILE), b.REGISTERS, mem, log2(mem), b.GEN_CODE, genimg, sc[0], ph1, ph2))
R.append("Success probability at least 0.39: Lemma 2 of proof.md Section 4 proves it for a uniformly random function from the lazy-sampling hazard (a supermartingale over the evaluations, no conditioning on which trails finish, the cut count bounded by a proved theorem; bound %.5f, exact certificate in Appendix A, none spare); H1, score-critical (clauses (a) to (d), declared and not proved), says the real attempt succeeds at least as often. Nothing else in the bound is heuristic. If the hazard were (1 - eps) / N the plan needs extra time: %s." % (ls["P_lower"], sens_short))
R.append("The declared experiments run this program in the organizer sandbox: bsrho-n18 (one attempt of the 256-lane search per trial at width 18, DP = low 2 bits zero) and proj-k0-w256 (2048 points of the target at width 256 per trial, a pair when two digests agree in the low 21 bits). Each returns pairs whose complete 5-round digests agree in the stated low bits. They are program checks: no number of the claim is estimated from their counts and no sampling premise is used. No outside code or library is used.")
R.append("No nonuniform advice and no prefix: q = 0 is derived by the generator. Credited derivative: our own 4a9f31b8 (the same search, plan method and proof, with a straight-line five-round step), a2e94df7 (the rolled step, generator, ledger and proof at 7 rounds), a6ee439c (the same program and proof at 4 rounds), 41b32afc, 75d5e1f9, 62cfd777 (3 rounds), 0a9640ed and 3356413f (program, search, ledger, register convention), and jungjipdo's 6ae36351 for the pivot full adder and the mask walk g = f XOR q (re-implemented from its proof text; no file of it used or run). preprocessing_log2 = %.1f is the setup and generator row, which is also inside time_log2." % preclaim)
for r in R:
    assert len(r) <= 1024, (len(r), r[:60])
claim = {"schema_version": 3, "target_profile": "blake3-r5-prefix-v1", "attack_class": "ordinary-collision", "rounds": 5,
         "claim": {"time_log2": TL, "time_unit": "target-compressions", "memory_log2_bytes": 20, "preprocessing_log2": preclaim, "success_probability": 0.39, "nonuniform_advice_log2_bytes": 0},
         "restrictions": R, "baseline_improved": "blake3-r5-nominal-v2", "certificate_manifest": "certificates/manifest.json", "experiment_manifest": "experiments/manifest.json",
         "heuristics": [H1, H3], "submission_state": "ready", "lane": "exploratory"}
for h in claim["heuristics"]:
    for k, v in h.items():
        if isinstance(v, str):
            assert len(v) <= 4096, (h["id"], k, len(v))
w(os.path.join(PKG, "blake3", "claim.json"), json.dumps(claim, indent=2, ensure_ascii=False) + "\n")

m18 = "ffff03" + "00" * 29; m21 = "ffff1f" + "00" * 29; zero = "00" * 32
manifest = {"schema_version": 1, "experiments": [
    {"id": "bsrho-n18", "kind": "python-message-pairs-v1",
     "scope": ("The blake3-r5-prefix-v1 target with 64-byte messages 0^32 || x (one block, flags 11), collision of the low 18 bits of the complete digest. Each trial runs ONE attempt of the shipped 256-lane search on the walk g = f XOR q (plan(18): distinguished points with the low 2 bits zero, %d batches of 256 lanes, cut rule, table, recovery on the packed circuit) from a word derived from the trial seed, with no amplification, "
               "and returns the two 64-byte messages 0^32 || x and 0^32 || y when the attempt found a pair, two nulls otherwise. The same program also runs the same attempt on an ideal function of the same width (keyed blake2b) and one family-law run with a fresh key at n = 12; these are reported as untrusted observations only." % b.plan(18)["B"]),
     "hypothesis": ("For every returned pair the two messages are distinct and their complete 5-round digests agree in the low 18 bits (digest bytes 0 and 1 and the low 2 bits of byte 2). This is exact: the program recovers a merge of two trails of the walk g = f XOR q at width 18. "
                    "The number of trials that return a pair is the number of single attempts that succeeded; it is reported as a program check, with the ideal-function control as an untrusted observation, and no probability, interval or sampling inference is drawn from it. Observations (untrusted, the program's own): target_ok, ideal_ok, batches, halts, t1_steps. Not shown: any width-256 cost or success probability."),
     "program": "experiments/bsrho.py", "event": {"kind": "digest-xor-mask", "mask_hex": m18, "expected_hex": zero}},
    {"id": "proj-k0-w256", "kind": "python-message-pairs-v1",
     "scope": ("The blake3-r5-prefix-v1 target with 64-byte messages 0^32 || x at full width 256. Each trial evaluates 2048 points x with the shipped bit-sliced circuit (source by trial index mod 3: uniform inputs from the seed, counter inputs r + i, iterates of g from 256 seed-derived starts), recovers the digests from the stored planes by XOR with q, "
               "and returns two distinct points whose complete digests agree in the low 21 bits when the set contains such a pair, two nulls otherwise. Untrusted observations: the numbers of equal pairs in seven 21-bit projections of the digest."),
     "hypothesis": ("For every returned pair the two messages 0^32 || x and 0^32 || y are distinct and their complete 5-round digests agree in the low 21 bits (digest bytes 0 and 1 and the low 5 bits of byte 2). This is exact: it checks the bit-sliced circuit, the mask q and the message construction at full width. "
                    "The number of returned pairs and the projection counts are reported as program checks, not as estimates, and no inference is drawn from them. Observations (untrusted): source, dup_w0, dup_w3, dup_w7, dup_xor8, dup_sum8, dup_p01, dup_p23. Not shown: collision structure at 2^128 evaluations."),
     "program": "experiments/bsrho.py", "event": {"kind": "digest-xor-mask", "mask_hex": m21, "expected_hex": zero}}]}
w(os.path.join(PKG, "blake3", "experiments", "manifest.json"), json.dumps(manifest, indent=2) + "\n")

deps = [
    {"submissionId": PRED["id"],
     "rationale": "Our own B3R5b (blake3 round 5, time_log2 125.00951, memory_log2_bytes 20.37855, scalar score 125.38806): the search, the plan method, the success proof (Section 4), the experiments and the ledger method of this entry are those of 4a9f31b8. Changed: the step is the rolled program of a2e94df7 (rounds 1-2 straight, rounds 3-5 as 3 iterations of one generic round, charged register moves and loop control), so that the whole program fits in 2^20 bytes and the memory term is removed; the table, Tp, B and c are re-planned.",
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."},
    {"submissionId": "a2e94df7-bff4-4461-ad40-7f75930cb241",
     "rationale": "Our own B3R7c (blake3 round 7, time_log2 125.29113, memory_log2_bytes 20): the rolled round body, its circuit generator in C, the register file of 1,856, the loop and message-permutation charges, the plan method and Section 4 (Lemma 2 v2) of this entry are those of a2e94df7, taken from seven rounds to 5 (ROUNDS and the unit 1054 only; the recovery circuit, Tp, B, c and the table follow).",
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."}]
w(os.path.join(PKG, "dependencies.json"), json.dumps(deps, indent=2) + "\n")
print(S31, S32, S33, S34, S35, S36, S4, S5, S6, S7)

nt = note.format(**vals)
w(os.path.join(PKG, "submission-note.md"), nt)
print("note bytes", len(nt.encode()), "TL", TL, "raw", TLraw, "preclaim", preclaim, "mem", mem, "ph1", ph1)
