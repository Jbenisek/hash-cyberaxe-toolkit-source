#!/usr/bin/env python3
"""Render the sixth package from its templates and the one data place. Research helper, not submitted.

    python -B tools/build_pkg6.py            write the package files and the note
    python -B tools/build_pkg6.py --check    write nothing; say whether the files on disk are what the templates give
    python -B tools/build_pkg6.py --program  write nothing; only compare experiments/halfsearch.py with pkg6_data.py
    python -B tools/build_pkg6.py --manifest render only experiments/manifest.json from src/manifest.json, with the
                                             figures of the program (pkg6_data.program_tokens); the program is compared
                                             with the data module first

Templates (src/): proof_head.md (Sections 1 to 9), proof_evidence.md (Section 10), claim.json, manifest.json,
note.md. A template is the final text with {{name}} where a figure depends on the pinned call, the class or the
rate; the names are defined in tools/pkg6_data.py and nowhere else. Edit the text in src/, never in the rendered
files: a later build overwrites them (--check shows the difference first).

What the build does:
  1. writes the pin, the lengths, eta, the number of conditions of rule A and the number of trials of pkg6_data.py
     into experiments/halfsearch.py (six lines) and checks, by loading the program, that its class, its list, its
     three rules, rule A on z, the stage-2 budget and the stage counts are those of the data module;
  2. renders the proof; a paragraph or list item that contains a name, or a line over 79 characters, is wrapped
     again at 79; tables, displayed formulas and headings are left as they are;
  3. finds the line ranges of the rendered proof that claim.json cites and renders claim.json with them;
  4. renders the experiment manifest and the note;
  5. refuses to write if a name is unknown, a proof line is over 79 characters, a file is not ASCII, the JSON
     files do not parse or a field is longer than the schema allows.
"""
import importlib.util
import json
import re
import sys
import textwrap
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import pkg6_data as data  # noqa: E402

PKG, CAND, SRC = data.PKG, data.CAND, data.PKG / "src"
PROOF, CLAIM = CAND / "proof.md", CAND / "claim.json"
MANIFEST, NOTE, PROGRAM = CAND / "experiments" / "manifest.json", PKG / "submission-note-r2.md", data.PROGRAM
TOKEN = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")
ITEM = re.compile(r"^(\d+\. |- )")
BAD_START = re.compile(r"^\s*([-+*>#] |\d+\. )")
WIDTH = 79


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
        raise SystemExit("names that pkg6_data.py does not define: " + ", ".join(missing))
    out = []
    for block in text.rstrip("\n").split("\n\n"):
        names = TOKEN.findall(block)
        if TOKEN.fullmatch(block.strip("\n")):             # a block that is one name: a table, a formula or a paragraph
            value = tokens[names[0]]
            if value == "":
                continue
            out.append(wrap_block(value) if reflow and is_prose(value) else value)
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
    e63 = find("**6.3 Three tests of a trial.**")
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
             "batch": (s65, back(s7 - 1)), "s7": (s7, neither),
             "h2": (h2, back(h3 - 1)), "h3": (h3, back(under - 1)), "s10": (s10, back(scope - 1))}
    # What each heuristic cites. H1's event includes rule A, so it cites 6.3 (the rule, Lemma A) and 6.4 (what the
    # algorithm drops) besides the construction (Sections 4 and 5), the trials, Section 7 and Section 10. H3's
    # extrapolation quotes the self-test of 6.5.
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
    path = data.RESEARCH / "public_text_scan.py"
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


def patch_program(tokens):
    """The six lines of experiments/halfsearch.py that hold the pin, the lengths, eta, the rule and the trials."""
    text = PROGRAM.read_bytes().decode("ascii")
    p = data.PIN
    want = {
        r"^X3, X7, X11, X15 = .*$": "X3, X7, X11, X15 = " + ", ".join(f"0x{p[k]:08X}" for k in ("X3", "X7", "X11", "X15")),
        r"^W4, W13 = .*$": f"W4, W13 = 0x{p['W4']:08X}, 0x{p['W13']:08X}",
        r"^ETA = .*$": f"ETA = 0x{data.ETA:08X}",
        r"^LEN_A, LEN_B = .*$": f"LEN_A, LEN_B = {data.LEN_A}, {data.LEN_B}",
        r"^RULE_CONDITIONS = .*$": f"RULE_CONDITIONS = {data.RULE_CONDITIONS}",
        r"^TRIALS_LOG2 = .*$": f"TRIALS_LOG2 = {127 - data.LOG2_FACTOR}",
    }
    new = text
    for pattern, line in want.items():
        new, count = re.subn(pattern, line, new, flags=re.M)
        if count != 1:
            raise SystemExit(f"experiments/halfsearch.py: expected one line matching {pattern}")
    return text, new


