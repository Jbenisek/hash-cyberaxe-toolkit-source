
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

import json,sys,os,re
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
ex=add_cell.load()
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U06')
EV="research/dig/incoming2/blake3-r2-G05-U06/work/scan.c; scan_out.txt; sample.py; ref.py"
MODEL=" Model: post-round-0 state X and round-1 words free apart from the pins (X3,X7,X11,X15,w4,w13 = pkgCK values), pair B = A with w4+8, w5-8; legality of the round-0 half (real 55/63-byte messages) is not re-checked, so LOCAL_ONLY. Validation: ref.py round-1 compression equals the organizer verifier (hash-smash/verifier/blake3.py, r=2) on 200 random messages; C3 known answer (Y3 8127c181/7edf3e7e, Y7 76f7aefd, Y11 7af77f38/850000c3, Y15 bbfbdffe) reproduced by scan.c; digest fold = Z[i]^Z[i+8]."
def rec(cell,object_,question,number,notes,labels):
    r=dict(hash="blake3-r2",row_i=None,row_j=None,object=object_,question=question,labels=labels,status="LOCAL_ONLY",number=number,
      source="our workflow: scan-once-wave2",own_test=True,evidence=EV,date="2026-10-12",lever=False,gain_bits=None,
      notes="universe cell %s. "%cell+notes+MODEL, topic=cell)
    return r
R=[]
R.append(rec("blake3-r2|OUT.d4|OUT|Q2","digest word 4 = Z4^Z12 (E3 b-out ^ E1 d-out), residual word","Necessity: is it required that E1 and E3 both be matched, and what is the exact mass if only one side is held?",
 "Cone: word 4 depends on the pair only through dY3 (E3 a-in) and dY11 (E1 c-in). Exact 2^32 scans of Y4 (3 instances): E3-alone dZ4=0 had 3,0,1 solutions (mean 1.33), so holding E3 alone gives word-4 equality at mass ~2^-32 per Y4 value; E1-alone scans of Y12 (3 instances): dZ12=0 had 0,0,0 solutions. Sampled 100000 pinned points: word 4 equal 0 times.",
 "Relaxation made: replace the joint E1-xor-E3 condition by each side alone (dY11=0 or dY3=0 variants). Each single-side version is still a 32-bit condition with about 1 solution per 2^32 scan, so the E1/E3 pairing costs no extra bits over a single-side hold, but the pins cannot be dropped (relaxing X7, X15 or w13 gives 0/100000 equality on any digest word). Counts exact per instance, only 3 instances per scan.",["I"]))
R.append(rec("blake3-r2|OUT.d4|OUT|Q3","digest word 4 degrees of freedom: count over one free word (Y4, Y12)","Exact count of values of one free 32-bit word that make word 4 equal (carry count).",
 "Y4 scan (E3 b-in, true pair, E1 side fixed), 3 instances x 2^32: #(word 4 eq) = 1,3,0 (mean 1.33, total 4 in 3*2^32); Y12 scan (E1 d-in, E3 side fixed): 0,0,0 (0 in 3*2^32).",
 "Exact full scans per instance, but only 3 instances so the mean is a sample with a wide interval. Consistent with Poisson mean ~1 per 32-bit word, no free carry bonus; the Y12 zeros are consistent with mean 1 (P(0,0,0)=0.05) but more instances would be needed before claiming a deficit.",["E"]))
R.append(rec("blake3-r2|OUT.d4|OUT|Q4","digest word 4 alternatives: cancel on E3 only / E1 only / both","Alternative routes to word-4 equality.",
 "(i) true pair, both sides differ: Y4 scan 4 hits in 3*2^32; (ii) E3-alone (dY11=0 variant) dZ4=0: 4 hits in 3*2^32 (3,0,1); (iii) E1-alone (dY3=0 variant) dZ12=0: 0 hits in 3*2^32 (Y12 scan). All about 1 solution per 2^32 scan.",
 "No variant is cheaper than the true pair: each is a single 32-bit equality. Not tested: a joint-relaxation search over (dY7,dY15) pairs (64-bit join, expected about 1 nontrivial solution).",["I"]))
R.append(rec("blake3-r2|OUT.d5|OUT|Q2","digest word 5 = Z5^Z13 (E0 b-out ^ E2 d-out), pinned word","Necessity of the Y7 and Y15 pins for word 5.",
 "Cone: word 5 depends on dY7 (E2 b-in) and dY15 (E0 d-in) only. Relax Y7 only (2^32 scan, 2 instances): #(Z13 same) = 6, 2 (trivial point included); relax Y15 only: #(Z5 same) = 2, 1. Sampled pins: word 5 equal 100000/100000; relax X7: 0/100000, relax X15: 0/100000, relax w13: 0/100000.",
 "Both pins matter: relaxing one (the other held) leaves 1-6 solutions among 2^32 values (trivial one included), so an unpinned Y7' or Y15' that preserves word 5 alone exists at mass ~2^-32 per value but is not free. Exact scan counts, 2 instances.",["I","K"]))
