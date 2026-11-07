#!/usr/bin/env python3
"""Render the seventh package (a DRAFT) from its templates, and compare the experiment program with the data module.
Research helper, not submitted.

    python -B tools/build_pkg7.py            write proof, claim, experiment manifest and note
    python -B tools/build_pkg7.py --check    write nothing; say whether the files on disk are what the templates give
    python -B tools/build_pkg7.py --program  write nothing; only compare experiments/halfsearch.py with pkg7_data.py

Templates (src/): proof_head.md (summary, Sections 1 to 5), proof_search.md (Section 6), proof_cost.md (Sections 7 to
9), proof_evidence.md (Sections 10 to 13), claim.json, manifest.json, note.md, and src/parts/ (passages kept from the
filed text of entry c66f230d, copied once by tools/extract_parts.py). A template is the final text with {{name}}
where a figure depends on the program, the count or an evidence file; the names are defined in tools/pkg7_text.py
and nowhere else. Edit the text in src/, never in the rendered files.

The build never changes the experiment program. It renders the proof (a paragraph or list item that contains a name,
or a line over 79 characters, is wrapped again at 79; tables, displayed formulas and headings are left as they are),
finds the line ranges of the rendered proof that claim.json cites, renders claim.json, the manifest and the note,
and refuses to write if a name is unknown, a proof line is over 79 characters, a file is not ASCII, a JSON file does
not parse or a field is longer than the schema allows.

--program checks:
  1. the nine lines of experiments/halfsearch.py that hold the pin, the lengths, eta, the sub-class, the rule, the
     factor and the machine: each must be the line that pkg7_data.py gives;
  2. the loaded program: constants, class mask, value, size and list words, the three rules, the stage-2 budget
     (list words * ceil(2^127 / (FACTOR * members)) >> (n - 3));
  3. for each of the three rules (the line RULE_CONDITIONS set in memory): the program's TABLES give the stage counts
     and the counts of the three other pieces that pkg7_data.py has, and the program's own check of Lemma A
     (rule_a_right(): every pattern of the bits read, in every lane) holds.
"""
import json
import re
import sys
import textwrap
import types
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import pkg7_data as data  # noqa: E402

PKG, CAND, SRC = data.PKG, data.CAND, data.PKG / "src"
PROOF, CLAIM = CAND / "proof.md", CAND / "claim.json"
MANIFEST, NOTE = CAND / "experiments" / "manifest.json", PKG / "submission-note-r2.md"
PROOF_PARTS = ("proof_head.md", "proof_search.md", "proof_cost.md", "proof_evidence.md")
TOKEN = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")
ITEM = re.compile(r"^(\d+\. |- )")
BAD_START = re.compile(r"^\s*([-+*>#] |\d+\. )")
WIDTH = 79


def lines_wanted():
    p = data.PIN
    return {
        r"^X3, X7, X11, X15 = .*$": "X3, X7, X11, X15 = " + ", ".join(f"0x{p[k]:08X}" for k in ("X3", "X7", "X11", "X15")),
        r"^W4, W13 = .*$": f"W4, W13 = 0x{p['W4']:08X}, 0x{p['W13']:08X}",
        r"^ETA = .*$": f"ETA = 0x{data.ETA:08X}",
        r"^CUBE = .*$": f"CUBE = (0x{data.CUBE[0]:08X}, 0x{data.CUBE[1]:08X})",
        r"^LEN_A, LEN_B = .*$": f"LEN_A, LEN_B = {data.LEN_A}, {data.LEN_B}",
        r"^RULE_CONDITIONS = .*$": f"RULE_CONDITIONS = {data.RULE_CONDITIONS}",
        r"^FACTOR = .*$": f"FACTOR = {data.FACTOR}",
        r"^REGISTERS = .*$": f"REGISTERS = {data.MACHINE_REGISTERS}",
        r"^KEPT = .*$": f"KEPT = {data.KEPT_WORDS}",
    }


