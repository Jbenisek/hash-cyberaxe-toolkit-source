"""Patch proof_t.md for the select-gate entry (B3R4sel).  usage: python -B patch_tpl.py"""
import os
H = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(H, "proof_t.md")
t = open(P, encoding="utf-8", newline="").read()
L = t.split("\n")
assert L[0].startswith("# blake3-r4: plain birthday") and L[2].startswith("Credited derivative of our own eaef120f") and L[3].startswith("The target is the plain one")
assert L[5].startswith("The generator of the setup writes the 5-byte records") and L[7].startswith("What changed against the refuted a0398a27") and L[8] == ""
L[0] = "# blake3-r4: plain birthday with 256 bit-sliced lanes and a mask walk, at four rounds, straight-line step with select-gate full adders (B3R4sel)"
L[2] = ("Credited derivative of our own 0ecdfe35-ba7a-4f74-8ba9-779d417974a2 (B3R4u5b, blake3 round 4, time_log2 124.86023: the same target, search, plan method, handlers, recovery, table, "
        "Lemma 2 of Section 4, certificate and experiments; this entry changes the full adder of the generated step and the plan that follows from the smaller code), and through it of our own "
        "eaef120f-c690-4978-a31e-a3cde49fd669 (B3R4f, 124.93474), a6ee439c-5b82-41f2-8acb-9917c8c70756 (B3R4d, 125.06000: the entry that introduced clause (d) of H1, which answers the finding "
        "F1-adaptive-finished-trail-conditioning / H4 of the judges on 41b32afc), 9f69f1cc-f6b2-4e86-a668-19b5a2085a2c (B3R4e, 125.06177: Lemma 2 v2), 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 "
        "(125.02375, rejected by the judges on that one finding about the success-probability argument), 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (125.35348), 62cfd777-5613-463f-b561-e2340e00e528 "
        "(blake3 round 3, 124.8123), 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (blake3 round 3, 124.96822, passed the judges) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448; its two-block mode "
        "is not used), which are derivatives of our cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087). The mask walk g = f XOR q, "
        "in which the digest planes are fed back exactly as the circuit stores them, is from jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), whose proof text (3.4) we read as data "
        "and re-implemented without using or running any file of that entry; its pivot full adder (3.3), used by 0ecdfe35, is replaced here by the select adder of Section 3.2. The 5-byte encoding "
        "of register-only gate instructions is the convention of 616120b2-f777-44a8-bbd2-44f20c56224a (blake3 round 7), re-implemented from its text; none of its files used or run. "
        "mitchuski's 1b7bd746-17fa-429f-84f9-bbecc944ad38 (blake3 round 4, 124.80193) adds each all-variable a + b + m as one three-addend sum with the 9-gate MDFA column; we compared that column "
        "with this step: with the select gate two ripples of 3-gate full adders cost 6 gates per bit position, so the column is not used here.")
L[3] = ("The target is the plain one: the message is 64 bytes, 0^32 || x, one block, flags 11, standard IV; no prefix, no advice, no polarity climb, no scan. What this entry changes against "
        "0ecdfe35: the machine has one more bitwise word operation, the select s ? a : b of three registers (H3, Section 3.1), and the full adder of three variable planes is 2 XOR and 1 select "
        "instead of the 5 gates of the pivot adder (Section 3.2). The chain step is {PH} operations for 256 trails ({perlane:.2f} per trail; it was 24,422), of which {sel} are selects; the code is "
        "{codebytes} bytes (it was 170,020; a select record is 6 bytes), so the table holds {tmax} entries (it was 83,650) and Tp, B and c are re-planned by the same `plan(256)` (Section 7). "
        "The memory of the entry is {mem} bytes = 2^{memlog2:.5f} <= 2^20. time_log2 {TL} against 124.86023 ({dTL0:+.5f}). Without the select operation the program is 0ecdfe35 (124.86023).")
L[5] = "The generator of the setup writes the 5-byte and 6-byte records; the program it emits is byte-identical to the Python reference (sha256 equal)."
del L[7:9]
t = "\n".join(L)


def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (t.count(a), a[:80])
    t = t.replace(a, b)


rep("The attack outputs x != y", "The search outputs x != y")
rep("## 2. The attack (program", "## 2. The search (program")
rep("Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word;",
    "Charged: every addition, AND, OR, XOR, select, shift, comparison, conditional branch and the one random word;")
rep("(the declared 800 registers are below 1,024). The program of the generator writes exactly these records (Section 3.6).",
    "(the declared 800 registers are below 1,024). A select gate of the step (s ? a : b of three registers into a register) is one 48-bit instruction word, charged 6 bytes: an 8-bit opcode and four 10-bit register numbers. The program of the generator writes exactly these records (Section 3.6).")
