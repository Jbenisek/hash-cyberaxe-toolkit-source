import re
def rd(p): return open(p, encoding="utf-8", newline="").read()
def wr(p, t): open(p, "w", encoding="utf-8", newline="").write(t)
def rep(t, a, b, n=None):
    c = t.count(a)
    assert c >= 1 and (n is None or c == n), (a[:70], c)
    return t.replace(a, b)
B5C = "77fb5c02-839d-4aeb-8b51-2c100c649b9a"; B5B = "4a9f31b8-0ac7-475d-a73d-583a41298226"; T6 = "616120b2-f777-44a8-bbd2-44f20c56224a"
# ---- proof_t
t = rd("proof_t.md")
t = rep(t, "at the full five rounds, straight-line step with 5-byte gate instructions (B3R5u5)", "at five rounds, straight-line step with 5-byte gate instructions (B3R5u5)")
i = t.index("Credited derivative of our own a2e94df7"); j = t.index("of our own a6ee439c-5b82")
new3 = ("Credited derivative of our own %s (B3R5c, blake3 round 5, time_log2 125.19806: the filed rolled version of this program; this entry replaces its rolled step by the straight line of 4a9f31b8 and rewrites its Section 4 as a first-collision proof), "
        "of our own %s (B3R5b, blake3 round 5, time_log2 125.00951, memory_log2_bytes 20.37855, scalar score 125.38806: the same search, plan method and experiments, and this entry's straight-line five-round step; this entry charges its register-only gates 5 bytes of code each instead of 36, so the program fits in 2^20 bytes and the memory term is removed), "
        "of the convention of 616120b2-f777-44a8-bbd2-44f20c56224a (gate instructions priced and encoded at 5 bytes each; re-implemented from its text, none of its files used or run), of our own a2e94df7-bff4-4461-ad40-7f75930cb241 (B3R7c, blake3 round 7, 125.29113: the rolled program from which B3R5c was taken), " % (B5C, B5B))
t = t[:i] + new3 + t[j:]
t = rep(t, "What changed against B3R7c (a2e94df7): the step is the straight line of 1cd0dd3b ({PH} operations a batch, no loop) instead of the rolled body (55,210)", "What changed against B3R5c (77fb5c02): the step is the straight line of 4a9f31b8 ({PH} operations a batch, no loop) instead of the rolled body (37,255 operations a batch)")
t = rep(t, "time_log2 {TL} against 125.29113", "time_log2 {TL} against 125.19806")
t = t.replace("1cd0dd3b", "4a9f31b8").replace("125.05397", "125.00951").replace("0.86686", "0.37855").replace("125.92083", "125.38806")
t = rep(t, "(4a9f31b8 charged 36 bytes per gate, had {mem7} bytes and paid 0.37855 bit.)", "(4a9f31b8 charged 36 bytes per gate, had {mem7} bytes and paid 0.37855 bit.)")
t = rep(t, "at 4 rounds and at 7 rounds (the target, the full round count)", "at 4 rounds and at 5 rounds (the target)")
t = rep(t, "At 7 rounds the program's digest", "At 7 rounds (BLAKE3) the program's digest")
t = rep(t, "(222, 430, 638, 846, 1,054, 1,262 and 1,054 for 1 to 7 rounds, that is 14 + 208 r;", "(222, 430, 638, 846 and 1,054 for 1 to 5 rounds, that is 14 + 208 r;")
t = rep(t, "exp(-120 + (e^2 - 1) H)", "exp(-300 + (e^5 - 1) H)")
t = rep(t, "w = e^2", "w = e^5"); t = rep(t, "outside 60 or more", "outside 60 or more") if "outside 60 or more" in t else t
wr("proof_t.md", t)
# ---- note_t
n = rd("note_t.md")
n = rep(n, "(B3R5u5)", "(B3R5u5)") 
i = n.index("It is our own B3R7c"); j = n.index("The lineage:")
n = n[:i] + ("It is our own B3R5c, %s (time_log2 125.19806, a rolled round body), with the straight-line step of our B3R5b, %s (time_log2 125.00951, memory 2^20.37855, scalar score 125.38806), whose code now fits in 2^20 bytes because each register-only gate is charged as a 40-bit instruction word of 5 bytes (an 8-bit opcode and three 10-bit register numbers; proof Section 3.1; the convention of 616120b2-f777-44a8-bbd2-44f20c56224a, re-implemented from its text, none of its files used or run), and with Section 4 rewritten as a first-collision proof of Lemma 2.\n" % (B5C, B5B)) + n[j:]
n = rep(n, "The lineage: 4a9f31b8 is our round-4 entry a6ee439c-5b82-41f2-8acb-9917c8c70756 (125.06000) taken to five rounds;" if "The lineage: 4a9f31b8" in n else "The lineage: 1cd0dd3b is our round-4 entry a6ee439c-5b82-41f2-8acb-9917c8c70756 (125.06000) taken to five rounds;", "The lineage: B3R5c and B3R5b are our B3R7c a2e94df7-bff4-4461-ad40-7f75930cb241 and our round-4 entry a6ee439c-5b82-41f2-8acb-9917c8c70756 (125.06000) taken to five rounds;") if False else n
n = n.replace("The lineage: 1cd0dd3b is our round-4 entry", "The lineage: B3R5b is our round-4 entry")
n = rep(n, "## What changed against B3R7c (a2e94df7)", "## What changed against B3R5c (77fb5c02)")
n = rep(n, "straight line of 1cd0dd3b ({PH} operations a batch) instead of the rolled body (55,210)", "straight line of 4a9f31b8 ({PH} operations a batch) instead of the rolled body (37,255 operations a batch)")
n = rep(n, "time_log2 {TL} against 125.29113", "time_log2 {TL} against 125.19806")
n = n.replace("## What changed against 1cd0dd3b (B3R7)", "## What changed against 4a9f31b8 (B3R5b)").replace("1cd0dd3b", "4a9f31b8").replace("125.05397", "125.00951").replace("0.86686", "0.37855").replace("125.92083", "125.38806")
n = rep(n, "at 3, 4 and 7 rounds", "at 3, 4 and 5 rounds") if "at 3, 4 and 7 rounds" in n else n
wr("note_t.md", n)
# ---- build_all
b = rd("build_all.py")
b = rep(b, "TL7, SC7, MT7 = 125.05397, 125.92083, 0.86686", "TL7, SC7, MT7 = 125.00951, 125.38806, 0.37855")
b = rep(b, "mem7=fm(1912272)", "mem7=fm(1363176)")
b = rep(b, '"rounds": 7,', '"rounds": 5,') if '"rounds": 7,' in b else b
wr("build_all.py", b)
