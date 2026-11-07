
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
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G07-U03')
EV="research/tools/build_pkg/scratch/pkgB3S/pkg/blake3-r2/experiments/frontline.py; research/dig/incoming2/blake3-r2-G07-U03/work/led.py; research/tighten/B3M_blake3_memrule.md; research/tighten/b3m_F_result.md"
def rec(cell,obj,q,num,notes,labels,lever=False,gain=None,basis=None):
    d=dict(hash="blake3-r2",row_i=None,row_j=None,object=obj,question=q,labels=labels,status="COMPUTED",number=num,source="our workflow: scan-once-wave2",own_test=True,evidence=EV,date="2026-10-12",lever=lever,notes="universe cell "+cell+". "+notes,topic="blake3-r2 "+cell.split('|')[1]+" "+cell.split('|')[3])
    if gain is not None: d["gain_bits"]=gain; d["gain_basis"]=basis
    r=cell.split('|')
    fn=cell.replace('|','_')+'.json'
    json.dump(d,open(os.path.join(D,fn),'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(os.path.join(D,fn),encoding='utf-8')),add_cell.load()); print('ok',fn)
H5="blake3-r2 H5_exec/H5_screen: U = U0 - 410"
HG="blake3-r2 H_G_cluster: fills F of shipped walk"
rec("blake3-r2|PREM.H5E|PREM|R1",H5,"R1 value charged in the shipped program","u_U = 335,060,079,487,497/2^48 = 1.1903725 (exact); credit m_C = ceil(1.01*RUN_STEPS*u_U)",
 "Read of frontline.py (scratch package pkgB3S, line U_U and _MC): the shipped program charges the ledger U (not U0) at factor 1.01, with no 7506/7711=0.9734 worst-case ratio. u_U/u_U0 = 0.92134 exact. Filing status of pkgB3S not checked here. Premise itself (mean of U <= 1.01 u_U for the sampler) remains a premise.",["E"])
rec("blake3-r2|PREM.H5E|PREM|R2",H5,"R2 exact recount of U = U0 - 410 credit","u_U = u_U0 - 410*p_call exact in rationals: (727,329,595,507,749/2^49) - 410*(279,070,422,111/2^50) = 335,060,079,487,497/2^48 = 1.19037253; u_U0 = 1.29199690",
 "Fraction arithmetic in work/led.py; equality True. Recounts the algebra only; the mean of U on the sampler was not re-measured (package preregistered sample 1.180 vs 1.190 cited from B3M, not rerun). Metered run of the shipped program not done.",["N"])
rec("blake3-r2|PREM.H5E|PREM|R3",H5,"R3 control: same ledger tool on the old charge","shipped N reproduces claim.json time_log2 62.434710 (claim 62.43471); control charging old U0 unconverted at 1.01 gives 62.469639 (+0.0349); old 7506/7711*U0 gives 62.457928 (+0.0232)",
 "work/led.py execs the shipped frontline.py with U_U replaced; the tool discriminates old vs new charge and reproduces the shipped claim. Note the +0.0232 for the old-ratio form is the B3M item-2 effect on the current stack (B3M quoted 0.0200 on the older stack).",["Z"])
rec("blake3-r2|PREM.H5E|PREM|R4",H5,"R4 score sensitivity of the credit factor and u_U","+1% in u_U = +0.004135 bit; credit factor 1.010 -> 1.006 = -0.00164 bit, -> 1.003 = -0.00287 bit, -> 1.020 = +0.00410 bit",
 "Exact N re-evaluated from the shipped program (work/led.py). Slack candidate: a smaller factor than 1.01 is worth at most 0.003 bit and needs the premise sample to support it (B3M cites a measured one-sided bound 1.0006 u_U, not rerun here). Small.",["N"],lever=True,gain=0.00287,basis="T")
rec("blake3-r2|PREM.HG|PREM|R3",HG,"R3 control for the F premise","ledger tool: shipped N = 2,680,333,835,014,828,941,956, time_log2 62.434710 reproduces claim; same tool at G_BUDGET 12,466 gives 62.617433 (old claim 62.6175)",
 "Own ledger control done now. The counter-side controls (hgf vs fref identical in 2048 of 2048 contexts, F>G in 0, G' mean 12,426 vs package 12,427, walk() vs mirror 13 of 13) are read from b3m_F_result.md / main.log / walk_check.log, not rerun (scan once). Mean F 7159.266 on 2^24 contexts is from that earlier own run.",["Z"])
rec("blake3-r2|PREM.HG|PREM|R4",HG,"R4 score sensitivity of the F value","d time_log2 / dF = 3.674e-5 bit per unit F (0.00367 per 100). F=7100: -0.002353; 7000: -0.006038; 7198 (Hoeffding form): +0.001249; 8000: +0.030393; 12466: +0.182723 vs 7164",
 "Exact N from the shipped program with G_BUDGET replaced. At the measured mean 7159.27 the mean-only value saves 0.00018 bit; the 6-SE margin of 7164 costs 0.00018 bit, so no slack left in F. Floor is the 84261*S range term.",["N"],lever=False)