rep("The 5-byte word is a price stated by this entry (H3), not a measurement.\n",
    "The 5-byte and 6-byte words are prices stated by this entry (H3), not measurements.\n"
    "Select operation (part of H3). The machine of this entry has one bitwise operation besides AND, OR, XOR and NOT: select(s, a, b) = (s AND a) OR ((NOT s) AND b), bit by bit on "
    "256-bit words, charged 1 operation like the other bitwise operations. It is a bitwise Boolean function of whole words, of the same kind as the bitwise AND/OR/XOR/NOT that the cost model "
    "lists, with three inputs. It is one instruction on real machines: WebAssembly v128.bitselect (three operands, one result: the form used here), Arm NEON BSL, and x86 AVX-512 VPTERNLOG "
    "with immediate 0xCA. The step uses it only in the full adder (Section 3.2), {sel} times per batch. Without it the full adder is the 5-gate pivot adder and the program is 0ecdfe35 "
    "(24,422 gates, time_log2 124.86023).\n")
rep("The full adder is the pivot adder of 6ae36351 (our re-implementation, `Gen.fa`). Each signal is a pair (node, polarity): the register holds the node's value and the true plane is that value XOR polarity, so complements are free. Of three variable inputs a, b, c, two have the same polarity (pigeonhole); take the third as the pivot p and the two equal ones as x and y. With u = x XOR p and v = y XOR p: sum = u XOR y, carry = (u AND v) XOR p, because maj(x, y, p) = p XOR ((x XOR p) AND (y XOR p)). u and v have equal polarity, so the AND is always one gate (an AND of two upright planes, or an OR of two inverted planes, with the result's polarity set); every full adder with three variable inputs is 5 gates (XOR for u, XOR for the sum, XOR for v, the AND, XOR for the carry).",
    "The full adder (`Gen.fa`) uses the select operation of Section 3.1. Each signal is a pair (node, polarity): the register holds the node's value and the true plane is that value XOR polarity, so complements are free. Of three variable inputs a, b, c, two have the same polarity (pigeonhole); take the first such pair in the order (a, b), (a, c), (b, c) as z and x, and the third as y. With t = x XOR y: sum = t XOR z and carry = t ? z : x, because maj(x, y, z) = z when x != y and = x when x = y. z and x have the same polarity k, so the select of their registers is the register of the carry, with polarity k; a selector of polarity 1 swaps the two data operands. Every full adder with three variable inputs is 3 gates (2 XOR and 1 select; the pivot adder of 0ecdfe35 needs 5).")
rep("{gates} gates = {xor} XOR + {and_} AND + {or_} OR = **{PH} operations**", "{gates} gates = {xor} XOR + {and_} AND + {or_} OR + {sel} select = **{PH} operations**")
rep("It builds the network of Section 3.2 with the pivot adders and allocates", "It builds the network of Section 3.2 with the select adders and allocates")
rep("the result takes the lowest free register or a new one, and the instruction record is written.",
    "the result takes the lowest free register or a new one, and the instruction record is written (5 bytes for a gate of two registers, 6 bytes for a select).")
rep("With the code of the gates charged 5 bytes (Section 3.1) the program", "With the code of the gates charged 5 bytes and of the selects 6 bytes (Section 3.1) the program")
rep(" (Charged 36 bytes per gate, this program would be 954,072 bytes of code and leave a table of 5,245 entries.)", "")
rep("the recovery circuit {PH7}) + {otherinstr} other instructions * 36 bytes", "the recovery circuit {PH7}) + {sel} selects * 1 byte (their records are 6 bytes) + {otherinstr} other instructions * 36 bytes")
rep("and H3 (the 800-register machine convention and the instruction charges, 5 bytes per register-only gate and 36 bytes per other instruction, supporting).",
    "and H3 (the 800-register machine convention, the select operation, and the instruction charges, 5 bytes per register-only gate, 6 bytes per select and 36 bytes per other instruction, supporting).")
rep("Credited to 6ae36351 (jungjipdo): the pivot full adder (Section 3.2) and the mask walk g = f XOR q with the digest planes fed back as stored (Sections 1, 3.2); we wrote both from the text of its proof and did not use or run its files.",
    "Credited to 6ae36351 (jungjipdo): the mask walk g = f XOR q with the digest planes fed back as stored (Sections 1, 3.2); we wrote it from the text of its proof and did not use or run its files; its pivot full adder is replaced here by the select adder.")
rep("The generator is new (Section 3.6), charged. Credited to our own B3R4f (eaef120f): the straight-line step, the search, the plan method, the experiments' form and the generator's use-count and packing changes; this entry changes the instruction price of the gates, the record format of the generator, and Section 4.",
    "Credited to our own 0ecdfe35 (B3R4u5b) and through it B3R4f (eaef120f): the straight-line step, the generator, the search, the plan method, Section 4 and the experiments' form; this entry changes the full adder (select operation), the generator's records and the plan that follows.")
open(P, "w", encoding="utf-8", newline="\n").write(t)
print("patched proof_t.md", len(t.encode()))
