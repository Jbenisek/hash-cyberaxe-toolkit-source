#!/usr/bin/env python3
"""The displays of Section 4 (steps O, M, Y, T and the 24 lines of round 1) and Table C, read from the template
src/proof_head.md as they are printed, and run. Research helper, not submitted.

    python -B tools/proof_lines_pkg7.py [tuples, default 20000]

Nothing is typed a second time here: the formulas are parsed out of the text, so a slip in the text (a wrong sign,
a wrong name, a line that reads a name before it is assigned) shows. For every tuple of eight words it checks
  - every one of the 96 names against a forward 2-round compression of the real 55 bytes of A that is written in
    this file from Section 1 and records every value of every call by its name (Lemma T2 (b));
  - the names that the experiment program computes (outer, middle, member, trial) and its sixteen words;
  - lengths, the zero tail of B, the same states S and X for B, digest words 0, 2, 5, 7 (theorem of Section 5),
    Y4 = y for A and B, eta for members of the sub-class, and that the eight words are read back from A.
Without numbers it checks Lemma T2 (a): 29 + 21 + 10 + 12 + 24 lines, every name assigned once, every line reads
only constants, the eight words and earlier names, what each step may read, no formula mixes + or - with XOR at
one bracket level, and for every cell of Table C that the line of that name contains exactly the names of that
assignment of that call. Writes work/text/proof_lines.json. Exit status 0 only if everything holds.
"""
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
SRC = PKG / "src" / "proof_head.md"
OUT = PKG / "work" / "text" / "proof_lines.json"
M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CALLS = (("K0", 0, 4, 8, 12), ("K1", 1, 5, 9, 13), ("K2", 2, 6, 10, 14), ("K3", 3, 7, 11, 15),
         ("D0", 0, 5, 10, 15), ("D1", 1, 6, 11, 12), ("D2", 2, 7, 8, 13), ("D3", 3, 4, 9, 14))
ROUND1 = (("C0", 0, 4, 8, 12), ("C1", 1, 5, 9, 13), ("C2", 2, 6, 10, 14), ("C3", 3, 7, 11, 15),
          ("E0", 0, 5, 10, 15), ("E1", 1, 6, 11, 12), ("E2", 2, 7, 8, 13), ("E3", 3, 4, 9, 14))
STEPS = (("O", "**Step O", 29), ("M", "**Step M", 21), ("Y", "**Step Y", 10), ("T", "**Step T", 12),
         ("R", "*Round 1, forwards", 24))
EIGHT = ("C0.c1", "C0.d1", "D3.d1", "S15", "S9", "w5", "X2", "y")
TOKEN = re.compile(r"IV\[\d\]|ROL|ROR|XOR|[A-Za-z][A-Za-z0-9]*(?:\.[a-h][12])?|\d+")


def rol(v, n):
    v &= M32
    return ((v << n) | (v >> (32 - n))) & M32


def ror(v, n):
    return rol(v, 32 - n)