def check_program(d):
    spec = importlib.util.spec_from_file_location("halfsearch_pkg6", PROGRAM)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    same = ((m.X3, m.X7, m.X11, m.X15, m.W4, m.W13) == tuple(data.PIN[k] for k in ("X3", "X7", "X11", "X15", "W4", "W13"))
            and (m.LEN_A, m.LEN_B) == (data.LEN_A, data.LEN_B)
            and m.ETA == data.ETA and m.W4B == d["W4B"] and m.DELTA5 == d["delta"] and (m.Y3, m.Y3B, m.Y11, m.Y11B) ==
            (d["Y3"], d["Y3B"], d["Y11"], d["Y11B"]) and (m.CLASS_MASK, m.CLASS_VALUE) == (d["qmask"], d["qvalue"])
            and m.CLASS_SIZE == d["members"] and m.BATCHES == d["list_words"]
            and m.RULES == data.RULES and m.RULE_CONDITIONS == data.RULE_CONDITIONS
            and tuple(m.RULE_A) == tuple(data.RULE_A[data.ETA]) and all(m.rule_a(h) == data.rule_a(h) for h in data.RULE_A_PROBES)
            and (m.A_SHIFTS, m.A_ALL, m.A_VALUE) == (d["a_shifts"], d["a_all"], d["a_value"])
            and m.STAGE_2_LOG2_SHARE == data.STAGE_2_LOG2_SHARE and m.STAGE_2_BUDGET == d["list_words"] << d["stage2_shift"])
    stage_a, stage_2 = m.TABLE[:m.STAGE_A_PARTS], m.TABLE[m.STAGE_A_PARTS:]
    counts = (sum(r[1] for r in stage_a), sum(r[2] for r in stage_a), sum(r[1] for r in stage_2), sum(r[2] for r in stage_2))
    if not same:
        raise SystemExit("experiments/halfsearch.py does not have the pin, the lengths, the class, the list, the rules "
                         "and the stage-2 budget of pkg6_data.py")
    if counts != (data.STAGE_A_OPS, data.STAGE_A_LOADS, data.STAGE_2_OPS, data.STAGE_2_LOADS):
        raise SystemExit("the table of experiments/halfsearch.py does not have the stage counts of pkg6_data.py")


def main():
    check_only = "--check" in sys.argv
    if "--program" in sys.argv:
        old_program, new_program = patch_program(None)
        if new_program != old_program:
            print("DRIFT experiments/halfsearch.py: one of its six lines is not that of pkg6_data.py")
            return 1
        check_program(data.derive())
        print(f"experiments/halfsearch.py has the pin, lengths {data.LEN_A} and {data.LEN_B}, eta {data.ETA:08x}, the three rules, "
              f"RULE_CONDITIONS = {data.RULE_CONDITIONS}, the stage-2 budget and the stage counts of pkg6_data.py: stage A "
              f"{data.STAGE_A_OPS} operations and {data.STAGE_A_LOADS} loads, stage 2 {data.STAGE_2_OPS} and {data.STAGE_2_LOADS}")
        return 0
    if "--manifest" in sys.argv:
        old_program, new_program = patch_program(None)
        if new_program != old_program:
            raise SystemExit("experiments/halfsearch.py: one of its six lines is not that of pkg6_data.py; manifest not rendered")
        d = data.derive()
        check_program(d)
        manifest = render((SRC / "manifest.json").read_text(encoding="ascii"), data.program_tokens(d), reflow=False)
        mf = json.loads(manifest)
        problems = [f"manifest {e['id']}.{k} is {len(e[k])} characters (limit 2000)" for e in mf["experiments"]
                    for k in ("scope", "hypothesis") if len(e[k]) > 2000]
        if TOKEN.search(manifest) or "[[" in manifest or "\r" in manifest or "\t" in manifest:
            problems.append("manifest: a name, a placeholder, CR or tab is left")
        if problems:
            raise SystemExit("not written:\n  " + "\n  ".join(problems))
        new = manifest.encode("ascii")
        changed = not MANIFEST.exists() or MANIFEST.read_bytes() != new
        if changed:
            MANIFEST.write_bytes(new)
        print(f"{'written  ' if changed else 'unchanged'}  {MANIFEST.relative_to(PKG)}  ({len(new)} bytes); scope and hypothesis lengths "
              f"{[(e['id'], len(e['scope']), len(e['hypothesis'])) for e in mf['experiments']]}")
        return 0
    if not data.TEXT_PORTED:
        raise SystemExit("not built: pkg6_data.TEXT_PORTED is False. Nothing was read or written. Use --program to compare the "
                         "program with the data module.")
    old_program, new_program = patch_program(None)
    if new_program != old_program:
        if check_only:
            print("DRIFT experiments/halfsearch.py: one of its six lines is not that of pkg6_data.py")
        else:
            PROGRAM.write_bytes(new_program.encode("ascii"))
            print("experiments/halfsearch.py: pin and eta written")
    d, tokens = data.build_tokens()
    check_program(d)
    if data.MEMORY_LOG2 != 35:
        print("NOTE: MEMORY_LOG2 changed; the paragraph 'Memory of the preprocessing' in src/proof_head.md states 2^35 in words")
    # the two templates are joined with one empty line between them, whatever the first one ends with
    proof = render((SRC / "proof_head.md").read_text(encoding="ascii").rstrip("\n") + "\n\n"
                   + (SRC / "proof_evidence.md").read_text(encoding="ascii"), tokens)
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
    if c["claim"] != {"time_log2": float(tokens["time_log2"]), "time_unit": "target-compressions", "memory_log2_bytes": data.MEMORY_LOG2,
                      "preprocessing_log2": data.PREPROCESSING_LOG2, "success_probability": 0.39,
                      "nonuniform_advice_log2_bytes": data.ADVICE_LOG2}:
        problems.append("the claim block of claim.json is not that of pkg6_data.py")
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
    print("ranges:", {k: ranges[k] for k in ("constr", "trials", "early", "algo", "batch", "s7", "h2", "h3", "s10")})
    print(f"claim: time_log2 {tokens['time_log2']}, factor 2^{tokens['F']}, trials 2^{tokens['T']}, charge {tokens['charge']}, count with "
          f"rule A {tokens['rule_count']} (all solutions {tokens['exact_total']}), class {tokens['eta']} ({tokens['members']} members); "
          f"note {len(note.encode('ascii'))} bytes")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