def loaded(text, rule):
    text, count = re.subn(r"^RULE_CONDITIONS = .*$", f"RULE_CONDITIONS = {rule}", text, flags=re.M)
    assert count == 1
    module = types.ModuleType(f"halfsearch_rule{rule}")
    exec(compile(text, "experiments/halfsearch.py", "exec"), module.__dict__)
    return module


def program_check(quiet=False):
    text = data.PROGRAM.read_bytes().decode("ascii")
    problems = []
    for pattern, line in lines_wanted().items():
        found = re.findall(pattern, text, flags=re.M)
        if found != [line]:
            problems.append(f"line {pattern}: program has {found}, pkg7_data.py gives {line!r}")
    for rule in data.RULES:
        m = loaded(text, rule)
        if rule == data.RULE_CONDITIONS:
            same = ((m.X3, m.X7, m.X11, m.X15, m.W4, m.W13) == tuple(data.PIN[k] for k in ("X3", "X7", "X11", "X15", "W4", "W13"))
                    and (m.CLASS_MASK, m.CLASS_VALUE, m.CLASS_SIZE, m.BATCHES) == (data.CLASS_MASK, data.CLASS_VALUE, data.CLASS_SIZE,
                                                                                  data.LIST_WORDS)
                    and m.RULES == data.RULES and tuple(m.RULE_A) == data.RULES[rule]
                    and m.STAGE_2_BUDGET == data.LIST_WORDS * -(-(1 << 127) * 6400 //
                                                 (data.FACTOR * data.CLASS_SIZE * getattr(m, "EQUIVALENTS", 6400))) >> (rule - 3))
            if not same:
                problems.append("the loaded program does not have the pin, the sub-class, the rules or the stage-2 budget of pkg7_data.py")
        table = {name: tuple(sum(r[i] for r in rows) for i in (1, 2, 3)) for name, rows in m.TABLES.items() if name != "batch"}
        a, s2 = m.TABLES["batch"][:m.STAGE_A_PARTS], m.TABLES["batch"][m.STAGE_A_PARTS:]
        counts = ((sum(r[1] for r in a), sum(r[2] for r in a)), (sum(r[1] for r in s2), sum(r[2] for r in s2)))
        if counts != (data.STAGE_A_BY_RULE[rule], data.STAGE_2_BY_RULE[rule]) or table != {
                "outer step": data.OUTER_STEP, "table build": data.TABLE_BUILD, "middle step": data.MIDDLE_STEP}:
            problems.append(f"rule {rule}: TABLES of the program gives {counts}, {table}")
        patterns, right, _ = m.rule_a_right()
        if right != patterns:
            problems.append(f"rule {rule}: rule_a_right() {right} of {patterns}")
        if not quiet:
            print(f"rule {rule}: stage A {counts[0][0]}+{counts[0][1]}, stage 2 {counts[1][0]}+{counts[1][1]}; Lemma A patterns "
                  f"{right} of {patterns}")
    if problems:
        print("DIFFERENCES:\n  " + "\n  ".join(problems))
        return 1
    if not quiet:
        print(f"experiments/halfsearch.py has the pin, lengths {data.LEN_A} and {data.LEN_B}, eta {data.ETA:08x}, the sub-class "
              f"{data.CLASS_MASK:08x}/{data.CLASS_VALUE:08x} ({data.CLASS_SIZE} members), the three rules, RULE_CONDITIONS = "
              f"{data.RULE_CONDITIONS}, FACTOR = {data.FACTOR}, the stage-2 budget and the counts of pkg7_data.py")
    return 0


# ---- rendering (the functions of the build of the filed package, unchanged in what they do)
def is_prose(block):
    lines = block.split("\n")
    if any(l.startswith("|") or l.startswith("#") for l in lines):
        return False
    first = lines[0]
    if ITEM.match(first):
        return all(ITEM.match(l) or l.startswith("  ") or not l for l in lines)
    return not any(l.startswith("    ") for l in lines)


