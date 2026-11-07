import json, re
P = "../pkg/blake3/"
proof = open(P + "proof.md", encoding="utf-8").read().split("\n")
H = {}
for i, l in enumerate(proof, 1):
    m = re.match(r"^#+ (\S+)", l)
    if m:
        H[m.group(1)] = i
heads = sorted(H.values()) + [len(proof)]


def rng(key):
    a = H[key]
    b = min(h for h in heads if h > a) - 1
    return "proof:%d-%d" % (a, b)


eps = "0.0073 bit for eps = 0.01, 0.0370 bit for eps = 0.05, 0.0760 bit for eps = 0.10, 0.2075 bit for eps = 0.25"
restrictions = [
    "Two distinct 64-byte messages K || x and K || y (x != y, 256-bit little-endian integers; K = the fixed 32-byte prefix, words 0x80000000, 0, 0x80000000, 0, 0x70000000, 0, 0, 0): one chunk of one block, chaining value IV, counter 0, length 64, flags 11, 3 rounds, unkeyed, the complete 256-bit digest (blake3-r3-prefix-v1). Found as a collision g(x) = g(y) of the walk g(x) = f(x) XOR q, f(x) = digest(K || x), q the fixed mask of the polarities of the generated digest planes; g(x) = g(y) iff f(x) = f(y). Plain birthday search; no differential or structural property of the rounds is used.",
    "Machine, a declared convention (H3, supporting): load/store machine with 256-bit words, 256-bit immediates and 800 registers under collision-frontier-v5; 638 operations (C of blake3-r3) to the unit. Charged: every add, AND, OR, XOR, shift, compare, branch, register move, load, store and the random word. One batch of 256 trails is 16563 operations (16546 gates: pivot full adders and three-addend pair-carry columns, 14 for the stage-1 test, 3 for the loop), no load, store or move; it needs 773 registers. Code: 5 bytes per register-only gate, 36 bytes per other instruction (proof.md 3.1).",
    "time_log2 is an upper bound: every row of proof.md 3.4 is enforced by a halt and charged at its limit (B batches, pmax passing batches of the stage-1 test, e2max stage-1 hits, 124633 table keys, 1 cut trail, a recovery of at most c_r = ceil(12.4 L) pass-1 batches and 17 D pass-2 batches). Single attempt: one fresh uniform word r, no restart, no amplification, no stored collision. Distinguished points: low 32 bits zero and the next 90 bits below 1913. The generator run at setup (101,524,400 operations) and the offline choice of K (12,658,758,600) are charged.",
    "Memory: 124634 table slots of 7 bytes (872438 bytes: a quotient filter, 36 stored key bits + 16 implied by the slot, 17-bit trail number, 3 filter bits) + 134062 bytes of code (17186 gate words of 5 bytes, 1337 other instructions of 36 bytes) + 16,384 bytes of counters and plane copy + 25,600 bytes of registers + 32 bytes of advice K = 1048516 bytes = 2^19.99992; claimed as 20 (the scalar policy adds 0). The C generator (2149 wasm instructions, 77,364 bytes, scratch 21,576) runs at setup in the same region: setup phase 249418 bytes; run in a sandbox capped at 2^20 bytes of guest memory it emits the identical program.",
    "Success probability at least 0.39: Lemma 2 of proof.md Section 4 proves it for a uniformly random function from the lazy-sampling hazard (first collision of the run, detection delay, recovery cap, cut count and budgets bounded by proved statements; exact evaluation 0.39000000100041 in Appendix A); H1, score-critical (clauses (a) to (d), declared and not proved), says the real attempt succeeds at least as often. Nothing else in the bound is heuristic. A hazard (1 - eps) / N needs extra time: " + eps + ".",
    "The declared experiments run this program in the organizer sandbox: bsrho-n18 (one attempt of the 256-lane search per trial at width 18, DP = low 2 bits zero) and proj-k0-w256 (2048 points of the target at width 256 per trial, a pair when two digests agree in the low 21 bits). Each returns pairs whose complete 3-round digests agree in the stated low bits. They are program checks: no number of the claim is estimated from their counts and no sampling premise is used. No outside code or library is used.",
    "Advice: the 32-byte prefix K (nonuniform_advice_log2_bytes = 5), chosen offline by the stated coordinate descent (python3 bsrho.py --choose-key, 241 evaluations, charged in time_log2); preprocessing_log2 = 24.26 is the setup and generator row plus that choice, both inside time_log2. Credited derivative of mitchuski's 10ce9f59 (the three-addend pair-carry column, re-implemented from its note) and of our own 3c2d1220 (this program at three rounds); also credited in proof.md Section 8: jungjipdo's 6ae36351 (pivot full adder, mask walk) and 0xplemonade's 11d961ad (polarity-specific column idea).",
]
for r in restrictions:
    assert len(r) <= 1024, (len(r), r[:60])
