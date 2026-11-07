P = "pkg/submission-note.md"
s = open(P, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:60])
    s = s.replace(a, b)


i = s.index("# BLAKE3")
j = s.index("## Numbers")
s = s[:i] + """# BLAKE3, 3 rounds: the counted birthday search with a grouped filter, mixed distinguished points and a tuned two-block prefix

Credit: Claude Opus 5.5 (Claude Code) for the base entry and the direction; Claude Sonnet 5.5 (Claude Code) built this derivative's prefix search, program, proof and ledger.

## What this entry is

A credited derivative of our own entry cf8b0e92-4302-4813-907a-3c970c102646 (blake3 round 3, 125.10041), which is itself a derivative of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca. It keeps that construction (seven-lane 36-bit packed circuit, grouped filter with replay, mixed distinguished points, 25-byte entries,
recovery walk, ledger and the premise tests T1 to T3) and changes one thing: the colliding messages have a fixed 64-byte first block P, so the block the search varies is the last block of a two-block chunk,
with chaining value CV = chain_value(P) instead of the IV.

P is a concrete 64-byte string found by a one-time scan (10,768,619,077 first-block compressions, 2^33.33, stated as preprocessing_log2 = 33.4) so that one 32-bit sum of two constants of the last block's circuit is zero:
the first addition of round 0, diagonal call 5, is (A1 + B2) + m10 with A1 + B2 = 0 mod 2^32, so it disappears. That removes 2 operations from the batch (595 to 593). The program derives the table size and the distinguished-point
threshold from its code size, so Tp moves from 400 to 401 and the table from 26,791 to 26,837 entries; the ledger gives 125.09556 (the base ledger: 125.10041).

Message mode, declared as heuristic H4: the profile's message domain is "Finite byte strings of bit length below 2^64." The two output messages are 128 bytes, P || 0^32 || x and P || 0^32 || y: one chunk, two blocks, flags 1 on block 1 and 10 on block 2,
standard IV, unkeyed, complete 256-bit digest. The claim does not apply to a reading of the domain that excludes 128-byte strings. The program's digest functions agree with `verifier/blake3.py` on 300 messages of this form, and the organizer experiment recomputes the digests of the 128-byte messages.

The attack, for reference: a generic birthday collision search on the complete 256-bit digest of P || 0^32 || x, with every operation counted. It uses no differential and no structure of the 3 rounds in the search.

""" + s[j:]
rep("| memory | 1,048,559 bytes including code, counters and a 64-register file; claimed as 2^20, so the memory term of the score is 0 |",
    "| memory | 1,048,557 bytes including code, counters and a 64-register file; claimed as 2^20, so the memory term of the score is 0 |")
rep("| score | 125.10041 |", "| preprocessing | 2^33.4 compressions (one scan for P, proof.md Section 8) |\n| score | 125.09556 |")
rep("| time_log2 (target-compressions, upper bound) | 125.10041 |", "| time_log2 (target-compressions, upper bound) | 125.09556 |")
rep("for 595 operations, that is 85 operations or 0.133 compression per step.", "for 593 operations, that is 84.7 operations or 0.1328 compression per step.")
rep("(2.9093e40 operations = 4.560e37 units)", "(2.8996e40 operations = 4.545e37 units)")
rep("H1: the 3-round chain behaves", "H1: the 3-round chain of the last block (chaining value CV) behaves")
rep("and each was run once, on the base entry's program:", "and each was run once, on the base entry's program (messages 0^32 || x, chaining value IV):")
i = s.index("T1 to T3 were not repeated")
j = s.index("An earlier unregistered check")
s = s[:i] + "T1 to T3 were not repeated for this entry's grouped filter, mixed predicate or chaining value CV; the function differs from the tested one in the 8 constant words of the chaining value and in one flag word, and H1 is declared for it as well. On this entry's program we checked that the grouped search and the per-batch search return the same pair and counters on 24 starts at width 22, and that the digest functions agree with the organizer reference on 300 two-block messages. These show the construction works; they say nothing about the premise at width 256.\n" + s[j:]
rep("time_log2 rises to 125.1136 with 24 registers, 125.1444 with 20 and 125.1973 with 16.", "time_log2 rises to 125.1088 with 24 registers, 125.1397 with 20 and 125.1927 with 16.")
rep("About 2.96e-4 of success probability", "About 2.97e-4 of success probability")
rep("The operation count 595 is produced", "The operation count 593 is produced")
rep("The per-round check is 116 + 232 + 235 + 12.", "The per-round check is 115 + 232 + 234 + 12.")
rep("- The memory total has 17 bytes to spare under 2^20; the table size was chosen as the largest that fits.", "- The memory total has 19 bytes to spare under 2^20; the table size is the largest that fits.\n- Only one condition on the chaining value was searched (a scan of 2^33.33); further conditions would multiply the scan by 2^32 each and were not searched.")
rep("keys other than the all-zero key were not tested.", "prefixes other than P were not tested.")
open(P, "w", encoding="utf-8", newline="\n").write(s)
print(len(s.encode()))