R.append(rec("blake3-r2|OUT.d5|OUT|Q3","digest word 5 degrees of freedom: exact pin multiplicity over X3 and X11","Exact count of X3 (resp. X11) values that keep Y7 and Y15 equal with the other pins fixed.",
 "X3 scan (X7,X11,X15,w4,w13 pinned): #(Y7 equal)=1, #(Y15 equal)=2, #(both)=1 of 2^32. X11 scan: #(Y7 equal)=2, #(Y15 equal)=1, #(both)=1 of 2^32.",
 "Exact full scans, one instance each. The published pin X3=29d4fa98 (resp. X11=44036000) is the UNIQUE solution of the joint b-and-d pin in that coordinate, and at most one other value satisfies either half alone: no extra freedom inside the pin; the 2^256 pair freedom comes from the other words (pinned digest words 0,2,5,7 held for 100000/100000 random free completions).",["E"]))
R.append(rec("blake3-r2|OUT.d6|OUT|Q2","digest word 6 = Z6^Z14 (E1 b-out ^ E3 d-out), residual word","Necessity of matching both E1 and E3 for word 6.",
 "E3-alone dZ14=0 over Y4 scans: 0,0,0 hits in 3*2^32; E1-alone dZ6=0 over Y12 scans: 0,0,0. Word 6 equal 0/100000 on pinned samples.",
 "Single-side holds produced 0 solutions in 3*2^32 each, so the E1/E3 coupling is the only way to word-6 equality found in these scans. Zero hits means mean below about 1 per 3*2^32 at best (interval wide); UNKNOWN beyond that.",["I"]))
R.append(rec("blake3-r2|OUT.d6|OUT|Q3","digest word 6 degrees of freedom: exact count over Y4 and Y12","Exact count of values of one free word making word 6 equal.",
 "Y4 scan (true pair): #(word 6 eq) = 2,0,0 (total 2 in 3*2^32); Y12 scan: 0,2,0 (total 2 in 3*2^32). Joint word 4 and word 6 on the same scan: 0 of 6*2^32.",
 "Exact counts per scan, 3 instances: mean 0.67 per 2^32 against Poisson 1 (within noise). Joint two-word equality never co-occurs (expected 2^-32 per scan), as the 64-bit condition predicts.",["E"]))
R.append(rec("blake3-r2|OUT.d6|OUT|Q4","digest word 6 alternatives: E3-only / E1-only / both","Alternative routes to word-6 equality.",
 "True pair: 2 hits (Y4) + 2 hits (Y12) in 6*2^32; E3-alone dZ14=0: 0 in 3*2^32; E1-alone dZ6=0: 0 in 3*2^32.",
 "Only the coupled (both-sides) form produced word-6 hits; the single-side holds produced none at this sample size, so no cheaper alternative was found. Not a proof.",["I"]))
R.append(rec("blake3-r2|OUT.d7|OUT|Q2","digest word 7 = Z7^Z15 (E2 b-out ^ E0 d-out), pinned word","Necessity of the Y7 and Y15 pins for word 7.",
 "Cone: word 7 depends on dY7 and dY15 only. Relax Y7 only: #(Z7 same) = 1, 4 per 2^32; relax Y15 only: #(Z15 same) = 2, 2. Sampled: pins 100000/100000 equal, any single pin relaxed 0/100000.",
 "Both pins needed; relaxing one leaves a 2^-32-per-value condition (trivial solution plus 0-3 others in the instances scanned). Exact scans, 2 instances.",["I","K"]))
R.append(rec("blake3-r2|OUT.d7|OUT|Q3","digest word 7 degrees of freedom: joint (word 5, word 7) solutions per one-coordinate scan","Exact count over one 32-bit coordinate for words 5 and 7 together.",
 "Relax-Y7 scans: #(word 5 and word 7 both equal) = 1,1; relax-Y15 scans: 1,1 (the trivial point each time) of 2^32. X3 and X11 pin scans: 1 and 1.",
 "Exact. Words 5 and 7 together admit no non-trivial one-coordinate partner in the 4 scans (4 trivial points only). A two-coordinate (dY7,dY15) relaxation is a 64-bit join with about 1 expected nontrivial solution; NOT computed here (needs a 2^32 x 2^32 sort-join).",["E"]))
os.makedirs(D,exist_ok=True)
for r in R:
    f=os.path.join(D,re.sub(r'[^A-Za-z0-9._-]','_',r['topic'])+".json")
    json.dump(r,open(f,'w',encoding='utf-8'),indent=1)
    r2=json.load(open(f,encoding='utf-8'))
    print(os.path.basename(f), add_cell.validate(r2,ex))
