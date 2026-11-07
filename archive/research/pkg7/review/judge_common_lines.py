#!/usr/bin/env python3
"""Review helper (lens: judge). Sentences of pkg6's public files that are word for word in pkg5's as well and that
carry a figure, a name of a lemma or a file: these are the places where something false could be left over.
Writes review/judge_common_proof.txt and review/judge_common_note.txt. Reads only."""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG6 = HERE.parent
PKG5 = PKG6.parent / "pkg5"


def sentences(text):
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.:;]) (?=[A-Z*`(|])", text) if s.strip()]


for name, rel in (("proof", "blake3-r2/proof.md"), ("note", "submission-note-r2.md")):
    old = set(sentences((PKG5 / rel).read_text(encoding="utf-8")))
    new = sentences((PKG6 / rel).read_text(encoding="utf-8"))
    same = [s for s in new if s in old]
    keep = [s for s in same if re.search(r"\d", s) and len(s) > 40]
    out = HERE / f"judge_common_{name}.txt"
    out.write_text("\n".join(keep) + "\n", encoding="utf-8")
    print(f"{name}: {len(new)} sentences, {len(same)} also in pkg5, {len(keep)} of those with a figure -> {out.name}")
