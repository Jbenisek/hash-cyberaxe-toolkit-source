#!/usr/bin/env python3
# lens EVERY FIGURE: the fixes that the two pkg4 rechecks list, looked up in the pkg5 files (present / absent)

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

import re
B = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg5')
flat = lambda p: re.sub(r"\s+", " ", open(p).read())
proof, claim, note = flat(B + "/blake3-r2/proof.md"), flat(B + "/blake3-r2/claim.json"), flat(B + "/submission-note-r2.md")
out = open(B + "/review/fig_regress.out", "w")
must = [  # (what, where, text that must be there)
    ("34 classes", "proof", "34 classes of these constants"), ("34 classes", "claim", "second largest of 34 classes"), ("34 classes", "note", "34 classes of these constants"),
    ("40 pairs in 33", "proof", "40 pairs in 33 different classes"), ("40 pairs in 33", "note", "40 pairs in 33 different classes"),
    ("21 sets", "proof", "it held 21 sets"), ("21 sets", "note", "returned 21 such sets"),
    ("e74181df checks exist", "proof", "24 outcomes, largest difference 0.00 bits"), ("e74181df 2^44", "proof", "40 seen where the expectation file of that run has 37.52"),
    ("e3deep model", "proof", "found 161, where 176.5 are expected"),
    ("2^24.84", "proof", "about 2^24.84"), ("2^-103.16", "proof", "about 2^-103.16"), ("2^-103.16", "claim", "about 2^-103.16"), ("2^24.84", "note", "about 2^24.84"), ("2^-103.16", "note", "about 2^-103.16"),
    ("43.16 / 86.32", "proof", "In each 43.16 such trials are expected"), ("86.32", "claim", "predicts 86.32"), ("86.32", "note", "predicts 86.32"), ("628.75", "proof", "628.75 by the counts N1"),
    ("partial E3 2^-34.54 in note end", "note", "the count of partial E3 events 2^-34.54"),
    ("plan 03:22", "proof", "in the helper's log at 03:22"),
    ("36,358,944 in claim", "claim", "has 36,358,944 over the same values of beta"),
    ("listed-beta shortfall", "claim", "about 6 in a million too rarely (-2.3 standard deviations over 2^45 trials)"), ("listed-beta shortfall", "note", "about 6 in a million"),
    ("AI model wording", "proof", "further instances of the AI model that wrote this package"),
    ("shared seed words in H2 limitations", "claim", "in eight runs with shared seed words"),
    ("two counts recorded", "proof", "These runs record these two counts and nothing else"), ("two counts recorded", "note", "These runs record only the early test and the number of trials in which E1 requires the class"),
    ("common list not even-handed", "proof", "The common list is not even-handed between classes"),
    ("toy sets not simply random", "proof", "Jobs B, C, F and G keep only the sets whose best class has a rate per member above a threshold"),
    ("1.60 series in claim", "claim", "variance-to-mean ratio of its collisions per run of 1.60"),
    ("depths in claim", "claim", "the first on an event of probability 2^-38.57 per trial, the second, without the third of its conditions, on one of 2^-34.54"),
    ("second deep E1 +2.4 in limitations", "claim", "one is 2.4 standard deviations above its prediction"),
]
src = {"proof": proof, "claim": claim, "note": note}
miss = 0
for what, where, text in must:
    ok = text in src[where]
    miss += not ok
    print(("present  " if ok else "ABSENT   ") + where + ": " + what + (" | " + text if not ok else ""), file=out)
stale = ["2^24.83", "2^-103.17", "43.12 such", "86.24", "16 classes", "37 pairs in 31", "19 sets", "2^14.52", "2^14.54", "helper agents of the same model", "record the early test only"]
for s in stale:
    for name, t in src.items():
        if s in t:
            print("STALE    %s: %s | ...%s..." % (name, s, t[max(0, t.find(s) - 80):t.find(s) + 60]), file=out)
            miss += 1
print("problems:", miss, file=out)
out.close()
print("problems:", miss)
