import json, os
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pkg")
os.makedirs(os.path.join(H, "certificates"), exist_ok=True)
open(os.path.join(H, "certificates", "manifest.json"), "w", newline="\n").write('{"schema_version":2,"certificates":[]}')
mask14 = "ff3f" + "00" * 30
mask10 = "ff03" + "00" * 30
zero = "00" * 32
man = {"schema_version": 1, "experiments": [
    {"id": "rho-n14", "kind": "python-message-pairs-v1",
     "scope": "The poseidon-orchard-r56-prefix-v1 target (all 64 rounds), messages (v, 0) with v below 2^14: one run of the shipped single-trail search (`search` in experiments/rho.py: distinguished points of density 1/16, 256 steps, table of 64 points, recovery from stored points) on the walk v -> low 14 bits of the real digest of (v, 0), from a start derived from the trial seed. Returns the two messages (a, 0), (b, 0) when the search ends with a pair, two nulls otherwise.",
     "hypothesis": "For every returned pair the two messages are distinct canonical inputs (a, b below 2^14, rho = 0) and the complete 56-partial-round digests agree in the low 14 bits. This is exact: the program recovers the merge point of its own trail. The number of trials that return a pair is a program check, not an estimate of any success probability; no probability or cost is inferred from it. Observations (untrusted): status, evals. Not shown: any width-254 cost or success probability.",
     "program": "experiments/rho.py",
     "event": {"kind": "digest-xor-mask", "mask_hex": mask14, "expected_hex": zero}},
    {"id": "proj-w254", "kind": "python-message-pairs-v1",
     "scope": "The poseidon-orchard-r56-prefix-v1 target at full width: 64 points of the real walk x -> digest(x, 0) on field elements from a start derived from the trial seed (a 254-bit value), messages (x, 0). Returns two distinct points whose complete digests agree in the low 10 bits when the 64 points contain such a pair, two nulls otherwise.",
     "hypothesis": "For every returned pair the two messages are distinct canonical inputs (x, 0) with x below p and their complete digests agree in the low 10 bits. This checks the walk map, the message construction and the digest at full width. The number of returned pairs is a program check, not an estimate; no probability or cost is inferred. Observations (untrusted): status, j. Not shown: collision structure at 2^127 evaluations.",
     "program": "experiments/rho.py",
     "event": {"kind": "digest-xor-mask", "mask_hex": mask10, "expected_hex": zero}}]}
json.dump(man, open(os.path.join(H, "experiments", "manifest.json"), "w", newline="\n"), indent=1)

