"""Makes build_all8.py (builder of the B3R7b package) from ../b7/build_all.py.  usage: python3 -B patch_build8.py"""
import re
s = open("../b7/build_all.py", encoding="utf-8").read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new)


def cut(a, b, new=""):
    global s
    i = s.index(a)
    j = s.index(b, i)
    s = s[:i] + new + s[j:]


rep('"""Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the blake3-r7 entry from the program\'s own numbers.',
    '"""Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the blake3-r7 entry B3R7b (rolled round body) from the program\'s own numbers.')
rep("TL4 = 125.06000", "TL4 = 125.06000\nTL7, SC7, MT7 = 125.05397, 125.92083, 0.86686")
# --- drop the smaller-file block
cut("rows_R = {}", "stats_txt = open(", "")
# --- scan
cut("_ml = b.MEM_LIMIT", "CPORT = json.load", '''_ml = b.MEM_LIMIT
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
''')
rep('PYGEN = json.load(open(os.path.join(HERE, "ext", "pygen_rss.json")))\n', "")
rep('assert CPORT["identical"] and CPORT["instructions"] == st.ops and CPORT["registers"] == 771 and CPORT["calls"] == 2 * st.gen_calls',
    'assert CPORT["identical"] and CPORT["instructions"] == st.instr and CPORT["registers"] == st.regs and CPORT["calls"] == 2 * st.gen_calls')
