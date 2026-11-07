
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

import json,sys,os
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G04-U06')
ev="research/dig/incoming2/sha256-38-G04-U06/work/absorb.c, absorb.out, absorb2.c, absorb2.out, nz_b.out, nz_an.py, nz_b_an.txt, check.out, tl/ (copy of research/tools/traillab, chi38) with an output-difference recorder in src/smc.c"
base=dict(hash="sha256-38",row_i=None,row_j=None,object="CV.diff: characteristics with a nonzero chaining-value difference (first block leaves a near-collision, second block absorbs it)",
 source="our workflow: scan-once-wave2",own_test=True,evidence=ev,date="2026-10-12",lever=False,gain_bits=None,topic="CV.diff.nonzero")
cells={
"Q1":dict(labels=["N","E"],status="COMPUTED",
 question="Q1: count/size of the nonzero-dCV object as the attack could use it",
 number="Attack uses 1 dCV value (0) of 2^256. Rows 0..3 can absorb (by choosing dW0..dW3) exactly the dCV with the four A words (a,b,c,d = A-1..A-4) equal and the four E words (e,f,g,h) arbitrary: 2^128 values (exact algebra, triangular; numeric: 300,000/300,000 absorbed for E-only deltas, 0/4,800,000 when any A word differs). With the published W16..W19 cells (the published W16..W19 differences are unchanged only if dW0..dW3 = 0: W16..W19 contain W0+s0(W1), W1+s0(W2), W2+s0(W3)+s1(W16), W3+s0(W4)+s1(W17) and dW4=0, so triangular; and with dW=0, rows 0..3 identical forces dE_-1=0, then dE_-2, dE_-3, dE_-4 = 0) the set is 1 value, delta=0 (exact; 0 of 5,100,000 random nonzero deltas leave rows 0..3 identical with dW=0).",
 notes="universe cell sha256-38|CV.diff|CV|Q1. Own C (absorb.c: real step function rows 0..3, two members, CV_y=CV_x+delta, W_i^y solved to equalise E_i). Validation: delta=0 gives 20000/20000 both tests; published pair reproduces its digest (absorb2.c, traillab check). Algebra: E rows 0..3 are bijective in W_i; A_i = E_i - A_{i-4} + S0 + MAJ forces dA_3=dA_-1=0, then dA_2=dA_-2=0, dA_1=dA_-3=0, dA_0=dA_-4=0. Window = rows 0..3 under the printed rows >=4 and printed W cells; not a statement about a different characteristic."),
"Q2":dict(labels=["N","E"],status="COMPUTED",
 question="Q2: necessity of dCV = 0 for the published characteristic (drop it / replace it, exact event)",
 number="dCV=0 is necessary for the published characteristic: digest difference = dCV + (A34..A37,E34..E37 difference) and the printed tail rows 26..37 are '='. Tested on real 38-step compressions: published pair + absorbed E-word delta (rows 0..3 identical, W4..W15 published), 1,000,000 trials: digest collisions 0, mean digest XOR popcount 128.0, min 89 (unstructured); control delta=0 reproduces the printed digest. Nonzero dCV needs a tail with nonzero E-diff at rows 34..37 AND zero A-diff there, which needs nonzero A diffs in rows 30..33 (dE_i = dA_{i-4} + A-terms): a different characteristic, not derived.",
 notes="universe cell sha256-38|CV.diff|CV|Q2. absorb2.c links traillab tl_load/tl_compress_ref. Replacing dCV=0 by an absorbed nonzero delta breaks the message schedule (dW0..3 != 0 enter W16..W19), which is why the digests avalanche."),
"Q3":dict(labels=["N","E"],status="LOCAL_ONLY",
 question="Q3: log2 freedom left in the near-collision difference (what dCV a first block would have to produce)",
 number="Pairs following the printed cells of rows 6..23 (traillab SMC on chi38, np 24576, 24,559 samples, seed 7002): 6.79% have zero digest difference (1,667; EXACT/cells 1.100 +- 0.017, cells rate 2^-4.018 [2^-4.09,2^-3.95], 151 zero-difference pairs lie outside the tail cells), the other 93.21% (22,892) have all 8 digest words nonzero, 22,892 distinct 256-bit differences, 0 collisions (support > 2^27.97 by birthday), popcount min 97 median 128 mean 128.1. Shape 'A words zero, E words nonzero' (the only absorbable shape): 0 of 24,559.",
 notes="universe cell sha256-38|CV.diff|CV|Q3. LOCAL_ONLY: window rows 24..37 after the prefix 6..23 (rows 5..25 carry the printed cells in chi38), late words redrawn per sample (traillab window --rows 24 37). Tail failures are spread over the full 256 bits: no sparse near-collision difference is available from this characteristic. Sampling gives a bound on support, not an exact size. Run 70 s, 4 threads; validated: traillab check on chi38 (published pair reproduces its digest, 0 failing rows 0..37), delta=0 controls."),
"Q4":dict(labels=["N","E"],status="LOCAL_ONLY",
 question="Q4: alternatives to dCV=0 (other absorbing routes, other signings of the near-collision)",
 number="Within the published characteristic no alternative exists: (i) E-word deltas (2^128) are absorbed by dW0..dW3 but then need dW16..dW19 != 0 (changes W16..W19 away from the published differences, so the printed state rows 16..19 no longer hold) and a tail E-difference -delta that the characteristic does not have (digest collisions 0 of 1,000,000, min popcount 89, 38-step run); (ii) tail-failure near-collisions are full-width (popcount ~128, 0 of 24,559 A-zero shapes), so a first block would need a 256-bit target. Any real alternative needs a new characteristic with nonzero rows 30..37 AND a new dense part; not attempted.",
 notes="universe cell sha256-38|CV.diff|CV|Q4. Not a closure of the idea in general (a re-derived characteristic with dCV != 0 is untested); closed only for the published rows 5..37 shape. Cost side not measured: the first-block pair with a prescribed dCV would be a second 38-step differential."),
}
for q,c in cells.items():
    r=dict(base); r.update(c); r["object"]=base["object"]
    fn=os.path.join(D,"sha256-38_CV.diff_CV_%s.json"%q)
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    print(q,add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()))
