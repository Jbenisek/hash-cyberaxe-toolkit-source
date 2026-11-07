"""Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the pivot/mask-walk entry from the program's own numbers.
Run:  python -B build_all.py   (after stats_out.txt, appA.out, organizer_summary.txt, gen_c/cport.json exist)."""
import sys, json, os
from math import log2, exp, log
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "pkg")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(PKG, "blake3", "experiments"))
import bsrho as b

p = b.plan(256); lg = b.ledger(p); ls = b.loss(p); st = b.step256()
ph, filt, body, code, tmax = b.machine_constants(st)
PH7 = b.packed_circuit(st.qwords)[1]
N = lg["total"]; TL = 124.8123
assert abs(log2(N / 638) - 124.81229808) < 1e-7 and TL >= log2(N / 638) and TL - log2(N / 638) < 1e-5
parts = lg["parts"]
x = float(b.LAMBDA); slope = 2 * x * exp(-x)
f1 = ls["cut_one_trail"]; mu = ls["mean_cut_trails"]
pk = [exp(-mu) * mu ** j / (1, 1, 2)[j] for j in range(3)]
cut1 = pk[1] * (f1 - 1.5e-4) * slope; cut2 = pk[2] * (2 * f1 - 1.5e-4) * slope; cut3 = (1 - sum(pk)) * (1 - exp(-x))
cutdef = cut1 + cut2 + cut3
assert abs(cutdef - ls["cut_deficit"]) < 1e-9, (cutdef, ls["cut_deficit"])
L = p["L"]; Q = p["Q"]
U = (Q * (1 - b.CUTLOSS) - b.INFLIGHT * L - 1) / 2 ** 128
sumloss = ls["sum"]
eps = 0
for k in range(1, 20000):
    e = k / 1e5
    if 1 - exp(-x * (1 - e)) - sumloss >= 0.39:
        eps = e
rows_R = {}
for R in (1024, 512, 256):
    lgR = b.ledger(None, None, R); lsR = b.loss(lgR["plan"])
    rows_R[R] = (b.step256().spill_ops(R) if R < 1024 else 0, lgR["body"], lgR["plan"]["tmax"], lgR["plan"]["Tp"], log2(lgR["total"] / 638), lsR["P_lower"])
    assert lsR["P_lower"] >= 0.39, (R, lsR["P_lower"])
stats_txt = open(os.path.join(HERE, "stats_out.txt")).read().strip().split("\n")
appA = open(os.path.join(HERE, "appA.py")).read().rstrip("\n")
appOut = open(os.path.join(HERE, "appA.out")).read().rstrip("\n")
orgsum = open(os.path.join(HERE, "organizer_summary.txt")).read().strip().split("\n")
fm = lambda v: "{:,}".format(int(v))
sc = b.gen_scratch()
GENEXACT = 2036
CPORT = json.load(open(os.path.join(HERE, "gen_c", "cport.json")))
measured = ("(i) the circuit generator written in freestanding C (source embedded in `experiments/bsrho.py` as `GEN_C`, printed by `python3 bsrho.py --gen-c`, %s bytes) compiled to WebAssembly and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes emits the identical program: "
            "%s instructions, %d registers, %s nodes, %s primitive calls, the same q, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total %s bytes, of which %s are the final code region (36-byte records) and %s the counters; its own scratch peak is %s bytes (emit phase; trace phase %s), against the model's %s and %s, and it needs %s wasm operations, below the %s word operations the ledger charges for the generator. "
            "The guest links in %d pages and leaves %s bytes of the 1 MiB unused (the generator's code image, charged in the model at %s bytes, lies outside the guest memory in this sandbox). "
            "(ii) The Python generator alone (`ext/gen_only.py`, not shipped) has a peak resident set of 83.0 MB under memmeter (the bare interpreter 9.8 MB); that is the footprint of the interpreter and its objects, not of the machine model, and it is not charged." % (
                fm(CPORT["src_bytes"]), fm(CPORT["instructions"]), CPORT["registers"], fm(CPORT["nodes"]), fm(CPORT["calls"]), fm(CPORT["static_total"]), fm(CPORT["code_region"]), fm(CPORT["counters"]),
                fm(CPORT["emit_scratch"]), fm(CPORT["trace_scratch"]), fm(sc[2]), fm(sc[1]), fm(CPORT["fuel"]), fm(lg["gen"]), CPORT["pages"], fm(CPORT["spare"]), fm(b.GEN_CODE * b.INSTR_BYTES)))
