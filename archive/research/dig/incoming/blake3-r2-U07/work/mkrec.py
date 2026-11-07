
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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
D=os.path.dirname(os.path.abspath(__file__))+'/..'
EV="research/dig/incoming/blake3-r2-U07/work/b3ctr.py; research/dig/incoming/blake3-r2-U07/work/validate.py; research/dig/incoming/blake3-r2-U07/work/exp.py; research/dig/incoming/blake3-r2-U07/work/exp_out.json; research/dig/incoming/blake3-r2-U07/work/img.c; research/dig/incoming/blake3-r2-U07/work/img_out.txt; research/dig/incoming/blake3-r2-U07/work/surj.py; research/dig/incoming/blake3-r2-U07/work/surj_out.txt"
img=open(D+'/work/img_out.txt').read().strip().replace('\n',' | ')
VAL="validated first: counter-construction (pkgB3U Sec 8 steps CO+CT) transcribed in b3ctr.py; 2000/2000 random free-word sets give pinned X3,X7,X11,X15, equal round-0 state for A/B, and equal digest words 0,2,5,7 (known answer reproduced)."
def rec(w,q,obj,question,labels,status,number,notes,own=True):
    cid="blake3-r2|m%d|msgword|%s"%(w,q)
    r=dict(hash="blake3-r2",row_i=None,row_j=None,object=obj,question=question,labels=labels,status=status,number=number,
      source="our workflow: scan-once",own_test=own,evidence=EV,date="2026-10-12",lever=False,gain_bits=None,
      notes="universe cell %s. %s %s"%(cid,VAL,notes))
    fn=D+"/"+cid.replace('|','_')+".json"
    json.dump(r,open(fn,'w'),indent=1)
    add_cell.validate(json.load(open(fn)),add_cell.load())
    print("ok",fn)
for w in (2,3):
    o=2 if w==2 else 3
    rd={2:"K1 (first word) and C0 (first word)",3:"K1 (second word) and C1 (first word)"}[w]
    dep="depends on 7 of the 10 free words (D2.a1,D2.b1,S11,S4,X9,w6,t_hi: every single-bit flip changes it, 1.0 of 40x32 or 40x16 trials) and on none of C0.d1, y, c1 (0.0)"
    rec(w,"Q1","message word m%d (counter construction pkgB3U Sec 8)"%w,
      "Difference/condition count on m%d as used: bits differing between A and B, bits pinned, calls that read it"%w,
      ["N"],"COMPUTED",
      "m%d: 0 differing bits between A and B (only w4,w5 differ, 3000/3000 samples; proved by Lemma CT(c)); 0 pinned bits (not among the constants w4,w13,w14,w15,X3,X7,X11,X15); a derived line of step CO (free-by-construction), read by %s; %s"%(w,rd,dep),
      "m%d is neither pinned (w4) nor cancelling (w5+w4-w4') nor a forced constant; it is a line of step CO, so it carries no condition of its own. Full A/B state is equal after K2 through C2 (500/500; K0,K1 differ only in v14 = block length), first difference at C3, which does not read m%d."%(w,w))
    rec(w,"Q2","message word m%d, necessity of its condition groups"%w,
      "Necessity of each condition group at m%d: relax and recount"%w,
      ["N","K"],"COMPUTED",
      "m%d has no condition group of its own (0 groups). Relaxation test the other way round: flipping any single bit of m%d in both messages (no re-solve), 9600 trials (300 samples x 32 bits): pins X3,X7,X11,X15 kept 0/9600, half-collision (digest words 0,2,5,7 equal) kept 0/9600"%(w,w),
      "So m%d is not free to perturb: it is fixed through the pinned round-0 outputs; its only role is as a function of the construction words. Structurally trivial for conditions; the perturbation count is a sample over 300 free-word sets."%w)
    rec(w,"Q3","message word m%d, degrees of freedom"%w,
      "Degrees of freedom of m%d: exact count over carries"%w,
      ["I"],"LOCAL_ONLY",
      "(m2,m3) is onto all 2^64 pairs for every t_hi: constructive inverse (K1 backwards, then S13 via X13/S7/S11, S9 via X9) hit 20000/20000 random (w2,w3,t_hi) targets exactly (surj_out.txt); each step is an add, XOR or rotate so there is no carry ambiguity: (w2,w3) <-> (K1.c1,S13) is a bijection at fixed t_hi. Not free one parameter at a time: S13 over all 2^32 values of D2.a1 alone (others fixed) reaches only 79,460,208 values (1.85%%)",
      "m%d alone: 32 bits, all reached. Of the 280 free bits (7x32 outer, y 19, t_hi 16, c1 21) 64 go to (m2,m3) and 216 stay free; m2,m3 depend on 7 of the 10 free words. LOCAL_ONLY: surjectivity shown by sampled exact solves plus the step-by-step bijection, with the constants of the counter construction; the E1/E3 class conditions on y and c1 are untouched (m2,m3 do not depend on them). The one-parameter image was run for 1 fixing only (stopped after S13; S9 trials skipped, S9 is a visible bijection in X9)."%w)
    rec(w,"Q4","message word m%d, alternative outcomes / carry patterns"%w,
      "Alternative outcomes/carry patterns at m%d and whether they reach the same later differences"%w,
      ["Z"],"COMPUTED",
      "Required XOR difference on m%d is 0, which has exactly 1 additive pattern (0); any nonzero single-bit difference has 2 patterns, d=0x3 has 4, d=0x15 has 8 (exhaustive 16-bit). Alternative: put a difference on m%d (xor/+/-, 32 bits each, 96 deltas, 60 samples each): 0/96 reach a zero round-0 state difference; all 16 state words differ every time (K1 outputs feed all four diagonal calls). The length difference cancels only in K2 (w4,w5)."%(w,w),
      "No alternative carry pattern exists for m%d, and no alternative placement of the message difference on it reaches the same later differences (Z: tested, no gain)."%w)
