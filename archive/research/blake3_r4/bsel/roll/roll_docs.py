"""Roll the B3R4sel text changes (patch_build.py, patch_tpl.py, note_t.md) to one row.  usage: python -B roll_docs.py <rounds>
Reads <row>/bsel/{roll_nums.json, base_nums.json}; edits <row>/bsel/{build_all.py, proof_t.md, note_t.md}."""
import os, re, sys, json
R = int(sys.argv[1])
H = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.dirname(H)                                       # research/blake3_r4/bsel
D = os.path.join(R4, "..", "..", "blake3_r%d" % R, "bsel")
WORD = {3: "three", 5: "five", 6: "six", 7: "seven"}[R]
UNITS = {3: 638, 5: 1054, 6: 1262, 7: 1470}
CFG = {
    3: dict(base="3c2d1220-540f-480a-81ca-b26e5ae2173a", bname="B3R3u5b", bscore="124.76596", depsrc="compact_u5b", mit="10ce9f59-80a1-4304-92cc-ca4dede3bbcc", mscore="124.70692"),
    5: dict(base="119be052-0089-4789-94f1-eccf6babf67e", bname="B3R5u5b", bscore="124.91446", depsrc="compact_u5b", mit="5c8045d1-af47-41ec-a515-22ca7a2b61cd", mscore="124.85645"),
    6: dict(base="f07a5442-c59c-4f33-9476-062ef1819d6d", bname="B3R6u5b", bscore="124.94974", depsrc="compact_u5b", mit="2d8936b8-abab-4376-ade0-905a2c336574", mscore="124.8921"),
    7: dict(base="b9f7a2bc-2ba7-4a34-a4c0-8efa7527fba1", bname="B3R7h16", bscore="124.969", depsrc="h16_stage", mit="f88f3751-f08b-4561-a764-a04b5f7a899a", mscore="124.91757"),
}[R]
SEL4 = "2cf0d4a5-fa44-498e-bff8-b152c681ef12"
b8, m8 = CFG["base"][:8], CFG["mit"][:8]
NAME = "B3R%dsel" % R
bn = json.load(open(os.path.join(D, "base_nums.json")))
fm = lambda v: format(v, ",")
BG, BC, BT = fm(bn["ops"]), fm(bn["code"]), fm(bn["tmax"])


BASEDIR = os.path.join(D, "..", "compact_h16" if R == 7 else "compact_u5b")


def edit(path, fn):
    t = open(os.path.join(BASEDIR, os.path.basename(path)), encoding="utf-8", newline="").read()     # always from the base copy (idempotent)
    t = fn(t)
    open(path, "w", encoding="utf-8", newline="").write(t)


def rep(t, a, b, n=1):
    assert t.count(a) == n, (t.count(a), a[:90])
    return t.replace(a, b)


def sub(t, pat, new, n=1):
    t, k = re.subn(pat, lambda m: new, t)
    assert k == n, (k, pat[:90])
    return t


