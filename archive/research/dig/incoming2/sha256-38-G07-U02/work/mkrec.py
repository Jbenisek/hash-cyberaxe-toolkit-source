
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

import json, os, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G07-U02')
EV="research/dig/incoming2/sha256-38-G07-U02/work/g07u02.py; research/dig/incoming2/sha256-38-G07-U02/work/g07u02.out; research/dig/incoming2/sha256-38-G07-U02/work/g07u02b.py; research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/experiments/a0lean38.py; research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/proof.md"
KA=" Known answer first: a0lean38.py ledger() reproduces time_log2 87.9037360 (filed 87.90374) and memory() reproduces 1,045,792 B (filed values)."
def rec(cid,obj,q,status,number,notes,hp,lab=[]):
    h,loc,o,qq=cid.split('|')
    return dict(id=cid,hash=h,row_i=None,row_j=None,object=obj,question=q,labels=lab,status=status,number=number,source="our workflow: scan-once-wave2",own_test=True,evidence=EV,date="2026-10-12",lever=False,gain_bits=None,notes="universe cell %s. %s%s"%(cid,hp,notes))
R=[]
R.append(rec("sha256-38|PREM.H4A|PREM|R1","H4a characteristic-search allowance A_C, shipped line pkgR38M3 (R38M3, 87.90374)","R1: value charged or stated?","COMPUTED",
 "A_C = 2^78 compressions (x C=2728 ops = 824,487,408,977,177,097,149,612,032 ledger ops), exact; = 1.044e-3 of the total N (log2 N/C 87.9037360). Contributes 0.001507 bit (A_C=0 gives 87.9022291).",
 " In R38M3 the premise is named H4 (advice allowances: A_S 2^74, A_C 2^78, DEV 2^64); the label H4a belongs to the judge cause on R38E/R38N (dense characteristic derivation not measured). Proof text: A_C = 2^37 x 593,858 CPU-s of the predecessor's search, 'about 3 x 10^9 CPU-years'.",
 "Statement of the charged value only. The dense characteristic itself is not derived by us (4 solvers x 2 h UNKNOWN: UNKNOWN is not UNSAT); the allowance is advice priced by scaling, not a measurement of the search."))
R.append(rec("sha256-38|PREM.H4A|PREM|R2","H4a allowance A_C, recount of the conversion","R2: own re-measurement or metered recount?","COMPUTED",
 "Ledger rerun exact (see R1). Conversion recount (arithmetic): 2^37 x 593,858 s = 2^56.180 s = 2.59e9 CPU-years (proof says 'about 3e9'; 3e9 yr = 2^56.394 s, +0.21 bit); 2^78 compressions / 2^56.180 s implies a price of 3.70e6 compressions per CPU-second (3.19e6 if 3e9 yr is used). The price itself (calibrated in filing 6eeefb64) was not re-derived here. No re-measurement of the search is possible: dense characteristic not derived.",
 " Metered recount of the arithmetic only, no solver run.",
 "A 0.21-bit rounding in the years figure is worth <= 0.0003 bit of score (slope 0.0015 bit per doubling of A_C). What is NOT answered: the search cost is neither re-measured nor bounded by us; the judge cause (dense characteristic unmeasured) is unchanged by this cell."))
R.append(rec("sha256-38|PREM.H4A|PREM|R3","H4a allowance A_C, control of the ledger tool","R3: control (known answer or negative control)?","COMPUTED",
 "Known answer reproduced: 87.9037360 at A_C=2^78. Control arm A_C=2^84 gives 87.99563, equal to the figure stated in the proof (Section 12 H4). Negative control: A_C=2^100 gives 100.00033, i.e. the tool does respond (a wrong allowance cannot hide); A_C=0 gives 87.90223.",
 " Control is of the ledger arithmetic (a0lean38.py ledger with the full calibration, 11 s), not of the characteristic search.",
 "Control passes for the score arithmetic; there is no control for the search cost (no known-answer derivation of a dense characteristic exists here)."))
R.append(rec("sha256-38|PREM.H4A|PREM|R4","H4a allowance A_C, score sensitivity","R4: score sensitivity in bits per unit and slack candidates?","COMPUTED",
 "Exact ledger: 0.001505 bit per doubling of A_C at 2^78 (78->79); A_C 2^80 +0.0045, 2^84 +0.0919, 2^90 +2.399; cost thresholds: +0.01 bit at A_C=2^80.94, +0.1 bit at 2^84.12, +1 bit at 2^87.9. Whole allowance is worth only 0.0015 bit; no slack to gain (removing it saves 0.0015 bit).",
 " Sensitivity from a0lean38.ledger(A_C=...) with the same calibration.",
 "Not a lever: the premise matters for the judge ruling (validity), not for the number. A_C may be raised by 2^9.9 (x ~940) before the score moves 0.1 bit."))
R.append(rec("sha256-38|PREM.H6|PREM|R3","H6 memory 1,045,792 B, control","R3: control (known answer or negative control)?","COMPUTED",
 "Known answer: memory() sums to 1,045,792 B = 2^19.996165 (slack 2,784 B = 87 instructions of 32 B); component list identical to proof Section 14. Negative control: 33 B per instruction gives 1,056,395 B (over 2^20, penalty 0.0107 bit), 36 B gives 0.0535 bit, 64 B gives 0.4016 bit, so the check does fail when it must; breakeven is 32.26 B per instruction. Plane-program instruction total 9,946 is produced by the builder (7 programs 1410..1426).",
 " The 600 instructions of 'other routines' and the 5 loop slots are asserted constants in memory(), not metered. Metered passing-path of step3b: prologue 179 ops, rolled round body 106, rows 16..21 checks unrolled adds about 300, final 17 = about 600 static instructions for step3b alone (estimate, assumes unrolled row checks and a rolled round loop; a table-driven check would be smaller). Add fb_scalars 37, planes loop, lane scan, first-block words: estimate 700..800 instead of 600.",
 "LABEL estimate/bound: if the other-routine code is 800 instructions the total is 1,052,192 B, 113 instructions over slack, penalty 0.0050 bit (700 instr: 1,048,992 B, 13 instr over, 0.0006 bit). Not an exact static count of a real program; we ran no assembler. Penalty is tiny either way, but the claim 'under 2^20' rests on the 600 figure."))
R.append(rec("sha256-38|PREM.H6|PREM|R4","H6 memory 1,045,792 B, score sensitivity","R4: score sensitivity in bits per unit and slack candidates?","COMPUTED",
 "Exact: S = T + max(0, log2 B - 20). Slack 2,784 B (87 x 32 B instructions); above 2^20 each extra byte costs 1.376e-6 bit (0.0107 bit for the full 33 B/instr reading, 1,056,395 B). Code is 339,296 of 1,045,792 B (32.4%); planes 675,840 B (64.6%); at 4 B/instr total is 748,908 B (299 KB under 2^20).",
 " Sensitivity table from memory(cal) with bytes per instruction varied; score arithmetic is exact, the instruction size is a convention (the machine model defines none).",
 "Slack candidates: if code were counted at 4 B per instruction, 299 KB headroom could hold more classes (not measured, no time gain computed here)."))
for r in R:
    fn=os.path.join(D,r['id'].replace('|','_').replace('.','_')+'.json')
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1,ensure_ascii=False)
    try: add_cell.validate(json.load(open(fn,encoding='utf-8')), add_cell.load()); print('OK',fn)
    except Exception as e: print('FAIL',fn,e)
