"""Roll of patch_sel.py (B3R4sel) to another round row: the select-gate full adder in the row's base bsrho.py, plus round-text normalisation.
usage: python -B roll_sel.py <row dir> <rounds>"""
import os, sys, re
D = sys.argv[1]; R = int(sys.argv[2])
P = os.path.join(D, "pkg", "blake3", "experiments", "bsrho.py")
t = open(P, encoding="utf-8", newline="").read()
UNITS = {1: 222, 2: 430, 3: 638, 4: 846, 5: 1054, 6: 1262, 7: 1470}


def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (t.count(a), a[:80])
    t = t.replace(a, b)


def sub(pat, new, n=1):
    global t
    t, k = re.subn(pat, new, t)
    assert k == n, (k, pat)


sub(r'"""Birthday collision search on \d-round BLAKE3-256 \(blake3-r\d, one block\)', '"""Birthday collision search on %d-round BLAKE3-256 (blake3-r%d, one block)' % (R, R))
sub(r"flags 11 = CHUNK_START\|CHUNK_END\|ROOT, \d rounds with", "flags 11 = CHUNK_START|CHUNK_END|ROOT, %d rounds with" % R)
sub(r"renaming; full adders by the pivot rule\), 4 register", "renaming; full adders of 2 XOR and 1 select gate), 4 register")
rep("Credit: the pivot full adder and the mask walk g = f XOR q are the method of jungjipdo's 6ae36351 (proof 3.3, 3.4), implemented here from its\ntext;",
    "Credit: the mask walk g = f XOR q (and the pivot adder kept for constant inputs) is the method of jungjipdo's 6ae36351 (proof 3.3, 3.4), implemented here from its\ntext;")
sub(r"ROUNDS = \d +# rounds of the target \(blake3-r\d-prefix-v1\)", "ROUNDS = %d                         # rounds of the target (blake3-r%d-prefix-v1)" % (R, R))
sub(r"UNIT = \d+ +# organizer reference operation cost C of blake3-r\d \([^)]*\)", "UNIT = %d%s# organizer reference operation cost C of blake3-r%d (222, 430, 638, 846, 1054, 1262, 1470 for 1..7 rounds)" % (UNITS[R], " " * (28 - len(str(UNITS[R]))), R))
sub(r"`rounds` rounds \(\d for the target\)", "`rounds` rounds (%d for the target)" % R)
sub(r"the plain \d-round compression of the block", "the plain %d-round compression of the block" % R)
sub(r"# a shared gate \(none at the \d-round target: see selftest\)", "# a shared gate (none at the %d-round target: see selftest)" % R)
sub(r"The network of the \d-round digest of the block", "The network of the %d-round digest of the block" % R)
sub(r"units are operations / \d+ \(C of blake3-r\d\)", "units are operations / %d (C of blake3-r%d)" % (UNITS[R], R))
sub(r"against the scalar \d-round compression: 4,096 lanes", "against the scalar %d-round compression: 4,096 lanes" % R)
rep("GEN_FACTOR = 200 ", "GEN_FACTOR = 250 ")

rep("    Node kinds: ('v', j) input plane j, (op, a, b) with op x (xor), a (and), o (or).  calls counts generator primitives.\"\"\"",
    "    Node kinds: ('v', j) input plane j, (op, a, b) with op x (xor), a (and), o (or), ('m', s, a, b) the select s ? a : b.  calls counts generator primitives.\"\"\"")
rep("""    def XOR(self, x, y):
        self.calls += 1""", """    def mk3(self, s, a, b):
        self.calls += 1
        k = ("m", s, a, b)
        if k in self.memo:
            self.hits += 1
        else:
            self.nodes.append(k)
            self.memo[k] = len(self.nodes) - 1
        return self.memo[k]

    def SEL(self, s, a, b):
        \"\"\"s ? a : b on signals, one select gate (a 3-input bitwise word operation, as v128.bitselect or NEON BSL); a and b have equal polarity.
        The register of s holds the true selector XOR its polarity, so a selector of polarity 1 swaps a and b.\"\"\"
        self.calls += 1
        if s[1]:
            a, b = b, a
        assert s[0] != 0 and a[0] != 0 and b[0] != 0 and a[1] == b[1]
        if a[0] == b[0]:
            return a
        return (self.mk3(s[0], a[0], b[0]), a[1])

    def XOR(self, x, y):
        self.calls += 1""")
rep("""        \"\"\"(sum, carry) of three planes a + b + c by the pivot rule (the method of 6ae36351 proof 3.3, implemented here from its text).
        Three variable planes: two of the three polarities agree, so take the third as the pivot p and the two equal ones as x and y;
        u = x ^ p, v = y ^ p, sum = u ^ y, carry = (u & v) ^ p.  u and v then have equal polarity, so the AND is always one gate (AND or OR):
        every full adder is 5 gates.""", """        \"\"\"(sum, carry) of three planes a + b + c.  Three variable planes: two of them, z and x, have equal polarity (pigeonhole; the first
        such pair in the order (a, b), (a, c), (b, c)), y is the third; t = x ^ y, sum = t ^ z, carry = maj(x, y, z) = t ? z : x (one select gate):
        every full adder is 3 gates.""")