t18, t21 = "2.7", "4.1"
statslines = "\n".join("    " + s.rstrip() for s in stats_txt)
orgl = "\n".join("    " + s for s in orgsum)
ph1, ph2 = b.phase_bytes(code, tmax)
mem = 25 * tmax + code + b.REGFILE + b.COUNTERS + b.ADVICE
vals = dict(
    PH=st.ops, perlane=st.ops / 256, tmax=fm(tmax), Tp=p["Tp"], log2L=log2(L), Lnum=L.numerator, Lden=L.denominator, B=p["B"], Qratio=Q / 2 ** 128,
    e2max=p["e2max"], c=p["c"], log2c=log2(p["c"]), regs=771, spareregs=1024 - 771, PH7=PH7, PH7p=PH7 + b.RECOVER_EXTRA, gates=st.gates, xor=st.by["x"], and_=st.by["a"], or_=st.by["o"],
    unit=st.ops / 256 / 638, filt=filt, body=body, setupfixed=fm(b.SETUP_FIXED), gencalls=fm(st.gen_calls), gen=fm(lg["gen"]), setupall=fm(b.SETUP_FIXED + lg["gen"]),
    log2setup=log2((b.SETUP_FIXED + lg["gen"]) / 638), instr=fm(body + b.OTHER_CODE), main=fm(parts["main"]), mainsci="%.4e" % float(parts["main"]),
    slices_sci="%.3e" % float(parts["slices"]), hits_sci="%.4e" % float(parts["stage1_hits"]), events=fm(parts["events"]), log2capr=log2(p["capr"]), rec_sci="%.4e" % float(parts["recovery"]),
    gencodeexact=fm(GENEXACT), gencode=fm(b.GEN_CODE), gencodebytes=fm(b.GEN_CODE * b.INSTR_BYTES), nodes=fm(sc[3]), nbytes=fm(4 * sc[3]), trace_phase=fm(sc[1]), emit_phase=fm(sc[2]), scratch=fm(sc[0]),
    ph1=fm(ph1), memspare=b.MEM_LIMIT - ph2, region=fm(b.gen_idle(tmax)), genneed=fm(b.GEN_CODE * b.INSTR_BYTES + sc[0]), N=fm(N), Nsci="%.6e" % N, Nunits="%.4e" % (N / 638), log2N=log2(N / 638),
    TL=TL, slack=TL - log2(N / 638), pmain=100 * float(parts["main"]) / float(N), prec=100 * float(parts["recovery"]) / float(N), peak=st.peak_live(),
    M=b.INFLIGHT, tailages=exp(-256 * (b.INFLIGHT / 256 - 1 - log(b.INFLIGHT / 256))), f1=f1, trails=ls["trails"], mu=mu, pk0=pk[0], pk1=pk[1], pk2=pk[2], pk3=1 - sum(pk),
    allow=1.5e-4 / f1, d1=(f1 - 1.5e-4) * slope, d2=(2 * f1 - 1.5e-4) * slope, slope=slope, cutdef=cutdef, Uratio=U, log2inside=log2(ls["inside_trail"]), inside=ls["inside_trail"],
    log2keys=56 + log2(p["Tp"]), keyfm=ls["key_false_match"], tmaxp1=fm(tmax + 1), log2cap=log2(ls["table_capacity"]), cap=ls["table_capacity"], mu2=float(Q) / 2 ** 32, mu2c=float(Q) / 2 ** 32 * (2 * log(2) - 1),
    sumloss=sumloss, Pl=ls["P_lower"], margin=ls["P_lower"] - 0.39, eps=eps, eps_cost=0.5 * log2(1 / 0.99), statslines=statslines, orgsum=orgl, B18=b.plan(18)["B"], t18=t18, t21=t21,
    tablebytes=fm(tmax * 25), codebytes=fm(code), mem=fm(mem), appA=appA, appOut=appOut, qweight=bin(st.qint).count("1"), measured=measured, preclaim=14.2,
    nref_scalar=300, nref_step=fm(8192), nref_packed=448,
)
for R in (1024, 512, 256):
    s_, b_, t_, tp_, tl_, pl_ = rows_R[R]
    vals.update({"s%d" % R: fm(s_), "b%d" % R: fm(b_), "t%d" % R: fm(t_), "tp%d" % R: tp_, "tl%d" % R: tl_, "pl%d" % R: pl_})
