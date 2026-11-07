#!/usr/bin/env python3
"""One-off: copy the passages of the filed text (entry c66f230d, research/pkg6/blake3-r2/proof.md, read only) that
this package keeps into src/parts/, with the few word changes listed below. Each span is checked by its first and
last words, each change must match exactly once. Run again only if the list changes; the build reads src/parts and
never the filed folder. Research helper, not submitted.

    python -B tools/extract_parts.py
"""
import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
FILED = PKG.parent / "pkg6" / "blake3-r2" / "proof.md"
WANT = "3e11b6846e3fa8e30f561e00ab324a1fc7fc160b097b41bb876ddf979e5d3fa2"
OUT = PKG / "src" / "parts"

# name: (first line, last line, first words, last words, joined?, changes)
SPANS = {
    "s1_s3": (68, 225, "## 1. Exact complete hash", "is a collision exactly when R = 0.", False, ()),
    "class_q": (445, 474, "*The class.* The first message word", "bits free. QED.", False, ()),
    "residual": (490, 505, "**6.2 The residual of a trial.**", "a prime marks message B.", False,
                 (("known from step T without", "known from step Y without"),)),
    "lemma_n": (530, 550, "**Lemma N.** For a trial of 6.1", "the eta of E3 is the constant of the class.", False, ()),
    "packed": (642, 660, "**6.5 Seven trials in one word.**", "What is evaluated in the\nlanes here is different.", False, ()),
    "count_12": (1100, 1128, "**How r is counted (participant computation", "has two candidates for eps.", False,
                 (("As in the proof of Lemma E, E1's d and b", "E1's a1 and d1 are the same for A and B, so its d and b"),)),
    "count_3": (1129, 1142, "3. *The E3 side.*", "count.", True,
                ((" When the enumeration exceeds a work budget the program uses a uniform random subset with the matching "
                  "weight; it reports every outcome for which it did, and such a value is an estimate and not a count.",
                  " The counter of this package returns an integer for every outcome and has no sampling branch."),)),
    "count_4": (1143, 1157, "4. *The E1 side.*", "not a count.", True,
                ((" When the list of the db or of the dd exceeds a limit the program falls back to a product formula that "
                  "treats the additions as independent; it reports every outcome for which it did, and such a value is "
                  "not a count.",
                  " The counter of this package forms the count as an integer for every outcome; no outcome of the "
                  "count below needed a fallback."),)),
}


def main():
    raw = FILED.read_bytes()
    if hashlib.sha256(raw).hexdigest() != WANT:
        raise SystemExit("the filed proof does not have the SHA-256 of entry c66f230d")
    lines = raw.decode("ascii").split("\n")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (a, b, first, last, joined, changes) in SPANS.items():
        text = "\n".join(lines[a - 1:b])
        if not text.startswith(first) or not text.endswith(last):
            raise SystemExit(f"{name}: the span {a}-{b} does not begin or end as expected")
        if joined:
            text = " ".join(text.split())
        for old, new in changes:
            if text.count(old) != 1:
                raise SystemExit(f"{name}: expected exactly one place for {old[:50]!r}")
            text = text.replace(old, new)
        (OUT / f"{name}.md").write_bytes((text + "\n").encode("ascii"))
        print(f"{name}: lines {a}-{b}, {len(text)} characters, {len(changes)} change(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