def fill(text, first, rest):
    """Wrap one paragraph or list item at WIDTH; no continuation line may look like the start of a list or heading."""
    for width in range(WIDTH, WIDTH - 16, -1):
        lines = textwrap.wrap(" ".join(text.split()), width=width, initial_indent=first, subsequent_indent=rest,
                              break_long_words=False, break_on_hyphens=False)
        if not any(BAD_START.match(l[len(rest):]) for l in lines[1:]):
            return "\n".join(lines)
    raise SystemExit("cannot wrap: " + text[:80])


def wrap_block(block):
    lines = block.split("\n")
    if not ITEM.match(lines[0]):
        return fill(block, "", "")
    items, current = [], None
    for l in lines:
        if ITEM.match(l):
            current = [l]
            items.append(current)
        else:
            current.append(l)
    out = []
    for item in items:
        marker = ITEM.match(item[0]).group(1)
        body = item[0][len(marker):] + " " + " ".join(x.strip() for x in item[1:])
        out.append(fill(body, marker, " " * len(marker)))
    return "\n".join(out)


def render(text, tokens, reflow=True):
    missing = sorted({n for n in TOKEN.findall(text) if n not in tokens})
    if missing:
        raise SystemExit("names that pkg7_text.py does not define: " + ", ".join(missing))
    out = []
    for block in text.rstrip("\n").split("\n\n"):
        names = TOKEN.findall(block)
        if TOKEN.fullmatch(block.strip("\n")):             # a block that is one name: a table, a passage or a paragraph
            value = tokens[names[0]]
            if value == "":
                continue
            out.append("\n\n".join(wrap_block(b) if reflow and is_prose(b) and any(len(l) > WIDTH for l in b.split("\n")) else b
                                   for b in value.split("\n\n")))
            continue
        new = TOKEN.sub(lambda m: tokens[m.group(1)], block) if names else block
        if reflow and is_prose(new) and (names or any(len(l) > WIDTH for l in new.split("\n"))):
            new = wrap_block(new)
        out.append(new)
    return "\n\n".join(out) + "\n"