def load_program():
    spec = importlib.util.spec_from_file_location("halfsearch_pkg7_lines", PKG / "blake3-r2" / "experiments" / "halfsearch.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def displays():
    """[(step, name, formula text)] in printed order, and the SHA-256 of the display lines that were read."""
    text = SRC.read_text(encoding="ascii").split("\n")
    out, seen = [], []
    for step, head, _ in STEPS:
        at = next(i for i, l in enumerate(text) if l.startswith(head))
        i = at + 1
        while not text[i].startswith("    "):
            i += 1
        while i < len(text) and text[i].startswith("    "):
            seen.append(text[i])
            if text[i].startswith("        "):
                for piece in text[i].strip().split(";"):
                    name, formula = piece.strip().split(" = ", 1)
                    out.append((step, name.strip(), formula.strip()))
            i += 1
    return out, hashlib.sha256("\n".join(seen).encode("ascii")).hexdigest()


def table_c():
    text = SRC.read_text(encoding="ascii").split("\n")
    at = next(i for i, l in enumerate(text) if l.startswith("| Call | 1st |"))
    rows = {}
    for l in text[at + 2:]:
        if not l.startswith("|"):
            break
        cells = [c.strip() for c in l.strip("|").split("|")]
        rows[cells[0]] = cells[1:]
    return rows


def names_of(formula):
    return [t for t in TOKEN.findall(formula) if t not in ("ROL", "ROR", "XOR") and not t.isdigit() and not t.startswith("IV[")]


def compiled(formula):
    def sub(m):
        t = m.group(0)
        if t in ("ROL", "ROR"):
            return t.lower()
        if t == "XOR":
            return "^"
        if t.isdigit() or t.startswith("IV["):
            return t
        return f"v[{t!r}]"
    return compile(TOKEN.sub(sub, formula), "<line>", "eval")


def mixes(formula):
    """True if some bracket level of the formula has + or - together with XOR."""
    levels, depth = {}, 0
    for t in re.findall(r"XOR|[()+\-]", formula):
        if t == "(":
            depth += 1
            levels[depth] = set()
        elif t == ")":
            if {"X", "A"} <= levels.get(depth, set()):
                return True
            depth -= 1
        else:
            levels.setdefault(depth, set()).add("X" if t == "XOR" else "A")
    return {"X", "A"} <= levels.get(0, set())


def traced(words, length):
    """Forward 2-round compression of one block (Section 1). Returns every value by its name and the digest words."""
    v = list(IV) + list(IV[:4]) + [0, 0, length, 11]
    s, t = list(words), {f"w{i}": x for i, x in enumerate(words)}

    def g(tag, a, b, c, d, x, y):
        a1 = (v[a] + v[b] + x) & M32; d1 = ror(v[d] ^ a1, 16); c1 = (v[c] + d1) & M32; b1 = ror(v[b] ^ c1, 12)
        a2 = (a1 + b1 + y) & M32; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M32; b2 = ror(b1 ^ c2, 7)
        t.update({tag + ".a1": a1, tag + ".d1": d1, tag + ".c1": c1, tag + ".b1": b1, tag + ".a2": a2})
        v[a], v[b], v[c], v[d] = a2, b2, c2, d2

    for i, (tag, a, b, c, d) in enumerate(CALLS):
        g(tag, a, b, c, d, s[2 * i], s[2 * i + 1])
        if i == 3:
            t.update((f"S{k}", v[k]) for k in range(16))
    t.update((f"X{k}", v[k]) for k in range(16))
    s = [s[p] for p in PERM]
    for i, (tag, a, b, c, d) in enumerate(ROUND1):
        g(tag, a, b, c, d, s[2 * i], s[2 * i + 1])
        if i == 3:
            t.update((f"Y{k}", v[k]) for k in range(16))
    t["E3.h1"], t["E3.g1"], t["E3.f1"], t["E3.e2"] = t["E3.d1"], t["E3.c1"], t["E3.b1"], t["E3.a2"]
    return t, [v[i] ^ v[i + 8] for i in range(8)]


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    m = load_program()
    lines, sha = displays()
    const = {"W4": m.W4, "W13": m.W13, "X3": m.X3, "X7": m.X7, "X11": m.X11, "X15": m.X15, "Y3": m.Y3, "Y11": m.Y11}
    problems = []
    per_step = {s: sum(1 for l in lines if l[0] == s) for s, _, _ in STEPS}
    if [per_step[s] for s, _, _ in STEPS] != [n for _, _, n in STEPS]:
        problems.append(f"lines per step {per_step}")
    assigned, level = [], {}
    for step, name, formula in lines:
        reads = [n for n in names_of(formula) if n not in const]
        if name in assigned or name in EIGHT or name in const:
            problems.append(f"{name}: assigned twice, or one of the eight words or a constant")
        for n in reads:
            n = "y" if n == "Y4" else n
            if n not in EIGHT and n not in assigned:
                problems.append(f"{name} reads {n} before it is assigned")
            lv = level.get(n, {"X2": "M", "y": "Y"}.get(n, "O"))
            if (step == "O" and lv != "O") or (step == "M" and lv not in "OM") or (step == "Y" and lv not in "OY"):
                problems.append(f"{name} (step {step}) reads {n} of level {lv}")
        if mixes(formula):
            problems.append(f"{name}: + or - with XOR at one bracket level")
        assigned.append(name)
        level[name] = step
    # Table C: the line of every cell has exactly the names of that assignment of that call
    table, by_name = table_c(), {name: formula for _, name, formula in lines}
    state = {"K": ("iv", "S"), "D": ("S", "X"), "C": ("X", "Y")}
    sched = [f"w{i}" for i in range(16)]
    sched1 = [sched[p] for p in PERM]
    cells = 0
    pinned = set(const) | {"w4", "w13", "w14", "w15", "iv"}
    for group, order, words in ((CALLS, None, sched), (ROUND1[:3], None, sched1)):
        for i, (tag, a, b, c, d) in enumerate(group):
            src, dst = state[tag[0]]
            A, B, C, D = (("iv",) * 4 if src == "iv" else tuple(f"{src}{k}" for k in (a, b, c, d)))
            a2, b2, c2, d2 = (f"{dst}{k}" for k in (a, b, c, d))
            x, y = words[2 * i], words[2 * i + 1]
            a1, d1, c1, b1 = (f"{tag}.{k}" for k in ("a1", "d1", "c1", "b1"))
            eqs = ({a1, A, B, x}, {d1, D, a1}, {c1, C, d1}, {b1, B, c1}, {a2, a1, b1, y}, {d2, d1, a2}, {c2, c1, d2}, {b2, b1, c2})
            for n, eq in enumerate(eqs):
                cell = table[tag][n]
                want = {("y" if e == "Y4" else e) for e in eq if e not in pinned}
                have = {cell} | {("y" if e == "Y4" else e) for e in names_of(by_name.get(cell, "")) if e not in const}
                cells += 1
                if cell not in by_name or want != have:
                    problems.append(f"Table C, {tag} assignment {n + 1}: line of {cell} has {sorted(have)}, the assignment {sorted(want)}")
    flat = [c for row in table.values() for c in row]
    if len(flat) != 88 or len(set(flat)) != 88 or set(flat) | {"E1.a1", "E1.d1", "E1.b1", "E1.a2", "E3.h1", "E3.g1", "E3.f1", "E3.e2"} != set(assigned):
        problems.append("Table C and the eight lines of E1 and E3 are not the 96 lines")
    code = [(name, compiled(formula)) for _, name, formula in lines]
    right = {"names": 0, "program": 0, "words": 0, "half": 0, "y4": 0, "eta": 0, "back": 0, "in_sub": 0}
    extreme = 0
    for case in range(count):
        raw = hashlib.shake_256(b"pkg7-proof-lines-%d" % case).digest(40)
        w = list(struct.unpack("<8I", raw[:32]))
        if case % 10 == 9:
            extreme += 1
            w = [(0, M32, x)[raw[32 + i] % 3] for i, x in enumerate(w)]
        in_sub = case % 2 == 0
        if in_sub:
            w[7] = m.class_member(int.from_bytes(raw[36:40], "little") % m.CLASS_SIZE)
        v = dict(const, **dict(zip(EIGHT, w)))
        v["Y4"] = v["y"]
        env = {"v": v, "rol": rol, "ror": ror, "IV": IV}
        for name, c in code:
            v[name] = eval(c, env) & M32
        words = [v["w0"], v["w1"], v["w2"], v["w3"], m.W4, v["w5"], v["w6"], v["w7"], v["w8"], v["w9"], v["w10"], v["w11"],
                 v["w12"], m.W13, 0, 0]
        other = list(words)
        other[4], other[5] = m.W4B, (words[5] + m.DELTA5) & M32
        a, b = struct.pack("<16I", *words)[:55], struct.pack("<16I", *other)[:63]
        ta, da = traced(struct.unpack("<16I", a + bytes(9)), 55)
        tb, db = traced(struct.unpack("<16I", b + bytes(1)), 63)
        right["names"] += all(v[name] == ta[name] for name in assigned) and all(v[n] == ta[n] for n in EIGHT[:7])
        o = m.outer(w[:6])
        ctx = m.middle(o, w[6])
        pw, pt = m.trial(ctx, w[7])
        prog = dict(ctx, **pt)
        right["program"] += all(v[k] == prog[k] for k in prog if k in v) and len([k for k in prog if k in v]) >= 60
        right["words"] += pw == words and m.messages(pw) == (a, b)
        right["half"] += (b[55:] == bytes(8) and all(ta[f"{s}{k}"] == tb[f"{s}{k}"] for s in "SX" for k in range(16))
                          and all(da[i] == db[i] for i in (0, 2, 5, 7))
                          and m.compress2(a)[1] == da and m.compress2(b)[1] == db and a != b)
        right["y4"] += ta["Y4"] == tb["Y4"] == w[7]
        right["back"] += [ta[n] for n in EIGHT[:7]] + [ta["Y4"]] == w
        if in_sub:
            right["in_sub"] += 1
            right["eta"] += (ta["E3.h1"] ^ tb["E3.d1"]) == m.ETA and ((m.Y3 + w[7]) & m.CLASS_MASK) == m.CLASS_VALUE
    for key in ("names", "program", "words", "half", "y4", "back"):
        if right[key] != count:
            problems.append(f"{key}: {right[key]} of {count}")
    if right["eta"] != right["in_sub"]:
        problems.append(f"eta: {right['eta']} of {right['in_sub']}")
    result = {"tuples": count, "extreme": extreme, "lines": len(lines), "per_step": per_step, "table_c_cells": cells,
              "right": right, "problems": problems, "display_sha256": sha,
              "program_sha256": hashlib.sha256((PKG / "blake3-r2" / "experiments" / "halfsearch.py").read_bytes()).hexdigest()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
    print(f"displays: {len(lines)} lines {per_step}; Table C cells checked {cells}; display sha256 {sha[:16]}")
    print(f"{count} tuples ({extreme} extreme, {right['in_sub']} with y in the sub-class): " + ", ".join(f"{k} {n}" for k, n in right.items()))
    print("RESULT: " + ("everything holds" if not problems else f"{len(problems)} problem(s): " + "; ".join(problems[:4])))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
