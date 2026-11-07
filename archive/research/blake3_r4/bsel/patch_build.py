"""Patch build_all.py for the select-gate entry (B3R4sel).  usage: python -B patch_build.py"""
import os
H = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(H, "build_all.py")
t = open(P, encoding="utf-8", newline="").read()


def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (t.count(a), a[:80])
    t = t.replace(a, b)


rep("entry B3R4u5 (straight-line step, 5-byte gate instructions)", "entry B3R4sel (straight-line step, select-gate full adders)")
rep("dTLf=TL - TLF,", "dTLf=TL - TLF, sel=st.by['m'], dTL0=TL - 124.86023,")
# H3
rep("""the register-file convention of our 0a9640ed, which passed the judges, here with 800 registers). The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = 800 registers of 256 bits, counted as 25,600 bytes of memory, and charges every operation, load, store and register move. """,
    """the register-file convention of our 0a9640ed, which passed the judges, here with 800 registers). The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = 800 registers of 256 bits, counted as 25,600 bytes of memory, and charges every operation, load, store and register move. """
    """It also declares one bitwise word operation besides AND, OR, XOR and NOT: select(s, a, b) = (s AND a) OR ((NOT s) AND b) bit by bit on 256-bit words, charged 1 operation like the other bitwise operations; it is one instruction on real machines (WebAssembly v128.bitselect with three operands and one result, as here; Arm NEON BSL; x86 AVX-512 VPTERNLOG with immediate 0xCA). The step uses it only in its full adders, carry = (x XOR y) ? z : x (%d selects per batch); without it the program is our 0ecdfe35 (24,422 gates, time_log2 124.86023). """)
rep("""Code is memory and its format is not fixed by the cost model: a register-only gate (the step, the stage-1 test, the recovery circuit) is charged as one 40-bit instruction word of 5 bytes (8-bit opcode, three 10-bit register numbers), every other instruction 36 bytes""",
    """Code is memory and its format is not fixed by the cost model: a register-only gate of two operands (the step, the stage-1 test, the recovery circuit) is charged as one 40-bit instruction word of 5 bytes (8-bit opcode, three 10-bit register numbers), a select as one 48-bit word of 6 bytes (8-bit opcode, four 10-bit register numbers), every other instruction 36 bytes""")
rep("""(%d instructions, proof.md 3.1, 3.6)." % (body, st.ops, filt, b.GEN_CODE)),""", """(%d instructions, proof.md 3.1, 3.6)." % (st.by["m"], body, st.ops, filt, b.GEN_CODE)),""")
rep('''    limitations="The benchmark profile does not fix a register count or an instruction set; the declaration is this entry's own.''',
    '''    limitations="The benchmark profile does not fix a register count or an instruction set; the declaration is this entry's own, and the cost model's list of bitwise operations names AND, OR, XOR and NOT, not the three-input select (without the select the program is 0ecdfe35).''')
# restrictions
rep("The main loop evaluates 256 trails bit-sliced with pivot full adders: %d operations per batch (%d gates,",
    "Declared bitwise operation select(s, a, b) = (s AND a) OR ((NOT s) AND b), 1 operation (WebAssembly v128.bitselect, NEON BSL); full adder = 2 XOR + 1 select. The main loop evaluates 256 trails bit-sliced: %d operations per batch (%d gates,")
rep("Code: 5 bytes per register-only gate (40-bit word), 36 bytes per other instruction (proof.md 3.1).",
    "Code: 5 bytes per register-only gate (40-bit word), 6 bytes per select, 36 bytes per other instruction (proof.md 3.1).")
rep("plus %d bytes of code (%d gate words of 5 bytes and %d other instructions of 36 bytes)", "plus %d bytes of code (%d gate words of 5 bytes, %d of them selects of 6, and %d other instructions of 36 bytes)")
rep("% (tmax, b.ENTRY * tmax, code, ph + filt + PH7, body - ph - filt", "% (tmax, b.ENTRY * tmax, code, ph + filt + PH7, st.by[\"m\"], body - ph - filt")
i = t.index('R.append("No nonuniform advice and no prefix:')
j = t.index("\n", i)
t = t[:i] + ('R.append("No nonuniform advice and no prefix: the mask q is derived by the generator. Credited derivative of our own 0ecdfe35 (B3R4u5b, 124.86023: the same program, search, plan '
             'method, Lemma 2 and experiments; this entry changes the full adder to 2 XOR + 1 select) and through it of our eaef120f, a6ee439c, 41b32afc, 75d5e1f9, 62cfd777, 0a9640ed and 3356413f, '
             '616120b2 (the 5-byte gate encoding, re-implemented from its text; no file used or run), and jungjipdo\'s 6ae36351 for the mask walk g = f XOR q (re-implemented from its proof text; '
             'no file of it used or run). mitchuski\'s 1b7bd746 (MDFA three-addend column) was compared and is not used. preprocessing_log2 = %.1f is the setup and generator row, which is also inside time_log2." % preclaim)') + t[j:]
# dependencies: the filed 0ecdfe35 list with 0ecdfe35 first
i = t.index('deps = json.load(open(os.path.join(HERE, "..", "b4f", "pkg", "dependencies.json")))')
j = t.index('w(os.path.join(PKG, "dependencies.json")')
t = t[:i] + '''deps = json.load(open(os.path.join(HERE, "..", "compact_u5b", "pkg", "dependencies.json")))
for d in deps:
    if d["submissionId"].startswith("6ae36351"):
        d["rationale"] = ("jungjipdo's entry for blake3 round 3 (124.91252). Credited for the mask walk g = f XOR q (the digest planes are fed back as stored, so no complement and no polarity search are needed, and equality under g is equivalent to equality under f), re-implemented here from the text of its proof Section 3.4 (no file of that entry was used or run). Its pivot full adder (Section 3.3), used by our 0ecdfe35, is replaced in this entry by the select adder.")
        d["evidence"] = "proof.md first paragraph and Sections 1, 3.2 and 8."
deps.insert(0, {"submissionId": "0ecdfe35-ba7a-4f74-8ba9-779d417974a2",
     "rationale": "Our own B3R4u5b (time_log2 124.86023), filed 10-17: the program of this entry. Taken from it: the target form, the mask walk, the straight-line step and its generator (C and Python), the search, handlers, recovery, table, ledger, plan method, Section 4 (Lemma 2) and its certificate, and the experiments. Changed: the full adder of three variable planes is 2 XOR and 1 select (a declared three-input bitwise operation, 6-byte record) instead of the 5-gate pivot adder, so the step is %d gates instead of 24,422; the table and Tp, B, c are re-planned by the same plan (time_log2 124.86023 to %s)." % (st.ops, TL),
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."})
assert deps[0]["submissionId"].startswith("0ecdfe35") and len({d["submissionId"] for d in deps}) == len(deps)
''' + t[j:]
open(P, "w", encoding="utf-8", newline="").write(t)
print("patched build_all.py")
