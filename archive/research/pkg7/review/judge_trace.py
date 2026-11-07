#!/usr/bin/env python3
"""Review helper (lens: judge). Reads only; writes review/judge_trace.txt.

1. Every figure of proof.md, claim.json and the note with at least four digits (or a decimal point) is looked up,
   as a string without thousands separators, in the files of evidence/ (text files only) and in the program. Figures
   found nowhere are listed for a look by hand (many are arithmetic).
2. claim.json: field lengths, the cited line ranges with the first and the last line of each, ASCII.
3. SHA-256 of the rendered files against FILE_STEPS.md and evidence/validation_log.txt.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
CAND = PKG / "blake3-r2"
out = []


def say(*a):
    out.append(" ".join(str(x) for x in a))


# ---- 1. figures
pool = {}
for p in sorted((PKG / "evidence").rglob("*")):
    if p.is_file() and p.suffix in (".txt", ".json", ".log", ".csv", ".rs"):
        try:
            pool[str(p.relative_to(PKG))] = p.read_text(encoding="utf-8", errors="replace").replace(",", "")
        except OSError:
            pass
pool["program"] = (CAND / "experiments" / "halfsearch.py").read_text(encoding="utf-8").replace(",", "").replace("_", "")
big = "\n".join(pool.values())

FIG = re.compile(r"(?<![\w.^])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d{4,})(?![\w])")
for name, path in (("proof", CAND / "proof.md"), ("claim", CAND / "claim.json"), ("note", PKG / "submission-note-r2.md")):
    text = path.read_text(encoding="utf-8")
    missing = {}
    total = 0
    for ln, line in enumerate(text.splitlines(), 1):
        for m in FIG.finditer(line):
            tok = m.group(1)
            plain = tok.replace(",", "")
            total += 1
            if plain in big:
                continue
            # a figure printed with fewer decimals than the file has
            if "." in plain and re.search(re.escape(plain.rstrip("0")), big):
                continue
            missing.setdefault(tok, []).append(ln)
    say(f"== {name}: {total} figures, {len(missing)} distinct ones not found as a string in evidence/ or the program")
    for tok, lns in sorted(missing.items(), key=lambda kv: kv[1][0]):
        say(f"   {tok:>24}  line {lns[0]}" + (f" (+{len(lns) - 1})" if len(lns) > 1 else ""))

# ---- 2. claim.json
claim = json.loads((CAND / "claim.json").read_text(encoding="utf-8"))
proof_lines = (CAND / "proof.md").read_text(encoding="utf-8").splitlines()
say("== claim.json")
say("   state", claim["submission_state"], " time_log2", claim["claim"]["time_log2"])
for i, r in enumerate(claim["restrictions"]):
    say(f"   restriction {i}: {len(r)} characters")
for h in claim["heuristics"]:
    for k, v in h.items():
        if isinstance(v, str):
            say(f"   {h['id']} {k}: {len(v)} characters" + ("  <-- above 4096" if len(v) > 4096 else ""))
    for e in h["evidence_ids"]:
        m = re.fullmatch(r"proof:(\d+)-(\d+)", e)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            before = proof_lines[a - 2] if a >= 2 else ""
            after = proof_lines[b] if b < len(proof_lines) else ""
            say(f"   {h['id']} {e}: first [{proof_lines[a - 1][:60]}] last [{proof_lines[b - 1][-50:]}] "
                f"line before blank: {before.strip() == ''} line after blank: {after.strip() == ''}")
for name, path in (("proof", CAND / "proof.md"), ("claim", CAND / "claim.json"), ("note", PKG / "submission-note-r2.md"),
                   ("program", CAND / "experiments" / "halfsearch.py"), ("manifest", CAND / "experiments" / "manifest.json"),
                   ("certificates", CAND / "certificates" / "manifest.json")):
    raw = path.read_bytes()
    bad = sorted({b for b in raw if b > 126 or (b < 32 and b not in (10, 13, 9))})
    tabs = raw.count(b"\t")
    crlf = raw.count(b"\r\n")
    longest = max((len(x) for x in raw.split(b"\n")), default=0)
    say(f"   {name}: {len(raw)} bytes, non-ASCII or control bytes {bad}, tabs {tabs}, CRLF {crlf}, longest line {longest}, "
        f"sha256 {hashlib.sha256(raw).hexdigest()}")

# ---- 3. hashes quoted
for label, path in (("FILE_STEPS.md", PKG / "FILE_STEPS.md"), ("validation_log.txt", PKG / "evidence" / "validation_log.txt"),
                    ("note", PKG / "submission-note-r2.md"), ("selftest_pkg6_all", PKG / "evidence" / "selftest_pkg6_all.txt"),
                    ("selftest_pkg6_text_final", PKG / "evidence" / "selftest_pkg6_text_final.txt"),
                    ("proof_lines_check", PKG / "evidence" / "proof_lines_check.txt")):
    t = path.read_text(encoding="utf-8", errors="replace")
    say(f"== hashes quoted in {label}")
    for m in sorted(set(re.findall(r"\b[0-9a-f]{64}\b", t))):
        say("   ", m)
    for m in sorted(set(re.findall(r"\b([0-9a-f]{8})\.\.\.([0-9a-f]{4})\b", t))):
        say("    short", m)

(HERE / "judge_trace.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"{len(out)} lines -> judge_trace.txt")