def proof_ranges(proof):
    lines = proof.split("\n")

    def find(prefix, start=1):
        for i in range(start - 1, len(lines)):
            if lines[i].startswith(prefix):
                return i + 1
        raise SystemExit(f"not found in the proof: {prefix}")

    def back(n):
        while lines[n - 1].strip() == "":
            n -= 1
        return n

    s4 = find("## 4. Construction: the message from eight words")
    s6 = find("## 6. The search for the other half", s4)
    s61 = find("**6.1 Trials.**")
    s62 = find("**6.2 The residual of a trial.**", s61)
    e63 = find("**6.3 Two tests of a trial.**")
    s64 = find("**6.4 Algorithm.**", e63)
    s65 = find("**6.5 Seven trials in one word.**", s64)
    s7 = find("## 7. Success probability")
    h2 = find("**Heuristic H2 (supporting).**", s7)
    h3 = find("**Heuristic H3 (supporting).**", h2)
    under = find("Under H1, H2 and H3 the algorithm outputs", h3)
    neither = find("None of the three heuristics is proved.", s7)
    s10 = find("## 10. Evidence, scope and field meanings")
    scope = find("**Scope and limitations.**", s10)
    spans = {"constr": (s4, back(s6 - 1)), "trials": (s61, back(s62 - 1)), "early": (e63, back(s64 - 1)), "algo": (s64, back(s65 - 1)),
             "batch": (s65, back(s7 - 1)), "s7": (s7, neither), "h2": (h2, back(h3 - 1)), "h3": (h3, back(under - 1)),
             "s10": (s10, back(scope - 1))}
    # What each heuristic cites. H1's event includes rule A, so it cites 6.3 (the rule, Lemma A) and 6.4 (what the
    # algorithm drops) besides the construction (Sections 4 and 5), the trials, Section 7 and Section 10.
    cited = {"ev_h1": ("constr", "trials", "early", "algo", "s7", "s10"), "ev_h2": ("early", "algo", "h2", "s10"),
             "ev_h3": ("early", "algo", "batch", "h3", "s10")}

    def blank(n):
        return 1 <= n <= len(lines) and lines[n - 1].strip() == ""

    def assemble(sp):
        r = {k: f"proof:{a}-{b}" for k, (a, b) in sp.items()}
        r["ev_h1"] = ", ".join(f'"{e}"' for e in ("experiment:residual-search", "experiment:half-collision") + tuple(r[k] for k in cited["ev_h1"]))
        r["ev_h2"] = ", ".join(f'"{r[k]}"' for k in cited["ev_h2"])
        r["ev_h3"] = ", ".join(f'"{r[k]}"' for k in cited["ev_h3"])
        return r

    # research/public_text_scan.py reads digits as letters, so a pair of line numbers can spell a word of its list
    # next to "proof". Where that happens a range is widened by the blank line before or after it, which changes
    # the digits and not what is cited.
    flagged = scan_rule()
    r = assemble(spans)
    if flagged:
        for _ in range(8):
            bad = [k for k in ("ev_h1", "ev_h2", "ev_h3") if flagged(f'"evidence_ids": [{r[k]}],')]
            if not bad:
                break
            moved = False
            for key in tuple(k for name in ("ev_h1", "ev_h2", "ev_h3") if name in bad for k in cited[name]):
                a, b = spans[key]
                for cand in ((a - 1, b) if blank(a - 1) else None, (a, b + 1) if blank(b + 1) else None,
                             (a - 1, b + 1) if blank(a - 1) and blank(b + 1) else None):
                    if cand is None or cand == spans[key]:
                        continue
                    trial = dict(spans, **{key: cand})
                    rt = assemble(trial)
                    if sum(bool(flagged(f'"evidence_ids": [{rt[k]}],')) for k in ("ev_h1", "ev_h2", "ev_h3")) < len(bad):
                        spans, r, moved = trial, rt, True
                        break
                if moved:
                    break
            if not moved:
                print("NOTE: a cited line range reads as a word for research/public_text_scan.py and could not be moved")
                break
    return r


def scan_rule():
    """The test of research/public_text_scan.py for one line, built from that file's own word list and digit map.

    Returns a function line -> bool, or None if the script is not there or no longer has these two definitions."""
    path = PKG.parent / "public_text_scan.py"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^BAD = .*?^LEET = [^\n]*\n", text, re.S | re.M)
    if not m:
        return None
    env = {}
    try:
        exec(m.group(0), {"str": str}, env)          # two constant definitions of the participant's own script
    except Exception:
        return None
    words, leet = env.get("BAD"), env.get("LEET")
    if not words or leet is None:
        return None

    def flagged(line):
        low = line.lower()
        plain = re.sub(r"[^a-z ]", " ", low)
        spelled = re.sub(r"[^a-z ]", " ", low.translate(leet))
        squeezed = re.sub(r"[^a-z]", "", low.translate(leet))
        return any(w in plain or w in spelled or w.replace(" ", "") in squeezed for w in words)

    return flagged