tpl = open(os.path.join(HERE, "proof_t.md"), encoding="utf-8").read()
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
Tp, M = p["Tp"], b.INFLIGHT

H1 = dict(
    id="H1-random-function-model", role="score-critical",
    statement=("Model premise. Let F be a uniformly random function from 256-bit values to 256-bit values. For the fixed target, the probability that the single attempt of the search succeeds, with the walk g(x) = f(x) XOR q (f(x) = the complete 3-round digest of the 64-byte message 0^32 || x, q the fixed digest-plane mask of the generated circuit), "
               "is at least the probability, over the fresh word r and a uniformly random F, that the same search succeeds when every evaluation of g is replaced by F (lazy sampling). In that model the pair-collision rate of evaluated inputs is 2^-256, the iterates have the first-collision law of a random mapping, and a point is a distinguished point (low 32 bits zero and the next 90 bits below %d) with probability %d / 2^122, independently; the success probability is then at least %.4f (proof.md Section 4, under the named approximations H2). This is a comparison of two success events, not a statement about the entropy of r." % (Tp, Tp, ls["P_lower"])),
    scope=("The fixed target blake3-r3-prefix-v1 restricted to 64-byte messages 0^32 || x, the fixed mask q, the 2^128-scale evaluation of g along about %d trails of mean length 2^%.2f started from r + t, 256 trails at a time. Not claimed for other messages, other round counts, or evaluations beyond this scale." % (round(ls["trails"], -2), log2(L))),
    extrapolation=("Declared and not proved. The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. The organizer experiments bsrho-n18 and proj-k0-w256 run this program on the real target at reduced width (the search at width 18) and at full width for 2048 points with 21-bit projections; they are program checks, no number of the claim is estimated from their counts, and no sampling premise is used. "
                   "Extrapolation from these sizes to width 256 and 2^128 evaluations is by the premise only. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01)."),
    evidence_ids=["experiment:bsrho-n18", "experiment:proj-k0-w256", S4, S5, S6],
    limitations=("A model premise about one fixed function, not a theorem: on the target the run is a deterministic function of r. It cannot be tested at width 256; the experiments reach width 18 and 21-bit projections of 2048 points per trial and do not measure collision structure at 2^128 evaluations. "
                 "A rate deficit eps above %.4f lowers the success probability below 0.39 and is repaired by at most 0.5 * log2(1/(1-eps)) more bits of time." % eps),
)
H2 = dict(
    id="H2-tail-approximations", role="supporting",
    statement=("Supporting, named approximations used in the computation for the random function F (proof.md Section 4, Lemma 2). (a) The age of the trail of each lane at the halt is dominated by an exponential with mean L = 2^%.2f and the 256 ages are independent, although restarts depend on the history of the run; the sum of the ages is then at most %d L except with probability 1e-6 (Chernoff). "
               "(b) The number of cut trails is Poisson with mean %.3f. (c) The probability loss for a cut trail is linear in the lost points with slope %.3f per unit of relative loss; a third cut is a halt charged as failure; the cut-trail deficit is %.2e. (d) Trail lengths are geometric with mean L; the expected number of colliding pairs inside one trail is at most Q L / N = %.1e. "
               "The key-false-match bound %.0e and the table-capacity Chernoff bound 2^%.1f are computations for F. The sum of the loss terms is below %.3e." % (log2(L), M, mu, slope, cutdef, ls["inside_trail"], ls["key_false_match"], log2(ls["table_capacity"]), ls["sum"])),
    scope="The parameters of plan(256) in experiments/bsrho.py: 256 lanes, DP density %d / 2^122, age cap 11 L, table of %d keys." % (Tp, tmax),
    extrapolation="Computations for the random function F under the approximations (a) to (d) only; the same formulas are implemented in plan(n) and loss(p), and the plan is exercised at n = 18 in the experiments.",
    evidence_ids=[S4, "experiment:bsrho-n18"],
    limitations="Not proved: independence of the 256 ages in the adaptive process, the Poisson law of the cut count and the linearisation of the cut loss; the cut-trail deficit costs %.2e of the %.2e of probability slack above 0.39 (the rest of the slack is margin)." % (cutdef, ls["P_lower"] - 0.39 + ls["sum"]),
)
H3 = dict(
    id="H3-machine-convention", role="score-critical",
    statement=("Score-critical premise of this entry (accepted as such for our 0a9640ed). The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = 1,024 registers of 256 bits, counted as 32,768 bytes of memory, and charges every operation, load, store and register move. The main loop (one batch of 256 trails, %d operations: the %d-operation generated step, a %d-operation stage-1 test and 3 loop operations) "
               "has no load, store or move because the generated line needs 771 registers (output plane j in the register of input plane j). The organizer's reference count C(r3) = 638 is used only as the unit. Every instruction is charged 36 bytes of code, also the three-register ones." % (body, st.ops, filt)),
    scope="The loop body of one batch of 256 lanes, its stage-1 test and the handlers; table accesses, recovery, events and setup are charged at the stated bounds including loads and stores of their words.",
    extrapolation="A machine with fewer than 771 registers would add loads and stores to every batch; proof.md 3.5 gives the cost (time_log2 %.4f with 512 registers, %.4f with 256). The claim assumes the declared 1,024." % (rows_R[512][4], rows_R[256][4]),
    evidence_ids=[S31, S32, S33, S35, S36, S7],
    limitations="The benchmark profile does not fix a register count; the declaration is this entry's own. The count %d is produced by the generator in the program (a C port of it emits the identical program in a 1 MiB sandbox, proof 3.6) and the register allocation by `allocate`; smaller files are priced by the program's Belady allocation of the straight line (an upper bound on what a better schedule needs)." % st.ops,
)
R = []
R.append("Two distinct 64-byte messages 0^32 || x and 0^32 || y (x != y, 256-bit little-endian integers): one chunk of one block, chaining value IV, counter 0, length 64, flags 11 (CHUNK_START|CHUNK_END|ROOT), 3 rounds, unkeyed, the complete 256-bit digest (blake3-r3-prefix-v1). They are found as a collision g(x) = g(y) of the walk g(x) = f(x) XOR q, f(x) = digest(0^32 || x), q a fixed 256-bit mask (the polarities of the digest planes of the generated circuit); g(x) = g(y) iff f(x) = f(y). Plain birthday search; no differential or structural property of the 3 rounds is used.")
R.append("Machine, a premise of this entry (H3): a classical load/store machine with 256-bit words, 256-bit immediates and 1,024 registers under collision-frontier-v5 (the profile fixes the word size and charges loads and stores, not a register count); 638 operations (C of blake3-r3) to the unit. Charged: every add, AND, OR, XOR, shift, compare, branch, register move, load, store and the random word. The main loop evaluates 256 trails bit-sliced with pivot full adders: %d operations per batch (%d gates, a %d-operation stage-1 test, 3 loop operations), no load, store or move, no complement operation; it needs 771 registers. Every instruction is charged 36 bytes. Smaller files are priced in proof.md 3.5 (%.4f at 512, %.4f at 256)." % (body, st.ops, filt, rows_R[512][4], rows_R[256][4]))
R.append("time_log2 is an upper bound: every term of proof.md Section 3.4 is enforced by a halt of the program (B batches, e2max stage-1 hits, %d table keys, 2 cut trails, a recovery of at most c + 2^48 batches, one recovery), and the bound charges each at its limit. The attempt is single: one fresh uniform 256-bit word r, no restart, no amplification, no stored collision, no advice; m0..m7 = 0. Distinguished points: low 32 bits zero and the next 90 bits below %d (density %d / 2^122). The generator that builds the circuit at setup is charged (%s operations)." % (tmax, Tp, Tp, fm(lg["gen"])))
R.append("Memory: %d table entries of 25 bytes (%d bytes) plus %d bytes of code (%d instructions of 36 bytes) plus 16,384 bytes of counters and the plane copy plus 32,768 bytes for the 1,024 registers: %d bytes <= 2^20; claimed as 2^20. The circuit generator that runs at setup is accounted in proof 3.6: %d instructions (%d bytes) and a peak scratch of %d bytes held in the region that the table and the register file occupy once the search runs; the setup phase needs %d bytes, the search phase %d. A C port of the generator, run in a sandbox capped at 1,048,576 bytes of guest memory, emits the identical program with a scratch peak of %d bytes (proof 3.6)." % (tmax, 25 * tmax, code, body + b.OTHER_CODE, mem, b.GEN_CODE, b.GEN_CODE * 36, sc[0], ph1, ph2, CPORT["emit_scratch"]))
R.append("Success probability at least 0.39 holds under the model premise H1 (proof.md Sections 4 and 5: success on the fixed target is at least success against a uniformly random function) and the named approximations H2, with the losses of Section 4 (about %.2e spent of %.2e available). If the pair-collision rate of the evaluated inputs were (1 - eps) of the random-mapping rate, the success probability stays at least 0.39 for eps <= %.4f, and at most 0.5 * log2(1/(1-eps)) more bits (0.0072 for eps = 0.01) restore it beyond." % (ls["sum"], ls["P_lower"] - 0.39 + ls["sum"], eps))
R.append("The declared experiments run this program in the organizer sandbox: bsrho-n18 (one attempt of the 256-lane search per trial at width 18, DP = low 2 bits zero) and proj-k0-w256 (2048 points of the target at width 256 per trial, a pair when two digests agree in the low 21 bits). Each returns pairs whose complete 3-round digests agree in the stated low bits. They are program checks: no number of the claim is estimated from their counts and no sampling premise is used. No outside code or library is used.")
R.append("No nonuniform advice and no prefix: the mask q is derived by the generator. Credited derivative: our 0a9640ed and 3356413f (program, search, ledger, register convention), and jungjipdo's 6ae36351 for the pivot full adder and the mask walk g = f XOR q (re-implemented from its proof text; no file of it used or run). preprocessing_log2 = %.1f is the setup and generator row, which is also inside time_log2." % vals["preclaim"])
for r in R:
    assert len(r) <= 1024, (len(r), r[:60])
