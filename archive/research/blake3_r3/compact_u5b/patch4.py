def rd(p): return open(p, encoding="utf-8", newline="").read()
def wr(p, t): open(p, "w", encoding="utf-8", newline="").write(t)
n = rd("note_t.md")
add = ("## Response to the a0398a27 ruling (the same design, blake3 round 6)\n\n"
 "a0398a27 was refuted on F1-trail-index-overflow (lane_cost) and F1-trail-id-overflow (lane_cryptanalysis): a 16-bit trail-number field against a table of more than 2^16 entries. "
 "This entry's table has {tmax} entries. The trail number of an entry has 17 bits and the key 63 bits (80 bits = 10 bytes); the trail numbers stay below 256 + {tmax} + 1 + 1 < 2^17, a bound the program asserts when it plans (proof 3.1, 3.8); the key false-match term of Section 4 and Appendix A use 63 bits. "
 "The material findings of that ruling: F1-full-scale-extrapolation-gap, F2-H1-full-scale-evidence-gap and F2-no-statistical-support-for-H1 concern the extrapolation of H1 to width 256; H1 is declared as a model premise, not proved, and no number of the claim is estimated from a count. "
 "F3-cost-machine-not-run concerns the 5-byte machine: it is a declared convention (H3), priced in proof 3.1, and not run as hardware; the generator, the one component that defines the circuit, was run under the 2^20-byte caps (proof 3.6).\n\n")
assert "## Numbers" in n
n = n.replace("## Numbers", add + "## Numbers", 1)
wr("note_t.md", n)
p = rd("proof_t.md")
old = "What changed against the refuted a0398a27: the trail number of a table entry has 17 bits and the key 63 bits (the entry is still 10 bytes), because trail numbers reach 256 + {tmax} + 1 > 2^16;"
assert old in p
p = p.replace(old, "Trail-number field (answering F1-trail-index-overflow and F1-trail-id-overflow of the ruling on a0398a27, the same design at round 6): the trail number of a table entry has 17 bits and the key 63 bits (the entry is 10 bytes), because trail numbers reach 256 + {tmax} + 1 + 1 > 2^16 and stay below 2^17; the program asserts this bound when it plans;")
wr("proof_t.md", p)