rep('CPORT["scratch"] == sc[0] and CPORT["nodes"] == sc[2]', 'CPORT["scratch"] == sc[0] and CPORT["nodes"] + 1 == sc[2]')
rep("assert b.MEM_LIMIT >= mem and b.MEM_LIMIT - mem <= 64", "assert b.MEM_LIMIT >= mem and b.MEM_LIMIT - mem <= 64 + b.ENTRY - 1")
rep("memterm = memlog2 - 20", "memterm = max(0, memlog2 - 20)\nassert memterm == 0 and mem <= 2 ** 20")
# --- measured text
cut("measured = (", "statslines = ", '''measured = ("(i) the circuit generator written in freestanding C (source embedded in `experiments/bsrho.py` as `GEN_C`, printed by `python3 bsrho.py --gen-c`, %s bytes) compiled to WebAssembly (clang -Os, 2,048-byte shadow stack) and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes (the memory budget 2^20) emits the identical program: "
            "%s instructions, %d registers, %s nodes (larger segment), %s primitive calls (both passes of both segments), q = 0, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total %s bytes (the final code region %s, the counters %s, its own scratch %s); the guest uses %d pages (highest nonzero byte %s) (the generator's code image, charged in the model at %s bytes, lies outside the guest memory in this sandbox). It needs %s wasm operations, below the %s word operations the ledger charges for the generator. "
            "(ii) The same C program as a static x86-64 binary without libc (a %s-byte text segment, %s bytes of bss) runs under `prlimit --as=%s` (its whole address space capped at 2^20 bytes) and writes the identical program (sha256 equal); it does not start under %s of address space. "
            "(iii) The entry's generator is the C program of (i) and (ii), run within the caps shown; the Python generator in `experiments/bsrho.py` is only the reference whose output text the C program reproduces (sha256 equal)." % (
                fm(CPORT["src_bytes"]), fm(CPORT["instructions"]), CPORT["registers"], fm(CPORT["nodes"]), fm(CPORT["calls"]), fm(CPORT["static_total"]), fm(CPORT["code_region"]), fm(CPORT["counters"]), fm(CPORT["scratch"]),
                CPORT["pages"], fm(CPORT["highest_nonzero_byte"]), fm(genimg), fm(CPORT["fuel"]), fm(lg["gen"]), fm(NATIVE["text"]), fm(NATIVE["bss"]), fm(NATIVE["as_ok"]), fm(NATIVE["as_fail"])))
''')
# --- vals
rep("    PH=st.ops, perlane=st.ops / 256, tmax=fm(tmax),", "    PH=fm(st.ops), perlane=st.ops / 256, tmax=fm(tmax),")
rep('PH7=PH7, PH7p=PH7 + b.RECOVER_EXTRA, gates=st.gates, xor=st.by["x"], and_=st.by["a"], or_=st.by["o"],', "PH7=PH7, PH7p=PH7 + b.RECOVER_EXTRA,")
rep("regs=771, spareregs=800 - 771, ", "regs=b.REGISTERS, usedregs=st.regs, spareregs=b.REGISTERS - st.regs, regbytes=fm(b.REGFILE), tempbody=st.regs - b.TB, ")
rep("log2setup=log2((b.SETUP_FIXED + lg[\"gen\"]) / UNIT), instr=fm(body + b.other_code(st)),", "log2setup=log2((b.SETUP_FIXED + lg[\"gen\"]) / UNIT), instr=fm(st.instr + filt + b.LOOP_OPS + b.other_code(st)),")
rep("gencalls=fm(2 * st.gen_calls), gencalls1=fm(st.gen_calls), gen=fm(lg[\"gen\"])", "gencalls=fm(2 * st.gen_calls), gencalls1=fm(st.gen_calls), gen=fm(lg[\"gen\"])")
rep("peak=st.peak_live(),", "")
rep("nodes=fm(sc[2]), usesbytes=fm(sc[1])", "nodes=fm(sc[2]), usesbytes=fm(sc[1])")
rep("rows35=rows35, note256=note256, t512_note=t512_note,", "")
rep("nref_scalar=300, nref_step=fm(8192)", "nref_scalar=300, nref_step=fm(8192)")
rep("dTL=TL - 125.02375,", "dTL=TL - 125.02375, dTL7=TL - TL7, dSC7=TL + memterm - SC7, mem7term=MT7,")
rep("memterm=memterm, score=TL + memterm,", "memterm=memterm, score=TL + memterm,")
rep(" qweight=bin(st.qint).count(\"1\"),", " qweight=bin(st.qint).count(\"1\"),")
# new tokens
rep("def need(text, label):", '''_g = b.Gen(256)
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
            movn=fm(movn), ctln=loopc, Alen=fm(len(A_)), stepinstr=fm(st.instr), PH1=fm(45974), codebytes1=fm(1755288), savedinstr=fm(45974 - st.instr), PHdiff=fm(st.ops - 45974), PHpct=100 * (st.ops / 45974 - 1),
            nrolled=fm(16384), n0=fm(_L["nodes"]), n1=fm(1 + 1024 + len(B_)), Nunused=0)
def need(text, label):''')
rep('tpl = open(os.path.join(HERE, "proof_t.md"), encoding="utf-8").read()', 'tpl = open(os.path.join(HERE, "proof_t8.md"), encoding="utf-8").read()')
rep('note = open(os.path.join(HERE, "note_t.md"), encoding="utf-8").read()', 'note = open(os.path.join(HERE, "note_t8.md"), encoding="utf-8").read()')
# --- H1 / H3 / restrictions / deps
rep("(f(x) = the complete 7-round digest of the 64-byte message 0^32 || x, q the fixed digest-plane mask of the generated circuit)", "(f(x) = the complete 7-round digest of the 64-byte message 0^32 || x, q = 0 the digest-plane mask of the generated program)")
cut('H3 = dict(', 'R = []', '''H3 = dict(
    id="H3-machine-convention", role="supporting",
    statement=("Declared machine convention of this entry (supporting; a convention, not a claim about the benchmark; the register-file convention of our 0a9640ed and 1cd0dd3b, which the judges rated or have not yet rated, here with %d registers). The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = %d registers of 256 bits, counted as %s bytes of memory, and charges every operation, load, store and register move. The main loop (one batch of 256 trails, %d operations: the %s-operation generated step, a %d-operation stage-1 test and 3 loop operations) "
               "has no load or store; it has the register moves of the message permutation (576 plane copies after each of the first four iterations of the round loop), the setup of the message slots (%d operations), the complements (%d) and the loop control (%d operations), all counted. The generated program uses %d registers; the rest are for the loop counters and handlers. The organizer's reference count C(r7) = 1470 is used only as the unit. Every instruction is charged 36 bytes of code, also the three-register ones and the loop-control ones (no decode is free), and the code of the circuit generator is charged at 36 bytes per instruction of its compiled form (%d instructions, proof.md 3.6)." % (b.REGISTERS, b.REGISTERS, fm(b.REGFILE), body, fm(st.ops), filt, winit, nots, loopc, st.regs, b.GEN_CODE)),
    scope="The loop body of one batch of 256 lanes, its stage-1 test and the handlers; table accesses, recovery, events and setup are charged at the stated bounds including loads and stores of their words.",
    extrapolation="A machine with fewer than %d registers would add loads and stores to the loop body; that cost is not priced for the rolled program (proof.md 3.5) and not claimed. The claim assumes the declared %d." % (st.regs, b.REGISTERS),
    evidence_ids=[S31, S32, S33, S35, S36, S7],
    limitations="The benchmark profile does not fix a register count or an instruction set; the declaration is this entry's own, as is the reading of the loop (counted loop-control operations and instructions, register moves for the message permutation, no free decode or re-indexing). The counts (%s operations, %s instructions, %d registers) are produced by the generator in the program (a C port emits the identical program in a memory-capped sandbox, proof 3.6); smaller register files are not priced." % (fm(st.ops), fm(st.instr), st.regs),
)
''')
cut('R.append("Two distinct 64-byte messages', 'R.append("time_log2 is an upper bound', '''R.append("Two distinct 64-byte messages 0^32 || x and 0^32 || y (x != y, 256-bit little-endian integers): one chunk of one block, chaining value IV, counter 0, length 64, flags 11 (CHUNK_START|CHUNK_END|ROOT), 7 rounds, unkeyed, the complete 256-bit digest (blake3-r7-prefix-v1). They are found as a collision g(x) = g(y) of the walk g(x) = f(x) XOR q, f(x) = digest(0^32 || x), q = 0 here (the digest planes are stored upright); g(x) = g(y) iff f(x) = f(y). Plain birthday search; no differential or structural property of the 7 rounds is used.")
R.append("Machine, a declared convention of this entry (H3, supporting): a classical load/store machine with 256-bit words, 256-bit immediates and %d registers under collision-frontier-v5 (the profile fixes the word size and charges loads and stores, not a register count); 1470 operations (C of blake3-r7) to the unit. Charged: every add, AND, OR, XOR, shift, compare, branch, register move, load, store and the random word. The main loop evaluates 256 trails bit-sliced with pivot full adders: %d operations per batch (a rolled step of %s operations: rounds 1-2 straight, rounds 3-7 as 5 iterations of one generic round, with %d register moves of the message permutation after each of 4 iterations, %d loop-control operations, no zero-message folding in the loop; a %d-operation stage-1 test, 3 loop operations); it needs %d registers. Every instruction is charged 36 bytes, loop control included. Smaller register files are not priced." % (b.REGISTERS, body, fm(st.ops), len(M_), loopc, filt, st.regs))
''')
rep('Memory: %d table entries of 10 bytes (%d bytes) plus %d bytes of code (%d instructions of 36 bytes) plus 16,384 bytes of counters and the plane copy plus 25,600 bytes for the 800 registers: %d bytes = 2^%.5f; claimed as 2^%s (above 2^20, so the scalar policy adds %.5f to time_log2). The circuit generator that runs at setup is a two-pass C program charged at %d compiled instructions (%d bytes) and %d bytes of scratch, held in the region that the table and the register file occupy once the search runs: setup phase %d bytes, search phase %d (proof 3.6). It was run in a sandbox capped at 1,900,544 bytes of guest memory and as a native binary under prlimit at the claimed memory; both emit the identical program." % (tmax, b.ENTRY * tmax, code, body + b.other_code(st), mem, log2(mem), memlog2, memterm, b.GEN_CODE, genimg, sc[0], ph1, ph2))',
    'Memory: %d table entries of 10 bytes (%d bytes) plus %d bytes of code (%d instructions of 36 bytes, the rolled step %d of them) plus 16,384 bytes of counters and the plane copy plus %s bytes for the %d registers: %d bytes = 2^%.5f; claimed as 20, the log2 of the 2^20-byte budget (the scalar policy adds 0 to time_log2). The circuit generator that runs at setup is a two-pass C program charged at %d compiled instructions (%d bytes) and %d bytes of scratch, held in the region that the table and the register file occupy once the search runs: setup phase %d bytes, search phase %d (proof 3.6). It was run in a sandbox capped at 1,048,576 bytes of guest memory and as a native binary with its address space capped at 2^20 bytes; both emit the identical program." % (tmax, b.ENTRY * tmax, code, st.instr + filt + b.LOOP_OPS + b.other_code(st), st.instr, fm(b.REGFILE), b.REGISTERS, mem, log2(mem), b.GEN_CODE, genimg, sc[0], ph1, ph2))')
