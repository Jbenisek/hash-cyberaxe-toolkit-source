import json
P = "pkg/blake3/claim.json"
c = json.load(open(P, encoding="utf-8"))
cl = c["claim"]
cl["time_log2"] = 125.09556
cl["preprocessing_log2"] = 33.4

R = c["restrictions"]
R[0] = ("Two distinct 128-byte messages P || 0^32 || x and P || 0^32 || y (x != y, 256-bit little-endian integers), P the fixed 64-byte string of proof.md Section 8: one chunk of two blocks, "
        "block 1 = P (flags 1, counter 0, length 64), block 2 = 0^32 || x (flags 10, counter 0, length 64, chaining value = the chaining value of P), standard IV, unkeyed, the complete 256-bit digest of the 3-round hash "
        "(blake3-r3-prefix-v1), found as a collision f(x) = f(y) of f(x) = digest(P || 0^32 || x). Plain birthday attack; no differential or structural property of the 3 rounds is used. The two-block mode is declared as H4.")
R[1] = R[1].replace("595 operations per batch", "593 operations per batch")
R[2] = R[2].replace("26,791 table keys", "26,837 table keys").replace("no advice (m0..m7 = 0)", "no advice (m0..m7 of the last block = 0)").replace("below 400 (density 400 / 2^122)", "below 401 (density 401 / 2^122)")
R[3] = ("Memory: 26,837 table entries of 25 bytes (670,925 bytes) plus 373,536 bytes of code (10,376 instructions of 36 bytes) plus 2,048 bytes of counters plus 2,048 bytes for 64 registers: "
        "1,048,557 bytes <= 2^20; claimed as 2^20, so the memory term of the score is 0.")
R[4] = R[4].replace("about 2.96e-4 spent", "about 2.97e-4 spent")
R.append("Preprocessing: P was found once by a scan of 10,768,619,077 first-block compressions (2^33.33; proof.md Section 8) for one 32-bit condition on its chaining value; the claim states preprocessing_log2 = 33.4. The attack itself uses no stored advice (K = 0).")
for r in R:
    assert len(r) <= 1024, len(r)

H = c["heuristics"]
H[0]["statement"] = (H[0]["statement"]
    .replace("f(x) = digest(0^32 || x), the 3-round complete hash of a 64-byte message,", "f(x) = digest(P || 0^32 || x), the 3-round complete hash of the 128-byte message with the fixed first block P of proof.md Section 8,")
    .replace("below 400) is independent", "below 401) is independent").replace("probability 400 / 2^122", "probability 401 / 2^122"))
H[0]["scope"] = H[0]["scope"].replace("the fixed key m0..m7 = 0,", "the fixed prefix P (so the fixed chaining value CV of the last block) and m0..m7 of the last block = 0,").replace("mean length 2^113.36", "mean length 2^113.35").replace("other keys,", "other prefixes or keys,")
H[0]["limitations"] = H[0]["limitations"].replace("and other keys are untested.", "and other keys are untested; no participant test of T1 to T3 was made on the function with this CV (they used the chaining value IV).")
H[0]["evidence_ids"] = ["experiment:rho-n22", "proof:114-126", "proof:95-113", "proof:141-150"]
s = H[1]["statement"]
s = (s.replace("mean L = 2^113.36", "mean L = 2^113.35").replace("Poisson with mean 0.157, charged as 2.56e-4", "Poisson with mean 0.1574, charged as 2.57e-4")
     .replace("below 2^-42.5", "below 2^-41.2").replace("below 2.96e-4", "below 2.97e-4"))
H[1]["statement"] = s
H[1]["scope"] = H[1]["scope"].replace("DP density 400 / 2^122", "DP density 401 / 2^122").replace("table of 26,791 keys", "table of 26,837 keys")
H[1]["limitations"] = H[1]["limitations"].replace("mean 0.157", "mean 0.1574").replace("costs 2.56e-4", "costs 2.57e-4")
H[2]["scope"] = H[2]["scope"].replace("batches of 595 operations", "batches of 593 operations")
H[2]["limitations"] = H[2]["limitations"].replace("The count 595 is", "The count 593 is").replace("116 + 232 + 235 + 12", "115 + 232 + 234 + 12")
H[2]["evidence_ids"] = ["proof:40-59", "proof:91-94", "proof:134-139"]
H[2]["statement"] = H[2]["statement"].replace("16 batches of 595 operations", "16 batches of 593 operations")
H.append({
    "id": "H4-two-block-message-mode",
    "statement": ("Supporting, used by the score-critical claim. The target's message domain, quoted from the organizer profile field message_domain, is \"Finite byte strings of bit length below 2^64.\" "
                  "The attack outputs two 128-byte messages P || 0^32 || x and P || 0^32 || y, which are byte strings of that domain; the standard chunk rules for 128 bytes (one chunk, two blocks, flags 1 on block 1 and 10 on block 2) apply and are those of verifier/blake3.py. "
                  "P is a fixed constant of the program, fixed before the attack by a bounded scan (proof.md Section 8) for the one condition (A1 + B2) mod 2^32 = 0 on the chaining value of P; the attack does not depend on any other property of P."),
    "role": "supporting",
    "scope": "The target blake3-r3-prefix-v1, messages of exactly 128 bytes whose first 64 bytes are P and whose bytes 64..95 are zero. Not claimed for other message lengths, other prefixes, or keyed or tree modes.",
    "extrapolation": ("None beyond the profile text: the claim relies on the profile accepting any finite byte string as a message. The claim does not apply to a reading of the domain that excludes 128-byte strings; the base entry (0^32 || x, 125.10041) makes a claim for 64-byte messages. "
                      "The program's digest functions agree with verifier/blake3.py on 300 messages of this form (0 differences), and the organizer experiment rho-n22 recomputes the digests of the 128-byte messages with the organizer's reference."),
    "evidence_ids": ["experiment:rho-n22", "proof:11-19", "proof:141-150"],
    "limitations": ("The scan that found P is a one-time computation of 10,768,619,077 first-block compressions, stated as preprocessing_log2 = 33.4; its uniformity assumption (a random chaining value passes with probability 2^-32) is used only to describe the scan and is not used by the attack. "
                    "One condition of this kind saves 2 operations of 595 (0.0049 bit before the re-selection of Tp and the table, 0.00485 bit in the ledger).")
})
json.dump(c, open(P, "w", encoding="utf-8", newline="\n"), indent=2, ensure_ascii=False)
open(P, "a", encoding="utf-8", newline="\n").write("\n")

M = "experiments/manifest.json"
m = json.load(open(M, encoding="utf-8"))
e = m["experiments"][0]
e["scope"] = e["scope"].replace("returns the two 64-byte messages 0^32 || x and 0^32 || y.", "returns the two 128-byte messages P || 0^32 || x and P || 0^32 || y (P = PREFIX of the program, the first block; the last block has flags 10 and chaining value chain_value(P)).")
assert "128-byte" in e["scope"]
json.dump(m, open(M, "w", encoding="utf-8", newline="\n"), indent=2)
print("ok")
