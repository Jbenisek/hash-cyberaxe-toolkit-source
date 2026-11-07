
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
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G04-U05')
ev="research/dig/incoming2/sha256-37-G04-U05/work/absorb.c, absorb.out, absorb2.c, absorb2.out, nz_b.out, nz_an.py, nz_b_an.txt, tl/ (copy of research/tools/traillab with an output-difference recorder in src/smc.c)"
base=dict(hash="sha256-37",row_i=None,row_j=None,object="CV.diff: characteristics with a nonzero chaining-value difference (first block leaves a near-collision, second block absorbs it)",
 source="our workflow: scan-once-wave2",own_test=True,evidence=ev,date="2026-10-12",lever=False,gain_bits=None,topic="CV.diff.nonzero")
cells={
"Q1":dict(labels=["N","E"],status="COMPUTED",
 question="Q1: count/size of the nonzero-dCV object as the attack could use it",
 number="Attack uses 1 dCV value (0) of 2^256. Rows 0..3 can absorb (by choosing dW0..dW3) exactly the dCV with the four A words (a,b,c,d = A-1..A-4) equal and the four E words (e,f,g,h) arbitrary: 2^128 values (exact algebra, triangular; numeric: 300,000/300,000 absorbed for E-only deltas, 0/4,800,000 when any A word differs). With the published W16..W19 cells (dW16..19=0 forces dW3=dW2=dW1=dW0=0, triangular) the set is 1 value, delta=0 (0 of 5,100,000 random nonzero deltas leave rows 0..3 identical with dW=0).",
 notes="universe cell sha256-37|CV.diff|CV|Q1. Own C (absorb.c: real step function rows 0..3, two members, CV_y=CV_x+delta, W_i^y solved to equalise E_i). Validation: delta=0 gives 20000/20000 both tests; published pair reproduces its digest (absorb2.c, traillab check). Algebra: E rows 0..3 are bijective in W_i; A_i = E_i - A_{i-4} + S0 + MAJ forces dA_3=dA_-1=0, then dA_2=dA_-2=0, dA_1=dA_-3=0, dA_0=dA_-4=0. Window = rows 0..3 under the printed rows >=4 and printed W cells; not a statement about a different characteristic."),
"Q2":dict(labels=["N","E"],status="COMPUTED",
 question="Q2: necessity of dCV = 0 for the published characteristic (drop it / replace it, exact event)",
 number="dCV=0 is necessary for the published characteristic: digest difference = dCV + (A33..A36,E33..E36 difference) and the printed tail rows 25..36 are '='. Tested on real 37-step compressions: published pair + absorbed E-word delta (rows 0..3 identical, W4..W15 published), 1,000,000 trials: digest collisions 0, mean digest XOR popcount 128.0, min 89 (unstructured); control delta=0 reproduces the printed digest. Nonzero dCV needs a tail with nonzero E-diff at rows 33..36 AND zero A-diff there, which needs nonzero A diffs in rows 29..32 (dE_i = dA_{i-4} + A-terms): a different characteristic, not derived.",
 notes="universe cell sha256-37|CV.diff|CV|Q2. absorb2.c links traillab tl_load/tl_compress_ref. Replacing dCV=0 by an absorbed nonzero delta breaks the message schedule (dW0..3 != 0 enter W16..W19), which is why the digests avalanche."),
"Q3":dict(labels=["N","E"],status="LOCAL_ONLY",
 question="Q3: log2 freedom left in the near-collision difference (what dCV a first block would have to produce)",
 number="Pairs following the printed cells of rows 4..23 (traillab SMC, np 24576, 49,131 samples, seed 7002): 6.42% have zero digest difference (3,153; EXACT/cells 1.041 +- 0.007, validates the known 2^-4 tail), the other 93.58% (45,978) have all 8 digest words nonzero, 45,978 distinct 256-bit differences, 0 collisions (support > 2^29.98 by birthday), popcount min 96 median 128 mean 128.0. Shape 'A words zero, E words nonzero' (the only absorbable shape): 0 of 49,131. First pass on 1,981 samples gave the same picture.",
 notes="universe cell sha256-37|CV.diff|CV|Q3. LOCAL_ONLY: window rows 24..36 after the prefix 4..23, late words redrawn per sample (traillab window --rows 24 36). Tail failures are spread over the full 256 bits: no sparse near-collision difference is available from this characteristic. Sampling gives a bound on support, not an exact size. Run 331 s, 4 threads."),
"Q4":dict(labels=["N","E"],status="LOCAL_ONLY",
 question="Q4: alternatives to dCV=0 (other absorbing routes, other signings of the near-collision)",
 number="Within the published characteristic no alternative exists: (i) E-word deltas (2^128) are absorbed by dW0..dW3 but then need dW16..dW19 != 0 (breaks the '=' W cells of rows 16..19) and a tail E-difference -delta that the characteristic does not have (digest collisions 0 of 1,000,000, min popcount 89); (ii) tail-failure near-collisions are full-width (popcount ~128, 0 of 49,131 A-zero shapes), so a first block would need a 256-bit target. Any real alternative needs a new characteristic with nonzero rows 29..36 AND a new dense part; not attempted.",
 notes="universe cell sha256-37|CV.diff|CV|Q4. Not a closure of the idea in general (a re-derived characteristic with dCV != 0 is untested); closed only for the published rows 4..36 shape. Cost side not measured: the first-block pair with a prescribed dCV would be a second 37-step differential."),
}
for q,c in cells.items():
    r=dict(base); r.update(c); r["object"]=base["object"]
    fn=os.path.join(D,"sha256-37_CV.diff_CV_%s.json"%q)
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    print(q,add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()))
