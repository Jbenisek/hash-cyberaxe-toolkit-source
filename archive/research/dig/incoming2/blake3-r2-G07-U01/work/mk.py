
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
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
base=dict(hash="blake3-r2",row_i=None,row_j=None,object="H1' dependence clause (ii) / rho <= 3,071",
 source="our workflow: scan-once-wave2",own_test=True,date="2026-10-12",
 evidence="research/dig/incoming2/blake3-r2-G07-U01/work/h1p.py; h1p2.py; research/dossiers/1a92bf64; research/dossiers/fa761365",
 topic="blake3-r2 H1prime dependence clause",lever=False,gain_bits=None)
recs={
"R1":dict(question="R1: value charged or stated for H1'(ii) in the filed lines",labels=["N"],status="COMPUTED",
 number="1a92bf64 (101.9196): rho = E[N(N-1)]/E[N] <= 0.0065, success 1-exp(-0.515*(1-0.0065/2)) = 0.4014985, declared unproved, ruled NOT_EVALUABLE. fa761365 (65.0407): same H1' composite, stated per context, NOT_EVALUABLE (evaluability+experiments lanes). 848bcd76 (113.4454): proved rho <= 3,071 (Lemma S7 cap 3,072 members, Lemma S8 b=1/3072), passed. Stated values, exact.",
 notes="universe cell blake3-r2|PREM.H1P|PREM|R1. Read from proof-numbered.md of 1a92bf64 (lines 2340-2500) and judge-dossier.json of both rulings. Both judges cite: no organizer-executed measurement of the ~2^-91 joint event or cross-member factorial moment; proof itself says 'worst case 3071, partial events cluster (variance 572x mean for rule A)'. 848bcd76 dossier not in research/dossiers; its numbers come from MASTER_PLAN 2026-10-09 and EDGES_FIBRE item 4 (reread, then reproduced in R2)."),
"R2":dict(question="R2: own recount of the 1a92bf64 time formula and of the rho<=3071 re-price",labels=["N"],status="COMPUTED",
 number="Formula log2(O(f)/430+2^38), O=S+2^46+FRAMES*2,443,836,395,520, f=(5/7)*138,646,913,024, m=0.515 reproduces 101.91954 (claimed 101.9196), independent of S from 0 to 2^70. Re-price at rho=3071 with b=1/3072 and success 0.39 (-ln(0.61)*3072 frames-mean 1518.5): 113.44531 -> ceil 113.4454 = filed 848bcd76 (exact match); at success 0.40: 113.49276; keeping the proof's 0.51332625: 113.49981. Cost of the proved bound over the 0.0065 premise at equal success 0.40: +11.573 bits.",
 notes="universe cell blake3-r2|PREM.H1P|PREM|R2. Exact rational arithmetic (fractions) for FRAMES, float log2. Rule written before run: reproduce 101.9196 first, then re-price. Recount only, the premise itself (rho at the 2^-91 event) is NOT measured; nothing here tests whether 0.0065 is true."),
"R3":dict(question="R3: control of Lemma S8 b(rho) (the function that turns rho into success)",labels=["N"],status="COMPUTED",
 number="LP over laws of N on {0..3072} with fixed mean and fixed factorial ratio rho: minimum Pr(N>0)/mu equals b(rho) at rho in {0, 0.0065, 0.5, 1, 1.5, 2, 7.3, 100, 3070.5, 3071}; max abs difference 4.4e-16. Negative control: linear formula 1-rho/2 at rho=3071 gives -1534.5 (wrong), LP gives 3.2552e-4 = 1/3072. rho=3071.5 infeasible under the 3072 cap (LP returns none).",
 notes="universe cell blake3-r2|PREM.H1P|PREM|R3. scipy highs LP, scripts work/h1p2.py. Control confirms S8 is tight and that 3071 is the true ceiling of rho under the Lemma S7 cap. It does not verify Lemma S7 itself (3,072 members), which is a counting proof read, not rerun here."),
"R4":dict(question="R4: score sensitivity of H1'(ii) in bits per unit rho and slack candidates",labels=["N"],status="COMPUTED",
 number="Cost in bits = log2(1/b(rho)) (time is frames-dominated): 0.0047 bit at rho=0.0065; slope 0.724 bit per unit rho at 0.0065, 0.96 at 0.5; +1 bit at rho=1.003 over the 0.0065 premise; 1.000 bit at rho=1, 11.585 bits at rho=3071 (log2 3072 - 0.0000). Whole gap between premise and proved bound 11.573 bits at success 0.40. Intermediate rho values (a proved bound between 0.0065 and 3071) interpolate through this curve: every halving of the proved bound from 3071 saves about 1 bit while rho >> 1.",
 notes="universe cell blake3-r2|PREM.H1P|PREM|R4. Slack candidates: a proved bound on rho below 3071 (any structure in the 3,072-member set, e.g. the 2,048/3,072 split by bit 2 of Y9, Lemma S7, or conditioning on the t=0/rule A rows) buys ~1 bit per halving above rho~2; the proof's 0.515*0.99675 vs exact -ln(0.6) costs 0.007 bit; success 0.39 vs 0.40 is 0.047 bit (used by 848bcd76).",
 lever=True,gain_bits=None)}
for k,v in recs.items():
    r=dict(base); r.update(v)
    if k=="R4": r['gain_bits']=None
    p=f"blake3-r2_PREM.H1P_PREM_{k}.json"; json.dump(r,open(p,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(p,encoding='utf-8')),add_cell.load()); print(p,"ok")