rep("""        if len(vs) == 3:
            for pi in range(3):
                o = [vs[j] for j in range(3) if j != pi]
                if o[0][1] == o[1][1]:
                    p, x, y = vs[pi], o[0], o[1]
                    break
            u = self.XOR(x, p)
            return self.XOR(u, y), self.XOR(self.AND(u, self.XOR(y, p)), p)""", """        if len(vs) == 3:
            for zi, xi in ((0, 1), (0, 2), (1, 2)):
                if vs[zi][1] == vs[xi][1]:
                    z, x, y = vs[zi], vs[xi], vs[3 - zi - xi]
                    break
            t = self.XOR(x, y)
            assert t[0] != 0
            s = self.XOR(t, z)
            return s, self.SEL(t, z, x)""")
rep("""            if k in seen and g.nodes[k][0] in "xao":
                seen.add(g.nodes[k][1])
                seen.add(g.nodes[k][2])
        order = [k for k in range(1, len(g.nodes)) if k in seen and g.nodes[k][0] in "xao"]""", """            if k in seen and g.nodes[k][0] in "xaom":
                seen.update(g.nodes[k][1:])
        order = [k for k in range(1, len(g.nodes)) if k in seen and g.nodes[k][0] in "xaom"]""")
rep("""        sym = {"x": "^", "a": "&", "o": "|"}
        for k in order:
            op, a, b = g.nodes[k]
            names[k] = "t%d" % k
            lines.append("%s=%s%s%s" % (names[k], names[a], sym[op], names[b]))
            self.lines.append((names[k], names[a], names[b]))""", """        sym = {"x": "^", "a": "&", "o": "|", "m": "?"}
        for k in order:
            op, ar = g.nodes[k][0], [names[v] for v in g.nodes[k][1:]]
            names[k] = "t%d" % k
            if op == "m":                                       # select s ? a : b = b ^ (s & (a ^ b))
                lines.append("%s=%s^(%s&(%s^%s))" % (names[k], ar[2], ar[0], ar[1], ar[2]))
            else:
                lines.append("%s=%s%s%s" % (names[k], ar[0], sym[op], ar[1]))
            self.lines.append(tuple([names[k]] + ar))""")
rep("""        for k, (_, a, b) in enumerate(self.lines):
            lu[a] = lu[b] = k""", """        for k, (_, *ab) in enumerate(self.lines):
            for v in ab:
                lu[v] = k""")
rep("[d for d, _, _ in self.lines[s0:e0]]", "[ln[0] for ln in self.lines[s0:e0]]")
rep("""        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                last[v] = k""", """        for k, (_, *ab) in enumerate(self.lines):
            for v in ab:
                last[v] = k""")
rep("""        for k, (nm, a, b) in enumerate(self.lines):
            live.add(nm)""", """        for k, (nm, *_) in enumerate(self.lines):
            live.add(nm)""")
rep("""        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                if v not in ("0", "#"):""", """        for k, (_, *ab) in enumerate(self.lines):
            for v in ab:
                if v not in ("0", "#"):""")
rep("""        for k, (nm, a, b) in enumerate(self.lines):
            need = [v for v in {a, b} if v not in ("0", "#")]""", """        for k, (nm, *ab) in enumerate(self.lines):
            need = [v for v in set(ab) if v not in ("0", "#")]""")
rep("""    for k, (nm, a, b) in enumerate(st.lines):
        ra, rb = reg.get(a, -1), reg.get(b, -1)
        for v in {a, b}:""", """    for k, (nm, *ab) in enumerate(st.lines):
        rs = tuple(reg.get(v, -1) for v in ab)
        for v in set(ab):""")
rep("        code.append((nm, reg[nm], ra, rb))", "        code.append((nm, reg[nm]) + rs)")
rep("""    for (nm, d, ra, rb) in code:
        va = regs[ra] if ra >= 0 else 0
        vb = ALL if st.opsym[nm][1] else (regs[rb] if rb >= 0 else 0)
        o = st.opsym[nm][0]
        regs[d] = va ^ vb if o == "^" else (va & vb if o == "&" else va | vb)""", """    for (nm, d, *rs) in code:
        v = [regs[r] if r >= 0 else 0 for r in rs]
        o = st.opsym[nm][0]
        regs[d] = v[0] ^ v[1] if o == "^" else (v[0] & v[1] if o == "&" else (v[0] | v[1] if o == "|" else v[2] ^ (v[0] & (v[1] ^ v[2]))))""")
rep("""GATE_BYTES = 5                     # one register-only gate (^ & |) of the step, the stage-1 test or the recovery circuit: 40-bit word = 8-bit opcode + three 10-bit register numbers (800 registers < 1024)
""", """GATE_BYTES = 5                     # one register-only gate (^ & |) of the step, the stage-1 test or the recovery circuit: 40-bit word = 8-bit opcode + three 10-bit register numbers (800 registers < 1024)
SEL_BYTES = 6                      # one select gate s ? a : b of the step: 48-bit word = 8-bit opcode + four 10-bit register numbers
""")
rep("""    code = (ph + filt + packed_circuit(st.qwords)[1]) * GATE_BYTES + (body""", """    code = (ph + filt + packed_circuit(st.qwords)[1]) * GATE_BYTES + st.by.get("m", 0) * (SEL_BYTES - GATE_BYTES) + (body""")
rep("# The generator of section 3 and 4 (pivot adder, register allocation) written", "# The generator of section 3 and 4 (select-gate adder, register allocation) written")
assert "ROUNDS = %d " % R in t and "UNIT = %d " % UNITS[R] in t
open(P, "w", encoding="utf-8", newline="").write(t)
print("patched", P, len(t.encode()))
