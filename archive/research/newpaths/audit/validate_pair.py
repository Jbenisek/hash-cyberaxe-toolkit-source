"""Numeric validation at w=8 of a random sample of the 2^64-table ("pair") rules of rulesets.py, same method as
rules.py: the true target value must always be consistent; report P(0 solutions) per target and the mean."""
import random
import sys

sys.dont_write_bytecode = True
HERE = __file__.rsplit("\\", 1)[0]
sys.path.insert(0, HERE + "\\orig")
from rules import validate  # noqa: E402
from rulesets import get  # noqa: E402

lines = []
for variant in ("fixed", "outhalf"):
    _, _, _, _, orig = get(variant, "len64", "gen")
    _, _, _, _, allr = get(variant, "len64", "pair")
    pair = allr[len(orig):]
    rng = random.Random(1)
    sample = rng.sample(pair, min(25, len(pair)))
    res = validate(variant, "len64", [(tuple(t), g, "pair") for t, g in sample], nmsg=12)
    nvalid = sum(r[3] for r in res)
    lines.append(f"== {variant}: {len(pair)} pair rules beyond gen; sample of {len(sample)} validated at w=8: {nvalid} VALID")
    for trig, tgt, kind, ok, nchk, zero, mean, pt, ct in res:
        lines.append(f"   {'VALID' if ok else 'INVALID'} {list(trig)} -> {tgt} checks={nchk} P(0 sol)={zero:.3f}"
                     f" mean={mean:.3f}")
txt = "\n".join(lines)
print(txt)
open(HERE + "\\validate_pair.log", "w").write(txt + "\n")
