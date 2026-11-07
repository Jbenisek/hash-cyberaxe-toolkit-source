#!/usr/bin/env python3
# lens EVERY FIGURE: numbers of claim.json and of the note that do not occur in proof.md, and pkg4 leftovers

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

import json, re
B = _hca_public_path_text('__HCA_WORKSPACE__/research')
P5 = B + "/pkg5"
out = open(P5 + "/review/fig_cross.out", "w")
def say(*a): print(*a, file=out)
proof = open(P5 + "/blake3-r2/proof.md").read()
claim_raw = open(P5 + "/blake3-r2/claim.json").read()
note = open(P5 + "/submission-note-r2.md").read()
manifest = open(P5 + "/blake3-r2/experiments/manifest.json").read()
prog = open(P5 + "/blake3-r2/experiments/halfsearch.py").read()
flat = lambda s: re.sub(r"\s+", " ", s)
NUM = re.compile(r"(?<![\w.])(?:2\^-?\d+(?:\.\d+)?|[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[+-]?\d+\.\d+(?:e-?\d+)?|\d{3,}|[0-9a-f]{8})(?![\w])")
def nums(s):
    return set(m.group(0).lstrip("+") for m in NUM.finditer(flat(s)))
np_, nc, nn, nm = nums(proof), nums(claim_raw), nums(note), nums(manifest)
say("numbers in claim.json not in proof.md:", sorted(nc - np_))
say("numbers in the note not in proof.md:", sorted(nn - np_))
say("numbers in the experiment manifest not in proof.md:", sorted(nm - np_))
# pkg4 leftovers: figures that belong to the one-stage batch
left = ["154", "74", "228", "2,134,764", "2,135,020", "2,228,224", "32.578", "93,200", "4.4%", "100.36", "100.3506", "100.33927", "5.08746", "102.01", "102.087",
        "123.34", "123.4", "101.4", "2^92", "2^102", "2^-12", "26.52", "77.48", "14.52", "14.54", "7.08", "18,726", "19,456", "622,592", "2^21", "0.999 ", "0.001",
        "early-test passes suffices", "two lists", "H1 and H2", "Neither heuristic", "two heuristics", "lanes equal", "batch_operations", "batch_loads", "1.79", "2.17", "V[j]", "100.4"]
for name, text in (("proof", proof), ("claim", claim_raw), ("note", note), ("manifest", manifest), ("program", prog)):
    f = flat(text)
    hits = []
    for s in left:
        for m in re.finditer(re.escape(s), f):
            hits.append((s, f[max(0, m.start() - 60):m.end() + 40]))
    say("== leftovers in", name, ":", len(hits))
    for s, ctx in hits:
        say("   [%s] ...%s..." % (s, ctx))
# the same statement in three places: selected figures
for s in ["29,977,922", "29,965,882", "12,040", "12,039.8", "0.041%", "0.999598", "0.999839", "3.57", "8,375,631", "17.4", "16.756", "16.448", "1,098,067.75", "99.37282", "99.3841", "99.39",
          "2^-10.12", "2^-29.42", "2^74.58", "2^13.42", "2^13.47", "2^-29.56", "2^-5.81", "0.10938", "0.10937", "0.109375", "1.142", "17,179,784,810", "1,390", "11,407", "261,798", "205,330",
          "0.0856", "2^-6.004", "9.496", "8.509", "215", "177", "130,929", "102,378", "13,337", "13,505.6", "93.3", "0.96", "0.97", "13.0", "122.4", "100.4", "7.1", "1.78", "2.16", "4.33", "36,358,944",
          "0.8866", "0.10 bit", "-0.002", "0.973", "40 bytes", "2^6", "247", "270", "242", "215 without", "508", "2^20"]:
    say("%-16s proof %d  claim %d  note %d" % (s, flat(proof).count(s), flat(claim_raw).count(s), flat(note).count(s)))
out.close()
print("written")
