# ledger_chk.py - check2-4: independent pricing of the scout2-4 r38 rows.  The ledger is my own transcription of the
# formulas of cert.py as printed in pkgR38a proof.md Appendix B.1 (not levers_r38.py or price38.py); the A0 set sizes
# |R_j| are parsed from proof.md Appendix A.2.  The base must reproduce T_log2 = 72.633442 (proof.md Section 7).
# Variants: q3_model x g (N_G recomputed from the same success target), and the per-first-test-pass cost c_17b
# multiplied by a factor (the scout's "deep ops x2" GUESS).
# usage: python3 ledger_chk.py g1 g2 ...

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

import math, re, sys
from fractions import Fraction as F
PROOF = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base/proof.md')
txt = open(PROOF, encoding="utf-8").read()
blk = txt.split("### A.2 The A0 set")[1].split("```text")[1].split("```")[0]
trip = re.findall(r"(\d+)\s+([0-9a-f]{8})\s+(\d+)", blk)
R = [int(t[2]) for t in sorted(trip, key=lambda t: int(t[0]))]
assert len(R) == 256 and [int(t[0]) for t in sorted(trip, key=lambda t: int(t[0]))] == list(range(1, 257))
C = 2728
def LOG(x): return math.log2(x.numerator) - math.log2(x.denominator)
def ledger(q3_log2=-102.0, deep_mult=1, A_C=F(2) ** 70, A_S=F(2) ** 70, DEV=F(2) ** 64, w7_extra=0):
    m = len(R); SR = sum(R)
    p2 = F(287309824, 2 ** 32); p16 = F(32, 2 ** 32)
    q3 = F(math.floor(2.0 ** q3_log2 * 2 ** 140), 2 ** 140)
    S = SR * p2 * q3; qlb = S * (1 - F(1) / 2)
    cexp = F(math.ceil(-math.log(1 - 0.396) * 10 ** 6), 10 ** 6)
    NG = -(-cexp // qlb)
    BMAX = 14 * 32 * 768; muE = SR * p16; muW = muE * p2; mu1 = muW * F(1, 2 ** 10); rng = m * BMAX
    def cap(mu, t): return -(-(NG * mu * (1 + t)) // 1), float(2 * (t * mu) ** 2 * NG / rng ** 2)
    NE_MAX, eE = cap(muE, F(1, 64)); NW_MAX, eW = cap(muW, F(1, 32)); N1_MAX, e1 = cap(mu1, F(3))
    c_ent, c_17, c_17b = 10, 66 + w7_extra, (26 + 3132) * deep_mult
    over = rng * (c_ent + c_17 + c_17b)
    online = NG * (64 + m * 30 + 15) + NE_MAX * c_ent + NW_MAX * c_17 + N1_MAX * c_17b + over
    pre = (2 ** 32 * 64 + 2 ** 32 * 24 + 2 ** 32 * 64 + 768 * 64 + 32 * 128 + m * 768 * (2 ** 29 * 67 + 42 + 8) + SR * 25
           + 2 ** 32 * SR * (211 + 275) + m * 2 ** 64 * (4 + 10) + m * 2 ** 32 * 2 * 10)
    T = A_C + A_S + DEV + F(pre + 1024 + online + 1024, C) + NG + 6
    succ = 1 - math.exp(-float(NG * qlb)) - math.exp(-eE) - math.exp(-eW) - math.exp(-e1)
    return dict(T=LOG(T), NG=NG, online=online, pre=pre, succ=succ, e1=e1, SR=SR,
                allow=LOG(A_C + A_S + DEV), attack=LOG(T - A_C - A_S - DEV))
b = ledger()
print("base: T_log2 %.6f (proof.md 72.633442)  NG %d (proof.md 398563284869814990705)  online %d (proof.md 11938977653196641712347327)"
      % (b["T"], b["NG"], b["online"]))
print("      pre %d (proof.md 466412701031896270852028)  success %.7f  SR_log2 %.5f  allowances_log2 %.5f  attack %.5f"
      % (b["pre"], b["succ"], math.log2(b["SR"]), b["allow"], b["attack"]))
for g in [float(x) for x in sys.argv[1:]]:
    for dm, lab in ((1, "deep x1"), (2, "deep x2 (scout GUESS)")):
        r = ledger(q3_log2=-102.0 + math.log2(g), deep_mult=dm)
        print("g %8.4f %-22s T_log2 %.5f  delta %+.4f  success %.7f  N1 Hoeffding exponent %.0f  attack-only %.5f"
              % (g, lab, r["T"], r["T"] - b["T"], r["succ"], r["e1"], r["attack"]))
    r = ledger(q3_log2=-102.0 + math.log2(g), w7_extra=10)
    print("g %8.4f %-22s T_log2 %.5f  delta %+.4f" % (g, "W7 pass +10 ops", r["T"], r["T"] - b["T"]))