claim = {"schema_version": 3, "target_profile": "blake3-r3-prefix-v1", "attack_class": "ordinary-collision", "rounds": 3,
         "claim": {"time_log2": TL, "time_unit": "target-compressions", "memory_log2_bytes": 20, "preprocessing_log2": vals["preclaim"], "success_probability": 0.39, "nonuniform_advice_log2_bytes": 0},
         "restrictions": R, "baseline_improved": "blake3-r3-nominal-v2", "certificate_manifest": "certificates/manifest.json", "experiment_manifest": "experiments/manifest.json",
         "heuristics": [H1, H2, H3], "submission_state": "ready", "lane": "exploratory"}
for h in claim["heuristics"]:
    for k, v in h.items():
        if isinstance(v, str):
            assert len(v) <= 4096, (h["id"], k, len(v))
w(os.path.join(PKG, "blake3", "claim.json"), json.dumps(claim, indent=2, ensure_ascii=False) + "\n")

m18 = "ffff03" + "00" * 29; m21 = "ffff1f" + "00" * 29; zero = "00" * 32
manifest = {"schema_version": 1, "experiments": [
    {"id": "bsrho-n18", "kind": "python-message-pairs-v1",
     "scope": ("The blake3-r3-prefix-v1 target with 64-byte messages 0^32 || x (one block, flags 11), collision of the low 18 bits of the complete digest. Each trial runs ONE attempt of the shipped 256-lane search on the walk g = f XOR q (plan(18): distinguished points with the low 2 bits zero, %d batches of 256 lanes, cut rule, table, recovery on the packed circuit) from a word derived from the trial seed, with no amplification, "
               "and returns the two 64-byte messages 0^32 || x and 0^32 || y when the attempt found a pair, two nulls otherwise. The same program also runs the same attempt on an ideal function of the same width (keyed blake2b) and one family-law run with a fresh key at n = 12; these are reported as untrusted observations only." % b.plan(18)["B"]),
     "hypothesis": ("For every returned pair the two messages are distinct and their complete 3-round digests agree in the low 18 bits (digest bytes 0 and 1 and the low 2 bits of byte 2). This is exact: the program recovers a merge of two trails of the walk g = f XOR q at width 18. "
                    "The number of trials that return a pair is the number of single attempts that succeeded; it is reported as a program check, with the ideal-function control as an untrusted observation, and no probability, interval or sampling inference is drawn from it. Observations (untrusted, the program's own): target_ok, ideal_ok, batches, halts, t1_steps. Not shown: any width-256 cost or success probability."),
     "program": "experiments/bsrho.py", "event": {"kind": "digest-xor-mask", "mask_hex": m18, "expected_hex": zero}},
    {"id": "proj-k0-w256", "kind": "python-message-pairs-v1",
     "scope": ("The blake3-r3-prefix-v1 target with 64-byte messages 0^32 || x at full width 256. Each trial evaluates 2048 points x with the shipped bit-sliced circuit (source by trial index mod 3: uniform inputs from the seed, counter inputs r + i, iterates of g from 256 seed-derived starts), recovers the digests from the stored planes by XOR with q, "
               "and returns two distinct points whose complete digests agree in the low 21 bits when the set contains such a pair, two nulls otherwise. Untrusted observations: the numbers of equal pairs in seven 21-bit projections of the digest."),
     "hypothesis": ("For every returned pair the two messages 0^32 || x and 0^32 || y are distinct and their complete 3-round digests agree in the low 21 bits (digest bytes 0 and 1 and the low 5 bits of byte 2). This is exact: it checks the bit-sliced circuit, the mask q and the message construction at full width. "
                    "The number of returned pairs and the projection counts are reported as program checks, not as estimates, and no inference is drawn from them. Observations (untrusted): source, dup_w0, dup_w3, dup_w7, dup_xor8, dup_sum8, dup_p01, dup_p23. Not shown: collision structure at 2^128 evaluations."),
     "program": "experiments/bsrho.py", "event": {"kind": "digest-xor-mask", "mask_hex": m21, "expected_hex": zero}}]}