rep("No nonuniform advice and no prefix: the mask q is derived by the generator. Credited derivative: our own a6ee439c (the same program and proof at 4 rounds), 41b32afc,",
    "No nonuniform advice and no prefix: q = 0 is derived by the generator. Credited derivative: our own 1cd0dd3b (the same search, plan method and proof, with a straight-line seven-round step), a6ee439c (the same program and proof at 4 rounds), 41b32afc,")
rep('"memory_log2_bytes": memlog2,', '"memory_log2_bytes": 20,')
rep('"schema_version": 3, "target_profile": "blake3-r7-prefix-v1"', '"schema_version": 3, "target_profile": "blake3-r7-prefix-v1"')
# dependencies: 1cd0dd3b first
rep('deps = [\n    {"submissionId": "a6ee439c-5b82-41f2-8acb-9917c8c70756",',
    '''deps = [
    {"submissionId": "1cd0dd3b-eb60-4572-a75f-937cd771ec4a",
     "rationale": "Our own B3R7 (time_log2 125.05397, memory 2^20.86686, scalar score 125.92083), filed 10-15: the search, the plan method, the proof Section 4 (the supermartingale Lemma 2, clause (d) of H1), the experiments, the generator's use-count and packing changes and the ledger of this entry are those of 1cd0dd3b. Changed: the step is a rolled program (rounds 1-2 straight, rounds 3-7 as 5 iterations of one generic round, the message permutation done by charged register moves, loop control charged) instead of a straight line, so that the whole program fits in 2^20 bytes and the memory term (0.86686 bit) is removed; the price is a larger step (55,210 operations against 45,974), a re-planned table (the largest that fits in 2^20) and a larger register file (1,856).",
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."},
    {"submissionId": "a6ee439c-5b82-41f2-8acb-9917c8c70756",''')
rep('Changed: the round count and unit (C = 1470), the step (45,974 gates), the generator\'s use counts (one byte per node) and node packing, the plan (Tp, B, c, table size), and the memory statement: the program no longer fits in 2^20 bytes, so memory is claimed above it and the scalar score pays for it (proof Section 3.8).',
    'Changed (by 1cd0dd3b and here): the round count and unit (C = 1470), the step (a rolled program here), the plan (Tp, B, c, table size), and the memory statement: the program fits in 2^20 bytes here (proof Section 3.8).')
s = s.replace('"evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."}', '"evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."}')
open("build_all8.py", "w", encoding="utf-8", newline="\n").write(s)
print("build_all8.py", len(s))
