
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
o=json.load(open('work/scan_m89.out.json'))
ev="research/dig/incoming/blake3-r2-U10/work/scan_m89.py; research/dig/incoming/blake3-r2-U10/work/scan_m89.out.json; research/dig/incoming/blake3-r2-U10/work/b3lib.py; research/dig/incoming/blake3-r2-U10/work/validate_b3.py"
for w,i in (('m8',8),('m9',9)):
    ww='w%d'%i
    q1=o['Q1']; b=q1['max_bit_bias_'+ww]
    num={
    'Q1':f"Difference: 0 bits (A and B equal in {ww}; 0 of 20000 sampled blocks differ). Free word, no difference condition. Pinned conditions: {ww} is one of the pair (w8,w9) fixed by the 64 bits X0,X15 of column G(0,5,10,15) (X15 = pinned constant); constants X3/X7/X11/X15 held in 2000/2000 builds. Max bit bias over 20000 blocks {b:.4f} (uniform).",
    'Q2':f"Relaxing the pin on {ww}: diff in {ww} in B only, {o['Q2'][ww]['trials_diff_in_B_only']} trials: lemma-H digest words 0,2,5,7 kept 0, round-1 state X equal 0, mean digest words differing {o['Q2'][ww]['mean_digest_words_differing']}/8. Changing {ww} in both blocks keeps X3/X7/X11/X15 admissible 0/3000. The word is necessary: any change loses all of the outcome mass at 2^-128 scale of the sample.",
    'Q3':"Degrees of freedom: 0 left in the pair (w8,w9) given the half-state and pinned X0,X15: map (w8,w9)->(X0,X15) is a bijection (inverse recovered 20000/20000). Whole block: 8 free 32-bit parameters (256 bits) = 12 free words 384 bits minus 128 bits of X3/X7/X11/X15. Sweeps over each of the 8 parameters, 65536 values: pair distinct 65536 each; "+"; ".join(f"{k}:{v['distinct_'+ww]}" for k,v in o['Q3_param_sweeps'].items())+f" distinct {ww}; 100000 random builds give 100000 distinct (w8,w9).",
    'Q4':f"Alternative: B-side w8+dl with w9 re-solved to keep X0: X0 kept 3000/3000 but X15 kept 0/3000 (bijection), X5 and X10 kept 0, lemma-H kept 0, digest words differing mean {o['Q4_compensated_w8w9_alt']['mean_words_differ']}/8. No carry alternative for {ww}: A and B must share it exactly; the 75/32 carry effect lives in w4,w5 only."}
    qtext={'Q1':'difference/condition count at this word','Q2':'necessity of each condition group (relax, recount outcome mass)','Q3':'degrees of freedom (exact over carries)','Q4':'alternative outcomes / carry patterns and whether they reach the same later differences'}
    st={'Q1':'COMPUTED','Q2':'SAMPLED','Q3':'COMPUTED','Q4':'SAMPLED'}
    for q in ('Q1','Q2','Q3','Q4'):
        cid=f"blake3-r2|{w}|msgword|{q}"
        r=dict(hash='blake3-r2',row_i=None,row_j=None,object=f"message word {w} ({ww}): free, pairs with {'m9' if i==8 else 'm8'} under X0/X15 pin",
          question=f"{q} {qtext[q]}",labels=['N'] if q!='Q3' else ['N','I'],status=st[q],number=num[q],source="our workflow: scan-once",own_test=True,
          evidence=ev,date="2026-10-12",lever=False,gain_bits=None,
          notes=f"Universe cell {cid}. Own b3lib construction (pkgB3U Sec 4) validated 3000/3000 first. Sampled, window of 8-parameter construction, all words recomputed from the parameters; no gain seen.",
          topic=f"blake3-r2 msgword {w}")
        fn=f"{cid.replace('|','_')}.json"
        json.dump(r,open(fn,'w'),indent=1)
        add_cell.validate(json.load(open(fn)),add_cell.load()); print('ok',fn)