w(os.path.join(PKG, "blake3", "experiments", "manifest.json"), json.dumps(manifest, indent=2) + "\n")

deps = [
    {"submissionId": "0a9640ed-558a-4f0a-aba8-45e89ffcfd7c",
     "rationale": "Our own entry for blake3 round 3 (124.96822, bit-sliced 256-lane chain step, declared 1,024-register file, 36-byte instruction charge; passed the judges). This entry keeps its target (64-byte message 0^32 || x, flags 11), program structure, trail-and-table search, handlers, recovery walk, ledger method, restated Lemma 2 and experiments, and changes the circuit generator (pivot full adders), the walk (g = f XOR q) and the success argument's wording (model premise, named approximations).",
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.6, 4, 5, 6, 7 and Appendix A."},
    {"submissionId": "3356413f-cd60-410c-8847-2266d6444ac5",
     "rationale": "Our own entry for blake3 round 3 (124.95448, same program with a fixed first block P as advice; passed the judges). Taken from it: the polarity-signal generator, the declared register-file layout and the generator code and peak-storage accounting of its Section 3.6 (restated here for the new generator); its two-block mode, prefix, scan and polarity climb are not used.",
     "evidence": "proof.md Sections 3.2, 3.6, 3.7 and 7."},
    {"submissionId": "6ae36351-5836-4a46-ad34-227688264123",
     "rationale": "jungjipdo's entry for blake3 round 3 (124.91252). Credited for two ideas, re-implemented here from the text of its proof Sections 3.3 and 3.4 (no file of that entry was used or run): the pivot full adder (the input whose polarity differs is the pivot; u = x ^ p, sum = u ^ y, carry = ((u & (y ^ p)) ^ p); five gates per bit) and the mask walk g = f XOR q (the digest planes are fed back as stored, so no complement and no polarity search are needed, and equality under g is equivalent to equality under f).",
     "evidence": "proof.md first paragraph and Sections 1, 3.2, 3.3 and 8."}]
w(os.path.join(PKG, "dependencies.json"), json.dumps(deps, indent=2) + "\n")
print(S31, S32, S33, S34, S35, S36, S4, S5, S6, S7)

note = open(os.path.join(HERE, "note_t.md"), encoding="utf-8").read()
vals.update(gain=124.91252 - TL, gain0=124.96822 - TL, gain3=124.95448 - TL, t512=rows_R[512][4], t256=rows_R[256][4], spare=b.MEM_LIMIT - mem, epsp=100 * eps, stats1=stats_txt[0], stats2=stats_txt[1],
            cpe=fm(CPORT["emit_scratch"]), cpst=fm(CPORT["static_total"]))
nt = note.format(**vals)
w(os.path.join(PKG, "submission-note.md"), nt)
print("note bytes", len(nt.encode()))