# ---------------------------------------------------------------- build_all.py
def build(t):
    t = sub(t, r"of the blake3-r\d entry \S+ \(straight-line step, 5-byte gate instructions\)", "of the blake3-r%d entry %s (straight-line step, select-gate full adders)" % (R, NAME))
    t = rep(t, "TL=TL, TL3=TL3,", "TL=TL, sel=st.by['m'], dTL0=TL - %s, TL3=TL3," % CFG["bscore"])
    t = rep(t, """the register-file convention of our 0a9640ed, which passed the judges, here with 800 registers). The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = 800 registers of 256 bits, counted as 25,600 bytes of memory, and charges every operation, load, store and register move. """,
            """the register-file convention of our 0a9640ed, which passed the judges, here with 800 registers). The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = 800 registers of 256 bits, counted as 25,600 bytes of memory, and charges every operation, load, store and register move. """
            """It also declares one bitwise word operation besides AND, OR, XOR and NOT: select(s, a, b) = (s AND a) OR ((NOT s) AND b) bit by bit on 256-bit words, charged 1 operation like the other bitwise operations; it is one instruction on real machines (WebAssembly v128.bitselect with three operands and one result, as here; Arm NEON BSL; x86 AVX-512 VPTERNLOG with immediate 0xCA). The step uses it only in its full adders, carry = (x XOR y) ? z : x (%%d selects per batch); without it the program is our %s (%s gates, time_log2 %s). """ % (b8, BG, CFG["bscore"]))
    t = rep(t, """Code is memory and its format is not fixed by the cost model: a register-only gate (the step, the stage-1 test, the recovery circuit) is charged as one 40-bit instruction word of 5 bytes (8-bit opcode, three 10-bit register numbers), every other instruction 36 bytes""",
            """Code is memory and its format is not fixed by the cost model: a register-only gate of two operands (the step, the stage-1 test, the recovery circuit) is charged as one 40-bit instruction word of 5 bytes (8-bit opcode, three 10-bit register numbers), a select as one 48-bit word of 6 bytes (8-bit opcode, four 10-bit register numbers), every other instruction 36 bytes""")
    t = rep(t, """(%d instructions, proof.md 3.1, 3.6)." % (body, st.ops, filt, b.GEN_CODE)),""", """(%d instructions, proof.md 3.1, 3.6)." % (st.by["m"], body, st.ops, filt, b.GEN_CODE)),""")
    t = rep(t, '''    limitations="The benchmark profile does not fix a register count or an instruction set; the declaration is this entry's own.''',
            '''    limitations="The benchmark profile does not fix a register count or an instruction set; the declaration is this entry's own, and the cost model's list of bitwise operations names AND, OR, XOR and NOT, not the three-input select (without the select the program is %s).''' % b8)
    t = rep(t, "The main loop evaluates 256 trails bit-sliced with pivot full adders: %d operations per batch (%d gates,",
            "Declared bitwise operation select(s, a, b) = (s AND a) OR ((NOT s) AND b), 1 operation (WebAssembly v128.bitselect, NEON BSL); full adder = 2 XOR + 1 select. The main loop evaluates 256 trails bit-sliced: %d operations per batch (%d gates,")
    t = rep(t, "Code: 5 bytes per register-only gate (40-bit word), 36 bytes per other instruction (proof.md 3.1).",
            "Code: 5 bytes per register-only gate (40-bit word), 6 bytes per select, 36 bytes per other instruction (proof.md 3.1).")
    t = rep(t, "plus %d bytes of code (%d gate words of 5 bytes and %d other instructions of 36 bytes)", "plus %d bytes of code (%d gate words of 5 bytes, %d of them selects of 6, and %d other instructions of 36 bytes)")
    t = rep(t, "% (tmax, b.ENTRY * tmax, code, ph + filt + PH7, body - ph - filt", "% (tmax, b.ENTRY * tmax, code, ph + filt + PH7, st.by[\"m\"], body - ph - filt")
    extra = " TheTradoor's 09fe5fcd and b1e6de75 (the 64-bit table slot and the 47-bit key, re-implemented from their text; no file used or run)," if R == 7 else ""
    i = t.index('R.append("No nonuniform advice and no prefix:')
    j = t.index("\n", i)
    t = t[:i] + ('R.append("No nonuniform advice and no prefix: the mask q is derived by the generator. Credited derivative of our own %s (%s, %s: the same program, search, plan '
                 'method, Lemma 2 and experiments; this entry changes the full adder to 2 XOR + 1 select) and through it of its lineage (dependencies.json); our %s (B3R4sel: the same '
                 'select adder at round 4);%s 616120b2 (the 5-byte gate encoding, re-implemented from its text; no file used or run), and jungjipdo\'s 6ae36351 for the mask walk g = f XOR q '
                 '(re-implemented from its proof text; no file of it used or run). mitchuski\'s %s (MDFA three-addend column) was compared and is not used. preprocessing_log2 = %%.1f is the '
                 'setup and generator row, which is also inside time_log2." %% preclaim)' % (b8, CFG["bname"], CFG["bscore"], SEL4[:8], extra, m8)) + t[j:]
    i = t.index("deps = ")
    j = t.index('w(os.path.join(PKG, "dependencies.json")')
    t = t[:i] + '''deps = json.load(open(os.path.join(HERE, "..", "%s", "pkg", "dependencies.json")))
for d in deps:
    if d["submissionId"].startswith("6ae36351"):
        d["rationale"] = ("jungjipdo's entry for blake3 round 3 (124.91252). Credited for the mask walk g = f XOR q (the digest planes are fed back as stored, so no complement and no polarity search are needed, and equality under g is equivalent to equality under f), re-implemented here from the text of its proof Section 3.4 (no file of that entry was used or run). Its pivot full adder (Section 3.3), used by our %s, is replaced in this entry by the select adder.")
        d["evidence"] = "proof.md first paragraph and Sections 1, 3.2 and 8."
if not any(d["submissionId"].startswith("616120b2") for d in deps):
    deps.append({"submissionId": "616120b2-f777-44a8-bbd2-44f20c56224a",
                 "rationale": "TheTradoor's entry for blake3 round 7 (125.18448). Credited for the convention this entry adopts: register-only gate instructions priced and encoded at 5 bytes each. Re-implemented here from the text of that entry (no file of it was used or run).",
                 "evidence": "proof.md Section 3.1 (instruction encoding) and restrictions."})
deps.insert(0, {"submissionId": "%s",
     "rationale": "Our own %s (time_log2 %s): the program of this entry. Taken from it: the target form, the mask walk, the straight-line step and its generator (C and Python), the search, handlers, recovery, table, ledger, plan method, Section 4 (Lemma 2) and its certificate, and the experiments. Changed: the full adder of three variable planes is 2 XOR and 1 select (a declared three-input bitwise operation, 6-byte record) instead of the 5-gate pivot adder, so the step is %%d gates instead of %s; the table and Tp, B, c are re-planned by the same plan (time_log2 %s to %%s)." %% (st.ops, TL),
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."})
deps.insert(1, {"submissionId": "%s",
     "rationale": "Our own B3R4sel (blake3 round 4, time_log2 124.29795): the select operation of H3, the 2 XOR + 1 select full adder, the 6-byte select record and the C generator that writes it; this entry applies the same change at %d rounds.",
     "evidence": "proof.md first paragraph and Sections 3.1, 3.2 and 3.6."})
assert deps[0]["submissionId"].startswith("%s") and len({d["submissionId"] for d in deps}) == len(deps)
''' % (CFG["depsrc"], b8, CFG["base"], CFG["bname"], CFG["bscore"], BG, CFG["bscore"], SEL4, R, b8) + t[j:]
    return t


