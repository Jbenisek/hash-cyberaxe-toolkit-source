#!/usr/bin/env python3
"""judge7 (hostile-judge lens): every figure of proof.md (from Section 6 on), claim.json and the note of the pkg7
draft with four digits or a decimal point, looked up as a string (no thousands separators) in the evidence of this
package and in the sources it quotes. Figures found nowhere go to judge7_trace.txt for a look by hand; most of them
are arithmetic, recomputed in judge7_numbers.py. Reads only."""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
RES = PKG.parent
WS = RES.parent
CAND = PKG / "blake3-r2"
src = []
for d, pats in ((PKG / "work" / "evidence", ("*.txt", "*.json")), (PKG / "work" / "text", ("*.txt", "*.json")),
                (PKG / "count", ("*.txt", "*.md", "*.tsv", "*.log")), (RES / "pkg7_prep", ("**/VERDICT.md", "**/LAYOUT_REPORT.md", "**/*STEP.md", "**/COST*.txt")),
                (RES / "proveout", ("**/AUDIT.md", "**/RESULTS.md", "**/VERDICT.md")),
                (WS / "astra-jobs" / "server_tasks_2026-10-06", ("gpt_sol_answer_[KLMNO].md", "task5_small_h8/ref/LOCAL_RESULTS.txt")),
                (RES / "grok", ("answer18_redteam6.md", "work/job15_batch/ANSWER.md")), (RES / "others", ("CREDIT.md", "TECHNIQUES.md")),
                (RES / "pkg6", ("blake3-r2/proof.md", "blake3-r2/claim.json", "submission-note-r2.md", "evidence/**/*.txt"))):
    for pat in pats:
        src += [p for p in d.glob(pat) if p.is_file() and "proof_before" not in p.name and "claim_before" not in p.name]
src += [PKG / "COST.txt", PKG / "PROGRAM_STEP.md", CAND / "experiments" / "halfsearch.py"]
big = "\n".join(p.read_text(encoding="utf-8", errors="replace").replace(",", "") for p in src)
FIG = re.compile(r"(?<![\w.^])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d{4,})(?![\w])")
out = [f"sources read: {len(src)} files"]
for name, path, first in (("proof", CAND / "proof.md", 541), ("claim", CAND / "claim.json", 1), ("note", PKG / "submission-note-r2.md", 1)):
    missing, total = {}, 0
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if ln < first:
            continue
        for m in FIG.finditer(line):
            tok = m.group(1)
            plain = tok.replace(",", "")
            total += 1
            if plain in big or ("." in plain and plain.rstrip("0") in big):
                continue
            missing.setdefault(tok, []).append(ln)
    out.append(f"== {name}: {total} figures from line {first}, {len(missing)} distinct ones found in no source")
    out += [f"   {tok:>22}  line {lns[0]}" + (f" (+{len(lns) - 1})" if len(lns) > 1 else "") for tok, lns in sorted(missing.items(), key=lambda kv: kv[1][0])]
(HERE / "judge7_trace.txt").write_text("\n".join(out) + "\n", encoding="ascii")
print("\n".join(l for l in out if l.startswith("==") or l.startswith("sources")))
