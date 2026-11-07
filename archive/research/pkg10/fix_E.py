"""Make every statement of the stage-2 budget E match the program: E = STAGE_2_BUDGET = RUN_PAIRS * 2,341 >> 8,
one in 32 of the representative words of J pairs; neighbour words have their own budget S. Exact-once replacements."""

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

import json, sys
P = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/blake3-r2/')
PROOF = [
    ("0; or if E batches have run stage 2; or if G representatives have opened",
     "0; or if E representative words have run stage 2; or if G representatives have opened"),
    ("       E = 18,725 * J / 32 rounded down,",
     "       E = 2,341 * J / 256 rounded down,"),
    ("at least J, and 18,725 batches for each pair. So E is less than one part in 32\nof the batches of a run.",
     "at least J. One value of X2 in eight holds representatives, 2,341\nrepresentative words of seven lanes each, so E is one part in 32 of the\nrepresentative words of J pairs; a neighbour word that enters stage 2 counts\nagainst S and not against E."),
    ("- The entry count: the number of batches that have run stage 2 is advanced and\n  compared with its budget E (step 4).",
     "- The entry count: the number of representative words, or of neighbour words,\n  that have run stage 2 is advanced and compared with its budget, E or S (step\n  4)."),
    ("fewer than E of the batches of a run hold a trial that satisfies rule A, where\nE is the budget of step 4, just under one in 32 of the batches.",
     "fewer than E of the representative words of a run hold a trial that satisfies\nrule A, where E is the budget of step 4, one in 32 of the representative words."),
    ("1.1429 times 2^-8 of the trials, where a uniform h1 satisfies the rule with",
     "1.1430 times 2^-8 of the representatives, where a uniform h1 satisfies the rule with"),
    ("against the budget 0.03125; single contexts have between 0.0071 and 0.0421, so",
     "against the budget 0.03125, and on words of seven representatives, the words E\ncounts, 0.026178 and, in a second program, 0.02622 (Section 10); single\ncontexts have between 0.0071 and 0.0421, so"),
    ("such a word has 1.81 open lanes.",
     "such a word has 1.81 open lanes. A word of seven representatives has a lane\nthat satisfies rule A with share 0.026178, against 0.027016 for independent\nlanes, and 0.02622 over 393,216 values of X2 in a second program."),
]
CLAIM_H3 = {
    "statement": ("fewer than E of the batches of a run hold a trial that satisfies rule A of proof.md Section 6.3, where E is "
                  "the budget of Section 6.4, just under one in 32 of the batches; so fewer than E batches run stage 2.",
                  "fewer than E of the representative words of a run hold a trial that satisfies rule A of proof.md "
                  "Section 6.3, where E is the budget of Section 6.4, one in 32 of the representative words; so fewer than E "
                  "representative words run stage 2. Neighbour words have their own budget (H6)."),
    "scope": ("The budget E is 18,725 * J / 32 rounded down,", "The budget E is 2,341 * J / 256 rounded down,"),
}
CLAIM_H3_SCOPE2 = [
    ("a run has at least J pairs of an outer step and a value of X2 and 18,725 batches per pair. The time bound charges "
     "stage 2 for that many batches,",
     "a run has at least J pairs of an outer step and a value of X2, one value of X2 in eight holds representatives, and "
     "it holds 2,341 representative words; E is one in 32 of the representative words of J pairs, the constant "
     "STAGE_2_BUDGET of the submitted program. The time bound charges stage 2 for that many representative words,"),
    ("It holds whenever fewer than E trials of the run satisfy rule A, a share of 1.1429 times 2^-8 of the trials.",
     "It holds whenever fewer than E representatives of the run satisfy rule A, a share of 1.1430 times 2^-8 of the "
     "representatives."),
]
t = open(P + "proof.md", encoding="utf-8", newline="\n").read(); bad = []
for a, b in PROOF:
    if t.count(a) != 1: bad.append(f"proof x{t.count(a)}: {a[:70]!r}")
c = json.load(open(P + "claim.json", encoding="utf-8"))
h3 = [x for x in c["heuristics"] if x["id"] == "H3-stage-2-entries"][0]
for k, (a, b) in CLAIM_H3.items():
    if h3[k].count(a) != 1: bad.append(f"claim H3.{k} x{h3[k].count(a)}: {a[:70]!r}")
for a, b in CLAIM_H3_SCOPE2:
    if h3["scope"].count(a) != 1: bad.append(f"claim H3.scope x{h3['scope'].count(a)}: {a[:70]!r}")
if bad:
    print("STOP:"); print("\n".join(bad)); sys.exit(1)
for a, b in PROOF: t = t.replace(a, b)
for k, (a, b) in CLAIM_H3.items(): h3[k] = h3[k].replace(a, b)
for a, b in CLAIM_H3_SCOPE2: h3["scope"] = h3["scope"].replace(a, b)
open(P + "proof.md", "w", encoding="utf-8", newline="\n").write(t)
open(P + "claim.json", "w", encoding="utf-8", newline="\n").write(json.dumps(c, indent=2, ensure_ascii=False) + "\n")
print(f"E made consistent: {len(PROOF)} proof passages, H3 statement and scope in claim.json")