# ---------------------------------------------------------------- proof_t.md
def proof(t):
    L = t.split("\n")
    assert L[0].startswith("# blake3-r%d: plain birthday" % R) and L[2].startswith("Credited derivative of our own") and L[3].startswith("The target is the plain one")
    assert L[7] and L[8] == "" and L[9].startswith("## 1.")
    lineage = L[2].replace("Credited derivative of our own", "%s is itself a credited derivative of our own" % b8, 1)
    L[0] = "# blake3-r%d: plain birthday with 256 bit-sliced lanes and a mask walk, at %s rounds, straight-line step with select-gate full adders (%s)" % (R, WORD, NAME)
    L[2] = ("Credited derivative of our own %s (%s, blake3 round %d, time_log2 %s: the same target, search, plan method, handlers, recovery, table, Lemma 2 of Section 4, certificate "
            "and experiments; this entry changes the full adder of the generated step and the plan that follows from the smaller code), and of our own %s (B3R4sel, blake3 round 4, "
            "time_log2 124.29795: the same select adder and 6-byte select record at four rounds). %s Its pivot full adder (3.3 of 6ae36351), used by %s, is replaced here by the select "
            "adder of Section 3.2. mitchuski's %s (blake3 round %d, %s) adds each all-variable a + b + m as one three-addend sum with the 9-gate MDFA column; we compared that column with "
            "this step: with the select gate two ripples of 3-gate full adders cost 6 gates per bit position, so the column is not used here."
            % (CFG["base"], CFG["bname"], R, CFG["bscore"], SEL4, lineage, b8, CFG["mit"], R, CFG["mscore"]))
    L[3] = ("The target is the plain one: the message is 64 bytes, 0^32 || x, one block, flags 11, standard IV; no prefix, no advice, no polarity climb, no scan. What this entry changes against "
            "%s: the machine has one more bitwise word operation, the select s ? a : b of three registers (H3, Section 3.1), and the full adder of three variable planes is 2 XOR and 1 select "
            "instead of the 5 gates of the pivot adder (Section 3.2). The chain step is {PH} operations for 256 trails ({perlane:.2f} per trail; it was %s), of which {sel} are selects; the code is "
            "{codebytes} bytes (it was %s; a select record is 6 bytes), so the table holds {tmax} entries (it was %s) and Tp, B and c are re-planned by the same `plan(256)` (Section 7). "
            "The memory of the entry is {mem} bytes = 2^{memlog2:.5f} <= 2^20. time_log2 {TL} against %s ({dTL0:+.5f}). Without the select operation the program is %s (%s)."
            % (b8, BG, BC, BT, CFG["bscore"], b8, CFG["bscore"]))
    L[5] = "The generator of the setup writes the 5-byte and 6-byte records; the program it emits is byte-identical to the Python reference (sha256 equal)."
    del L[7:9]
    t = "\n".join(L)
    t = rep(t, "The attack outputs x != y", "The search outputs x != y")
    t = rep(t, "## 2. The attack (program", "## 2. The search (program")
    t = rep(t, "Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word;",
            "Charged: every addition, AND, OR, XOR, select, shift, comparison, conditional branch and the one random word;")
    t = rep(t, "(the declared 800 registers are below 1,024). The program of the generator writes exactly these records (Section 3.6).",
            "(the declared 800 registers are below 1,024). A select gate of the step (s ? a : b of three registers into a register) is one 48-bit instruction word, charged 6 bytes: an 8-bit opcode and four 10-bit register numbers. The program of the generator writes exactly these records (Section 3.6).")
    t = rep(t, "The 5-byte word is a price stated by this entry (H3), not a measurement.\n",
            "The 5-byte and 6-byte words are prices stated by this entry (H3), not measurements.\n"
            "Select operation (part of H3). The machine of this entry has one bitwise operation besides AND, OR, XOR and NOT: select(s, a, b) = (s AND a) OR ((NOT s) AND b), bit by bit on "
            "256-bit words, charged 1 operation like the other bitwise operations. It is a bitwise Boolean function of whole words, of the same kind as the bitwise AND/OR/XOR/NOT that the cost model "
            "lists, with three inputs. It is one instruction on real machines: WebAssembly v128.bitselect (three operands, one result: the form used here), Arm NEON BSL, and x86 AVX-512 VPTERNLOG "
            "with immediate 0xCA. The step uses it only in the full adder (Section 3.2), {sel} times per batch. Without it the full adder is the 5-gate pivot adder and the program is %s "
            "(%s gates, time_log2 %s).\n" % (b8, BG, CFG["bscore"]))
    t = rep(t, "The full adder is the pivot adder of 6ae36351 (our re-implementation, `Gen.fa`). Each signal is a pair (node, polarity): the register holds the node's value and the true plane is that value XOR polarity, so complements are free. Of three variable inputs a, b, c, two have the same polarity (pigeonhole); take the third as the pivot p and the two equal ones as x and y. With u = x XOR p and v = y XOR p: sum = u XOR y, carry = (u AND v) XOR p, because maj(x, y, p) = p XOR ((x XOR p) AND (y XOR p)). u and v have equal polarity, so the AND is always one gate (an AND of two upright planes, or an OR of two inverted planes, with the result's polarity set); every full adder with three variable inputs is 5 gates (XOR for u, XOR for the sum, XOR for v, the AND, XOR for the carry).",
            "The full adder (`Gen.fa`) uses the select operation of Section 3.1. Each signal is a pair (node, polarity): the register holds the node's value and the true plane is that value XOR polarity, so complements are free. Of three variable inputs a, b, c, two have the same polarity (pigeonhole); take the first such pair in the order (a, b), (a, c), (b, c) as z and x, and the third as y. With t = x XOR y: sum = t XOR z and carry = t ? z : x, because maj(x, y, z) = z when x != y and = x when x = y. z and x have the same polarity k, so the select of their registers is the register of the carry, with polarity k; a selector of polarity 1 swaps the two data operands. Every full adder with three variable inputs is 3 gates (2 XOR and 1 select; the pivot adder of %s needs 5)." % b8)
    t = rep(t, "{gates} gates = {xor} XOR + {and_} AND + {or_} OR = **{PH} operations**", "{gates} gates = {xor} XOR + {and_} AND + {or_} OR + {sel} select = **{PH} operations**")
    t = rep(t, "It builds the network of Section 3.2 with the pivot adders and allocates", "It builds the network of Section 3.2 with the select adders and allocates")
    t = rep(t, "the result takes the lowest free register or a new one, and the instruction record is written.",
            "the result takes the lowest free register or a new one, and the instruction record is written (5 bytes for a gate of two registers, 6 bytes for a select).")
    t = rep(t, "With the code of the gates charged 5 bytes (Section 3.1) the program", "With the code of the gates charged 5 bytes and of the selects 6 bytes (Section 3.1) the program")
    if " (Charged 36 bytes per gate, this program would be {code36} bytes of code and leave a table of {tmax36} entries.)" in t:
        t = rep(t, " (Charged 36 bytes per gate, this program would be {code36} bytes of code and leave a table of {tmax36} entries.)", "")
    t = rep(t, "the recovery circuit {PH7}) + {otherinstr} other instructions * 36 bytes", "the recovery circuit {PH7}) + {sel} selects * 1 byte (their records are 6 bytes) + {otherinstr} other instructions * 36 bytes")
    t = rep(t, "and H3 (the 800-register machine convention and the instruction charges, 5 bytes per register-only gate and 36 bytes per other instruction, supporting).",
            "and H3 (the 800-register machine convention, the select operation, and the instruction charges, 5 bytes per register-only gate, 6 bytes per select and 36 bytes per other instruction, supporting).")
    t = rep(t, "Credited to 6ae36351 (jungjipdo): the pivot full adder (Section 3.2) and the mask walk g = f XOR q with the digest planes fed back as stored (Sections 1, 3.2); we wrote both from the text of its proof and did not use or run its files.",
            "Credited to 6ae36351 (jungjipdo): the mask walk g = f XOR q with the digest planes fed back as stored (Sections 1, 3.2); we wrote it from the text of its proof and did not use or run its files; its pivot full adder is replaced here by the select adder.")
    t = sub(t, r"The generator is new \(Section 3\.6\), charged\. Credited to our own [^\n]*",
            "Credited to our own %s (%s) and through it its lineage (first paragraph): the straight-line step, the generator, the search, the plan method, Section 4 and the experiments' form; "
            "to our own %s (B3R4sel): the select adder and its 6-byte record at four rounds; this entry changes the full adder (select operation), the generator's records and the plan that follows."
            % (b8, CFG["bname"], SEL4[:8]))
    return t