claim = {
    "schema_version": 3, "target_profile": "poseidon-orchard-r56-prefix-v1", "attack_class": "ordinary-collision", "rounds": 56,
    "claim": {"time_log2": 127.009, "time_unit": "target-compressions", "memory_log2_bytes": 20, "preprocessing_log2": 0,
              "success_probability": 0.39, "nonuniform_advice_log2_bytes": 0},
    "restrictions": [
        "Two distinct inputs (x, 0) and (y, 0), x != y canonical Pallas field elements, rho = 0, for the complete Orchard hash with all 56 partial rounds (poseidon-orchard-r56-prefix-v1): found as a collision F(x) = F(y) of the walk F(x) = digest(x, 0), whose output is again a canonical input. Plain birthday search with one trail and distinguished points; no property of the rounds is used.",
        "Machine, the cost model's own: Pallas field RAM with 256-bit words, one call of the reference permutation = 1 unit (C = 1392), every other word operation 1/1392. The trail step is 1 unit + 7 other operations (proof.md Section 5); recovery evaluations 1 unit + 8; all table and bookkeeping work is bounded by 10^8 operations. time_log2 is the full budget (every halt charged at its limit): S = n + d trail steps, 3 gmax recovery evaluations, with n the least multiple of 2^100 that reaches success 0.39 (proof.md Section 4, `python3 experiments/rho.py --plan`). One attempt, no restart, no amplification, no advice, no preprocessing.",
        "Memory: a table of 2^14 + 2 entries of 48 bytes (786,528) plus at most 21,600 bytes of code, 6,464 bytes of constants and 512 bytes of registers: 815,104 bytes, below 2^20; claimed as 2^20, so the memory term of the score is zero.",
        "Success probability at least 0.39: Lemma 2 of proof.md Section 4 proves it for a uniformly random function F (bound 0.3900000006) from the lazy-sampling hazard (i + 1) / N of each fresh step, with explicit terms for detection, table and gaps; H1 (declared, score-critical) says the real attempt succeeds at least as often.",
        "The declared experiments run this program in the organizer sandbox at width 14 (rho-n14) and 64 points of the full-width walk (proj-w254); they check returned pairs against the real digest and are program checks, not estimates. No outside code or library is used. No collision of the full target is produced here and none is claimed to be producible here; the claim is the cost of the search."],
    "baseline_improved": "poseidon-orchard-r56-nominal-v2",
    "certificate_manifest": "certificates/manifest.json", "experiment_manifest": "experiments/manifest.json",
    "heuristics": [
        {"id": "H1-random-function-model", "role": "score-critical",
         "statement": "Model premise. Let F be a uniformly random function from the Pallas field (N = p, about 2^254) to itself and the distinguished-point set (density theta = 27554 / 2^128) independent of F. For the fixed target, the probability that the single attempt of the search succeeds on the walk x -> digest(x, 0) is at least the probability P_F, over a uniform 254-bit start and F, that the same search succeeds when every evaluation is replaced by F (lazy sampling): (a) the iterates have the first-collision law of a random mapping (each fresh step hits one of the i + 1 earlier values with probability (i + 1) / N); (b) whether an iterate is a distinguished point is independent of the collision events and of the other iterates, with probability theta. Proof.md Section 4 proves P_F >= 0.39 for F.",
         "scope": "The fixed target poseidon-orchard-r56-prefix-v1 restricted to inputs (x, 0), one trail of about 1.7e38 evaluations of F from a uniform 254-bit start. Not claimed for other messages, other round counts, or other evaluation counts.",
         "extrapolation": "Declared and not proved; no proof is known. The functional graph of F on 2^254 points and trails of 2^127 steps cannot be observed. The organizer experiments rho-n14 and proj-w254 run this program on the real target at width 14 and 64 points of the full-width walk; they are program checks, and no number of the claim is estimated from them. Extrapolation to width 254 is by the premise only. If the hazard is (1 - e) / N instead of 1 / N the budget needs 0.0072 bit for e = 0.01, 0.0370 bit for e = 0.05, 0.076 bit for e = 0.10.",
         "evidence_ids": ["experiment:rho-n14", "experiment:proj-w254", "proof:23-33", "proof:47-51"],
         "limitations": "A model premise about one fixed function, not a theorem: the run is a deterministic function of the start. It cannot be tested at width 254. The bound has no margin above 0.39 (n is the least multiple of 2^100 that reaches it), so any hazard deficit is repaired by extra time, priced above."},
        {"id": "H2-machine-convention", "role": "supporting",
         "statement": "The call of the reference permutation is one unit and pays for all of its arithmetic, constants and loads (the cost model's definition of the target-compression unit); the loop variables are registers; the other operations are charged at 1/1392 as listed in proof.md Section 5 (7 per trail step, 8 per recovery evaluation, 10^8 for everything else).",
         "scope": "The loop of one trail step, the recovery and the bounded bookkeeping of proof.md Section 5.",
         "extrapolation": "None beyond the stated charges. If a loop step cost 20 other operations instead of 7 the time would rise by 0.0135 bit.",
         "evidence_ids": ["proof:35-41", "proof:43-45"],
         "limitations": "The benchmark profile fixes no register count or instruction encoding; the code size of 36 bytes per instruction with 256-bit immediates is this entry's own convention, and memory has a one-MiB floor in the score."}],
    "submission_state": "draft", "lane": "exploratory"}
json.dump(claim, open(os.path.join(H, "claim.json"), "w", newline="\n"), indent=1)