h1 = {
    "id": "H1-random-function-model",
    "role": "score-critical",
    "statement": "Model premise, four clauses. Let F be a uniformly random function from 256-bit values to 256-bit values. For the fixed target, the probability that the single attempt of the search succeeds, with the walk g(x) = f(x) XOR q (f(x) = the complete 3-round digest of the 64-byte message K || x, K the fixed prefix, q the fixed digest-plane mask of the generated circuit), is at least the probability P_F, over the fresh word r and a uniformly random F, that the same search succeeds when every evaluation of g is replaced by F (lazy sampling). Clauses: (a) distinct evaluated inputs collide with probability 2^-256, uniform and independent outputs; (b) the iterates from r + t have the first-collision law of a random mapping; (c) a point is a distinguished point (low 32 bits zero and the next 90 bits below 1913) with probability 1913 / 2^122, independently of the collision events; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of g; given the whole history of the run and which later outputs are distinguished points, a fresh evaluation equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard of F). Proof.md Section 4 (Lemma 2) proves P_F >= 0.39 for F from the hazard alone; (d) is the premise that g has that hazard. This is a comparison of two success events, not a statement about the entropy of r. Nothing else in the success bound is heuristic.",
    "scope": "The fixed target blake3-r3-prefix-v1 restricted to 64-byte messages K || x, the fixed prefix K and mask q, the 2^128-scale evaluation of g along about 122000 trails of mean length 2^111.10 started from r + t, 256 trails at a time. Not claimed for other messages, other round counts, or evaluations beyond this scale.",
    "extrapolation": "Declared and not proved: an assumption, no proof is known. The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. The organizer experiments bsrho-n18 and proj-k0-w256 run this program on the real target at reduced width (the search at width 18) and at full width for 2048 points with 21-bit projections; they are program checks, reproducible observations consistent with the premise; no number of the claim is estimated from their counts, and no sampling premise is used. Extrapolation to width 256 and 2^128 evaluations is by the premise only. If the collision hazard is (1 - eps) / N instead of 1 / N, the plan needs, to restore 0.39: " + eps + ".",
    "evidence_ids": ["experiment:bsrho-n18", "experiment:proj-k0-w256", rng("4."), rng("5."), rng("6.")],
    "limitations": "A model premise about one fixed function, not a theorem: on the target the run is a deterministic function of r. It cannot be tested at width 256; the experiments reach width 18 and 21-bit projections of 2048 points per trial and do not measure collision structure at 2^128 evaluations. The bound has no margin above 0.39 (B is the least multiple of 10^24 that reaches it), so any hazard deficit is repaired by extra time, priced above: 0.0073 bit for eps = 0.01 (Tp 1903); 0.0370 bit for eps = 0.05 (Tp 1864); 0.0760 bit for eps = 0.10 (Tp 1815); 0.2075 bit for eps = 0.25 (Tp 1656).",
}
h3 = {
    "id": "H3-machine-convention",
    "role": "supporting",
    "statement": "Declared machine convention of this entry (supporting; a convention, not a claim about the benchmark; the register-file convention of our 0a9640ed and 3c2d1220, here with 800 registers). The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = 800 registers of 256 bits, counted as 25,600 bytes of memory, and charges every operation, load, store and register move. The main loop (one batch of 256 trails, 16563 operations: the 16546-gate generated step, 14 operations of the stage-1 test and 3 loop operations) has no load, store or move because the generated line needs 773 registers (output plane j in the register of input plane j). The organizer's reference count C(r3) = 638 is used only as the unit. Code is memory and its format is not fixed by the cost model: a register-only gate (the step, the stage-1 ORs, the recovery circuit) is charged as one 40-bit instruction word of 5 bytes (8-bit opcode, three 10-bit register numbers), every other instruction 36 bytes (opcode, registers, inline 256-bit immediate), and the code of the circuit generator 36 bytes per instruction of its compiled form (2149 instructions, proof.md 3.1, 3.6).",
    "scope": "The loop body of one batch of 256 lanes, its stage-1 test and the handlers; table walks, recovery, events and setup are charged at the stated bounds including loads and stores of their words.",
    "extrapolation": "A machine with fewer than 773 registers would add loads and stores to every batch; the claim assumes the declared 800.",
    "evidence_ids": [rng("3.1"), rng("3.2"), rng("3.3"), rng("3.5"), rng("3.6"), rng("7.")],
    "limitations": "The benchmark profile does not fix a register count or an instruction set; the declaration is this entry's own. The count 16546 is produced by the generator in the program (its C port emits the identical program in a memory-capped sandbox, proof 3.6) and the register allocation by `allocate`.",
}
claim = {
    "schema_version": 3,
    "target_profile": "blake3-r3-prefix-v1",
    "attack_class": "ordinary-collision",
    "rounds": 3,
    "claim": {"time_log2": 124.69481, "time_unit": "target-compressions", "memory_log2_bytes": 20, "preprocessing_log2": 24.26,
              "success_probability": 0.39, "nonuniform_advice_log2_bytes": 5},
    "restrictions": restrictions,
    "baseline_improved": "blake3-r3-nominal-v2",
    "certificate_manifest": "certificates/manifest.json",
    "experiment_manifest": "experiments/manifest.json",
    "heuristics": [h1, h3],
    "submission_state": "ready",
    "lane": "exploratory",
}
for h in (h1, h3):
    for k in ("statement", "scope", "extrapolation", "limitations"):
        assert len(h[k]) <= 4096, (h["id"], k, len(h[k]))
json.dump(claim, open(P + "claim.json", "w", encoding="utf-8", newline="\n"), indent=2)
print(h1["evidence_ids"], h3["evidence_ids"], [len(r) for r in restrictions])