# ---------------------------------------------------------------- note_t.md (from the B3R4sel note)
def note(_):
    t = open(os.path.join(R4, "note_t.md"), encoding="utf-8", newline="").read()
    deps = json.load(open(os.path.join(D, "..", CFG["depsrc"], "pkg", "dependencies.json")))
    ours = [d["submissionId"] for d in deps if d["rationale"].startswith("Our own")]
    lin = ", ".join(ours[:-1]) + " and " + ours[-1]
    third = ("; TheTradoor's 09fe5fcd-5614-4329-8b7d-48957c238fac (64-bit table slot) and b1e6de75 (47-bit key), re-implemented from their text" if R == 7 else "")
    t = rep(t, "# BLAKE3, 4 rounds: bit-sliced 256-lane search, straight-line step with select-gate full adders (B3R4sel)",
            "# BLAKE3, %d rounds: bit-sliced 256-lane search, straight-line step with select-gate full adders (%s)" % (R, NAME))
    t = rep(t, "Our entry for BLAKE3 reduced to 4 rounds (blake3-r4-prefix-v1), a plain birthday collision search on the complete 256-bit digest; it uses no differential and no structure of the rounds. It is our own B3R4u5b, 0ecdfe35-ba7a-4f74-8ba9-779d417974a2 (time_log2 124.86023), with one change to the generated step: the full adder of three variable planes is 2 XOR and 1 select instead of the 5-gate pivot adder.",
            "Our entry for BLAKE3 %s %d rounds (blake3-r%d-prefix-v1), a plain birthday collision search on the complete 256-bit digest; it uses no differential and no structure of the rounds. It is our own %s, %s (time_log2 %s), with one change to the generated step: the full adder of three variable planes is 2 XOR and 1 select instead of the 5-gate pivot adder. The same change at 4 rounds is our %s (B3R4sel, 124.29795)."
            % ("at" if R == 7 else "reduced to", R, R, CFG["bname"], CFG["base"], CFG["bscore"], SEL4))
    i = t.index("The lineage of 0ecdfe35 is unchanged:")
    j = t.index("\n", i)
    t = t[:i] + ("The lineage of %s is unchanged: our %s; jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 for the mask walk g = f XOR q (re-implemented from its proof text; no file of it used or run); "
                 "616120b2-f777-44a8-bbd2-44f20c56224a for the 5-byte gate encoding (re-implemented from its text)%s." % (b8, lin, third)) + t[j:]
    t = rep(t, "mitchuski's 1b7bd746-17fa-429f-84f9-bbecc944ad38 (124.80193)", "mitchuski's %s (%s)" % (CFG["mit"], CFG["mscore"]))
    t = rep(t, "it was 24,422)", "it was %s)" % BG)
    t = rep(t, "(it was 170,020)", "(it was %s)" % BC)
    t = rep(t, "(it was 83,650)", "(it was %s)" % BT)
    t = rep(t, "Without the select operation the program is 0ecdfe35 (124.86023).", "Without the select operation the program is %s (%s)." % (b8, CFG["bscore"]))
    t = rep(t, "({dTL0:+.5f} against 0ecdfe35)", "({dTL0:+.5f} against %s)" % b8)
    t = rep(t, "units of 846 |", "units of %d |" % UNITS[R])
    t = rep(t, "| table | {tmax} entries of 10 bytes;", "| table | {tmax} entries of %d bytes;" % (8 if R == 7 else 10))
    t = rep(t, "four clauses), as in 0ecdfe35:", "four clauses), as in %s:" % b8)
    t = rep(t, "compared with the organizer's `blake3(M, 4)` on 8,192 messages and on 4,096 lanes chained for 4 steps,", "compared with the organizer's `blake3(M, %d)` on 8,192 messages and on 4,096 lanes chained for %d steps," % (R, R))
    t = rep(t, "Without the select the program is 0ecdfe35.", "Without the select the program is %s." % b8)
    assert "B3R4u5" not in t and "against 0ecdfe35" not in t and "is 0ecdfe35" not in t and "as in 0ecdfe35" not in t
    return t


edit(os.path.join(D, "build_all.py"), build)
edit(os.path.join(D, "proof_t.md"), proof)
edit(os.path.join(D, "note_t.md"), note)
print("rolled docs r%d" % R)
