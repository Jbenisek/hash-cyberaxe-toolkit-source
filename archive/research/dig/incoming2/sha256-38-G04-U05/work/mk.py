
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

import json,sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
base=dict(hash="sha256-38",row_i=None,row_j=None,source="our workflow: scan-once-wave2",own_test=True,date="2026-10-12",lever=False,gain_bits=0.0,gain_basis="T",
 object="CV.H1: uniform independent chaining values F_38(IV, M0) (premise H1)",
 evidence="research/dig/incoming2/sha256-38-G04-U05/work/ (h1.cu, build.sh, runall.sh, classes.txt, exact_hist.txt, out_m0_l36_s7.txt, out_m1..6_l32.txt, out_m3_l29_s21/22.txt, out_m0_l32_steps37.txt)",
 topic="CV.H1.uniform")
val=("Validation on known answers: GPU compress gives SHA-256('abc') ba7816bf..f20015ad at 64 steps; 2000 random blocks at 37/38 steps equal an independent host reference (full W[64]) 0 mismatches; "
 "the 90-class pass-count table rebuilt on GPU over all 2^32 values of A_-1 equals the proof's A.2 table in all 40 bins (0 mismatches; sum_k 25,857,884,160 = 90|F7|, sum_k2 636,623,874,688).")
q2=dict(base,labels=["E","Z"],status="SAMPLED",question="Q2 necessity: what does the attack use of H1; replace H1 by the measured law and recompute the counts",
 number=("H1 is used only through the law of x = A_-1 (via the 90 class tests c7_c - x in F7) and, given a pass, the uniformity of the other CV words (Lemma 5.1). Replaced by measurement on 2^36 = 68,719,476,736 real 38-step first blocks (uniform random M0, own GPU code, seed 7): "
 "mean passing classes 6.020483 vs exact-under-H1 6.020508 (z -0.62, 95% interval on relative deviation of the good-pair rate +-1.3e-5 = +-1.9e-5 bit); P(some class passes) 0.303193 vs 0.303194 (z -0.84); mean k^2 148.2248 vs 148.2255; "
 "pass-count histogram chi2 46.4 on 40 bins vs the exact A.2 table; plain x in F7 4,596,988,233 vs 4,596,957,184 (z +0.47); 256 CV bit means (1/4 subsample, 1.7e10 blocks) max |z| 2.94, sum z^2 244.0 (expect 256+-22.6); "
 "224 bits of words 1..7 conditional on >=1 passing class (5.2e9 blocks) max |z| 3.56 (of 224, expected ~3.0); 1024 joint bit counts A_-1 x A-2 and A_-1 x E-1 (4.3e9 blocks each) max |z| 2.75 / 2.80. "
 "No deviation: the exact event with H1 dropped and replaced by the measured law gives the same counts to 2e-5 bit."),
 notes=("universe cell sha256-38|CV.H1|CV|Q2. "+val+" Scope and limits: marginals, 2-bit joint counts of A_-1 with A_-2 and E_-1, and conditional bit means only; the full 256-bit joint law and nonlinear dependence are not testable at this size; "
 "M0 is drawn by splitmix64 (a PRNG, so PRNG weakness would also show here, none seen); the independence across first blocks is by construction of the draw, not measured. Adds 2^36 real blocks to the inherited 2^21/2^23/2^29(r37)/29,360,128(r38). Sampled, interval stated; not a proof."),
 potential_bits=0.0,prior=0.0)
q4=dict(base,labels=["Z"],status="SAMPLED",question="Q4 alternatives: a structured first-block family or step count whose chaining value passes the gate more often than H1",
 number=("None found. Measured 2^32 real 38-step first blocks per family (seed 11): counter in W0 only: mean passing classes 6.020546 (z +0.24), x in F7 z -1.46; counter in W15 only: 6.020418 (z -0.56), z +0.25; W0 = counter with W1..W15 fixed random: 6.020373 (z -0.84), z +0.06; "
 "64-bit counter in W0,W1: 6.020553 (z +0.28), z +0.11; printable-ASCII words: 6.020732 (z +1.39), z -0.28; random weight-4 blocks: 6.019715 (z -4.9) at 2^32 draws but this is duplication (only C(512,4)=2.8e9 blocks exist, drawn with replacement); "
 "redone at 2^29 draws with two seeds: 6.020190 (z -0.70) and 6.020512 (z +0.01), bit-mean sum z^2 288 and 299 (expect 256+-23, inflated by the 9% repeated blocks). 37-step (r37) first blocks, uniform, 2^32: 6.020647 (z +0.86). "
 "Every family reproduces the exact A.2 histogram (chi2 30.8 to 55.8 on 40 bins). Reference: exact value under H1 6.020508 per block."),
 notes=("universe cell sha256-38|CV.H1|CV|Q4. "+val+" Reading of Q4: alternatives to a uniformly random first block (cheaper/biased M0 families) and to the 38-step block; none moves the pass rate beyond 1.5 sigma (relative 4e-5 per 2^32 blocks). "
 "Not tested: families that choose M0 by search (e.g. fixing A_-1 bits by partial inversion), which cost work; the gate x is a pseudorandom function of M0 after 38 steps so no cheap steering was seen. Sampled, interval stated."),
 potential_bits=0.0,prior=0.0)
for nm,r in (("sha256-38_CV.H1_CV_Q2.json",q2),("sha256-38_CV.H1_CV_Q4.json",q4)):
    p=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G04-U05/')+nm
    json.dump(r,open(p,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(p,encoding='utf-8')),add_cell.load()); print("ok",nm)
