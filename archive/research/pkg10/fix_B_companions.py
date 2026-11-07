"""Apply fixB's companion edits (A, D, E, F, G), its field bullet and its claim change, and move the search memory
from 2^23 to 2^26 bytes everywhere. Exact-once replacements; stops before writing if any does not match."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, re, sys
K = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/')
P, C, N = K + "pkg/blake3-r2/proof.md", K + "pkg/blake3-r2/claim.json", K + "pkg/submission-note-r2.md"
rd = lambda p: open(p, encoding="utf-8", newline="\n").read()

proof_pairs = [
    # A, with the memory figure of the cluster layout
    ("search needs less than 2^23 bytes of memory; the declared 2^35 bytes also cover\nthe computations by which the constants, the class, the sub-class and the rule\nwere selected (Sections 6 to 9).",
     "search needs less than 2^26 bytes of memory; the declared 2^35 bytes also cover\nthe selection procedure of Section 9, whose cost, below 2^80 units, is part of\nthat total."),
    # D
    ("Section 9 of this text is worded accordingly.",
     "Section 9 of this text replaces that estimate by a selection procedure with\n   a bound."),
]
# Field meanings: preprocessing bullet and memory bullet
field_old_pre = re.compile(r"- preprocessing_log2 = 63 bounds[^\n]*(?:\n  [^\n]*)*")
field_new_pre = ("- preprocessing_log2 = 80 bounds the selection procedure SEL of Section 9 by\n"
                 "  2^80 target-compression units (fewer than 2^88.45 primitive operations).\n"
                 "  Every search of SEL runs over a stated range and every program run in it\n"
                 "  halts at a stated cap, so this is a bound by construction; that SEL returns\n"
                 "  the stored constants rests on the participant's records (Sections 8, 9).")
mem_pairs = [("| search memory | below 2^22 bytes | below 2^23 bytes |", "| search memory | below 2^22 bytes | below 2^26 bytes |"),
             ("the search alone needs less than 2^23 bytes (Section 9).", "the search alone needs less than 2^26 bytes (Section 9)."),
             ("within memory_log2_bytes = 35 but above Section 9's search-alone figure.",
              "within memory_log2_bytes = 35 and within Section 9's figure for the search.")]

t = rd(P); bad = []
for a, b in proof_pairs + mem_pairs:
    if t.count(a) != 1: bad.append(f"proof x{t.count(a)}: {a[:80]!r}")
m = field_old_pre.findall(t)
if len(m) != 1: bad.append(f"field preprocessing bullet found {len(m)} times")
# E: Section 12 "The same" sentence and a new table row
e_old = "the declared figures for preprocessing, memory and advice (the advice is 48 bytes in place of 40)."
if t.count(e_old) != 1:
    e_old = re.sub(r"\s+", " ", e_old)
    if re.sub(r"\s+", " ", t).count(e_old) != 1: bad.append("Section 12 'The same' sentence not found")
# F: credit to winglock in Section 13
f_anchor = "the idea is winglock's."
if t.count(f_anchor) != 1: bad.append(f"Section 13 winglock anchor x{t.count(f_anchor)}")
n = rd(N)
g_anchor = "the selection has only an estimate from running times."
if n.count(g_anchor) != 1: bad.append(f"note G anchor x{n.count(g_anchor)}")
cj = json.loads(rd(C))
r5 = cj["restrictions"][5]
cm = rd(K + "fixB/CLAIM.md")
olds = re.findall(r"Old passage \(verbatim\):\n\n((?:> [^\n]*\n?)+)", cm)
news = re.findall(r"Replacement \(one JSON string[^\n]*\n\n((?:> [^\n]*\n?)+)", cm)
clean = lambda q: " ".join(l[2:] for l in q.strip().split("\n")).strip()
if len(olds) != 1 or len(news) != 1: bad.append(f"CLAIM.md old/new blocks: {len(olds)}/{len(news)}")
elif clean(olds[0]) not in r5: bad.append("restrictions[5] old passage not found verbatim")
if bad:
    print("STOP:"); print("\n".join(bad)); sys.exit(1)

for a, b in proof_pairs + mem_pairs: t = t.replace(a, b)
t = field_old_pre.sub(field_new_pre, t, count=1)
# E, tolerant of the line wrap
idx = re.sub(r"\s+", " ", t).find(e_old)
pat = re.compile(r"\s+".join(map(re.escape, e_old.split(" "))))
t = pat.sub("the declared figures for memory and advice (the advice is 48 bytes in\nplace of 40).", t, count=1)
row_anchor = re.search(r"\n\| time_log2 \| 97\.6 \| [0-9.]+ \|", t)
t = t[:row_anchor.start()] + "\n| preprocessing | 2^63, two words recomputed | 2^80, selection (Section 9) |" + t[row_anchor.start():]
t = t.replace(f_anchor, f_anchor + " Step 4 of the selection procedure of Section 9 follows\n  winglock's choice of the sub-class S8 in entries 2125212 and 2bb5d604 from the\n  exact rate of every member of the class.", 1)
open(P, "w", encoding="utf-8", newline="\n").write(t)
n = n.replace(g_anchor, g_anchor + " This package gives the selection as a\n  procedure with a bound of 2^80 units (proof.md Section 9).", 1)
open(N, "w", encoding="utf-8", newline="\n").write(n)
cj["restrictions"][5] = r5.replace(clean(olds[0]), clean(news[0]))
cj["claim"]["preprocessing_log2"] = 80
open(C, "w", encoding="utf-8", newline="\n").write(json.dumps(cj, indent=2, ensure_ascii=False) + "\n")
print("fixB companions A, D, E, F, G applied; field bullets; restrictions[5]; preprocessing_log2 = 80; memory 2^26")
