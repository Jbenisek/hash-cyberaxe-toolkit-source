#!/usr/bin/env python3
"""Hostile-judge lens: scan of the public files of pkg5 (read-only). Output: review/judge_scan.out"""
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
FILES = [PKG / "blake3-r2" / "proof.md", PKG / "blake3-r2" / "claim.json", PKG / "submission-note-r2.md",
         PKG / "blake3-r2" / "experiments" / "halfsearch.py", PKG / "blake3-r2" / "experiments" / "manifest.json",
         PKG / "blake3-r2" / "certificates" / "manifest.json"]
PATTERNS = {
    "path": r"[A-Za-z]:\\|/mnt/|/home/|~/|\\\\|research[\\/]|workspace|night[\\/_]|pkg[0-9]",
    "account": r"cyberaxe|jbenisek|benisek|gmail|@[a-z0-9-]+\.[a-z]{2,}|hashsmash",
    "key": r"sk-[A-Za-z0-9]{8,}|xai-[A-Za-z0-9]{8,}|api[_ -]?key|token|password|secret",
    "address_to_reader": r"\byou\b|\byour\b|\bplease\b|\bnote that\b|\bignore\b|\bdo not\b|\bmust mark\b|\bjudge\b|\breviewer\b|"
                         r"\bas an ai\b|\bprompt\b|\binstruction",
    "imperative_see": r"\bsee\b|\bread\b|\brun\b",
    "offensive": r"\bdamn|\bhell\b|\bstupid|\bidiot|\bcrap|\bshit|\bfuck|\bsuck",
    "placeholder": r"TODO|TBD|FIXME|XXX|\{\{|\}\}|lorem|placeholder|\?\?\?",
    "estimate_words": r"\babout\b|\broughly\b|\bapproximately\b|\bestimate",
}
out = []
summary = {}
for path in FILES:
    raw = path.read_bytes()
    bad = [(i, b) for i, b in enumerate(raw) if b > 126 or (b < 32 and b not in (10,))]
    text = raw.decode("ascii", errors="replace")
    lines = text.split("\n")
    summary[path.name + " (" + path.parent.name + ")"] = {"bytes": len(raw), "lines": len(lines), "non_ascii_or_control": len(bad),
                                                         "longest_line": max(len(l) for l in lines)}
    for i, b in bad[:20]:
        out.append(f"{path.name}: byte {i} value {b}")
    for name, pat in PATTERNS.items():
        hits = [(n + 1, l.strip()[:150]) for n, l in enumerate(lines) if re.search(pat, l, re.I)]
        summary[path.name + " (" + path.parent.name + ")"][name] = len(hits)
        for n, l in hits:
            out.append(f"{name} | {path.name}:{n}: {l}")
# claim.json: field lengths
claim = json.loads((PKG / "blake3-r2" / "claim.json").read_text(encoding="ascii"))
for h in claim["heuristics"]:
    for k, v in h.items():
        if isinstance(v, str):
            out.append(f"claimlen | {h['id']} {k}: {len(v)}")
for i, r in enumerate(claim["restrictions"]):
    out.append(f"claimlen | restriction {i}: {len(r)}")
# evidence ranges
proof = (PKG / "blake3-r2" / "proof.md").read_text(encoding="ascii").split("\n")
for h in claim["heuristics"]:
    for e in h["evidence_ids"]:
        m = re.match(r"proof:(\d+)-(\d+)", e)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            out.append(f"range | {h['id']} {e}: first [{proof[a - 1][:70]}] last [{proof[b - 1][:70]}] next [{proof[b][:50] if b < len(proof) else ''}]")
(PKG / "review" / "judge_scan.out").write_text("\n".join(out) + "\n", encoding="ascii", errors="replace")
for k, v in summary.items():
    print(k, json.dumps(v))
print("lines written", len(out))