def rendered():
    """(tokens, proof, claim, manifest, note) from the templates; stops on any problem."""
    import pkg7_text
    if program_check(quiet=True):
        raise SystemExit("not built: experiments/halfsearch.py is not the program of pkg7_data.py")
    tokens = pkg7_text.build_tokens()
    proof = render("\n\n".join((SRC / name).read_text(encoding="ascii").rstrip("\n") for name in PROOF_PARTS) + "\n", tokens)
    long_lines = [(i + 1, len(l)) for i, l in enumerate(proof.split("\n")) if len(l) > WIDTH]
    if long_lines:
        raise SystemExit(f"proof lines over {WIDTH} characters after rendering (shorten them in src/): {long_lines[:12]}")
    ranges = proof_ranges(proof)
    tokens.update(ranges)
    claim = render((SRC / "claim.json").read_text(encoding="ascii"), tokens, reflow=False)
    manifest = render((SRC / "manifest.json").read_text(encoding="ascii"), tokens, reflow=False)
    note = render((SRC / "note.md").read_text(encoding="ascii"), tokens)
    c, mf = json.loads(claim), json.loads(manifest)
    problems = []
    if c["claim"] != {"time_log2": float(tokens["time_log2"]), "time_unit": "target-compressions", "memory_log2_bytes": 35,
                      "preprocessing_log2": 63, "success_probability": 0.39, "nonuniform_advice_log2_bytes": 6}:
        problems.append("the claim block of claim.json is not the claim of pkg7_text.py")
    if c["submission_state"] != data.SUBMISSION_STATE:
        problems.append("the state of claim.json is not that of pkg7_data.py")
    problems += [f"restriction {i} is {len(r)} characters (limit 1024)" for i, r in enumerate(c["restrictions"]) if len(r) > 1024]
    for h in c["heuristics"]:
        problems += [f"{h['id']}.{k} is {len(h[k])} characters (limit 4096)" for k in ("statement", "scope", "extrapolation", "limitations")
                     if len(h[k]) > 4096]
    for e in mf["experiments"]:
        problems += [f"manifest {e['id']}.{k} is {len(e[k])} characters (limit 2000)" for k in ("scope", "hypothesis") if len(e[k]) > 2000]
    if len(note.encode("ascii")) < 5120:
        problems.append("the note is shorter than 5,120 bytes")
    for name, text in (("proof.md", proof), ("claim.json", claim), ("manifest.json", manifest), ("note", note)):
        if TOKEN.search(text) or "[[" in text:
            problems.append(f"{name}: a name or placeholder is left")
        if "\r" in text or "\t" in text or any(l != l.rstrip() for l in text.split("\n")):
            problems.append(f"{name}: CR, tab or trailing space")
    if problems:
        raise SystemExit("not written:\n  " + "\n  ".join(problems))
    return tokens, ranges, proof, claim, manifest, note


def main():
    if "--program" in sys.argv:
        return program_check()
    check_only = "--check" in sys.argv
    tokens, ranges, proof, claim, manifest, note = rendered()
    drift = 0
    for path, text in ((PROOF, proof), (CLAIM, claim), (MANIFEST, manifest), (NOTE, note)):
        new = text.encode("ascii")
        old = path.read_bytes() if path.exists() else b""
        if new == old:
            print(f"unchanged  {path.relative_to(PKG)}  ({len(new)} bytes)")
        elif check_only:
            drift += 1
            a, b = old.decode("ascii", "replace").split("\n"), text.split("\n")
            first = next((i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)) + 1)
            print(f"DRIFT      {path.relative_to(PKG)}: differs from the templates from line {first} "
                  f"(on disk {len(a) - 1} lines, rendered {len(b) - 1})")
        else:
            path.write_bytes(new)
            print(f"written    {path.relative_to(PKG)}  ({len(new)} bytes, {text.count(chr(10))} lines)")
    print("ranges:", ", ".join(f"{k} {ranges[k][6:]}" for k in ("constr", "trials", "early", "algo", "batch", "s7", "h2", "h3", "s10")))
    print(f"claim: state {tokens['submission_state']}, time_log2 {tokens['time_log2']} (bound 2^{tokens['bound_4dec']}), factor "
          f"{tokens['factor']}, 2^{tokens['trials_log2']} trials, charge {tokens['charge']}, count for H1 {tokens['kept_cons']} "
          f"(with rule A {tokens['kept_exact']}, all {tokens['r_sub']}), sub-class {tokens['cube_mask']}/{tokens['cube_value']} "
          f"({tokens['members']} members), margin {tokens['margin']}; note {len(note.encode('ascii'))} bytes")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
