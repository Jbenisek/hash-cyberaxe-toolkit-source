
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

import json,os,sys
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
out=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G07-U02')
W="research/dig/incoming2/sha256-37-G07-U02/work/"
ev=W+"analyse.py; "+W+"h5b.py; "+W+"rate.c; "+W+"lowm.py (copy of pkgR37M3 experiments/lowm.py); research/tools/build_pkg/scratch/pkgR37M3/pkg/sha256-r37/proof.md Sections 10, 11.2, 12 (H4, H5, H7), Appendix C"
KN=" Known-answer check: lowm.py ledger() reproduces the package claim time_log2 60.99099, N_FB 60,951,875,249,131,685, mu0 0.49558494, Pcap 0.00056206 (28103/5e7), preprocessing_log2 60.00141, success bound 0.3900000019 (exact Decimal/Fraction arithmetic). Package pkgR37M3 (r37 convention, memory 607,744 B = 2^19.21 < 2^20, so the new memory term max(0, log2 B - 20) is 0 and score = time_log2). Scan once; not a filed package."
def rec(cid,obj,q,num,notes,topic,status="COMPUTED",labels=("N",)):
    return dict(hash="sha256-37",row_i=None,row_j=None,object=obj,question=q,labels=list(labels),status=status,number=num,source="our workflow: scan-once-wave2",own_test=True,evidence=ev,date="2026-10-12",lever=False,gain_bits=None,notes="universe cell "+cid+". "+notes+KN,topic=topic)
R={}
c="sha256-37|PREM.H4|PREM|R2"
R[c]=rec(c,"H4 advice allowances A_C 2^60, A_S 2^50, DEV 2^40","R2: exact recount of the allowance comparison and own re-measurement of the CPU-second price behind A_C",
 "Recount (exact): 593,858 CPU-s x 2^21.427 units/CPU-s = 2^40.6068 units; 2^60 / that = 688,569x (text says 688,000: consistent, rounded down); A_C = 2^38.573 CPU-s at that price. A_S = 2^50 vs paper 2^41.3 = 2^8.70 = 415.9x. Shares of T = 2^60.99099: A_C 50.31%, A_S 0.0491%, DEV 4.8e-5%. Own SHA-256 compression rate (SAMPLED, single 3-s runs, machine at load 24 of 24 cores, CPU-time clock, one thread): portable C -O2 1.19-1.43 M compressions/s = 2^20.2-2^20.45 (known answer sha256('abc') ok); OpenSSL (16 KiB blocks, bytes/64) 12.84 M/s = 2^23.65. The accepted price 2^21.427 (2.82 M/s) lies between our portable-C rate and the OpenSSL rate. Sensitivity (exact ledger reruns): A_C 2^59 -0.418 bit, 2^58 -0.684, 2^56 -0.921, 2^52 -1.003, 2^61 +0.588; about 0.418 bit of time per bit of A_C near 2^60; A_C -> 0 would save 1.009 bits; A_S -> 2^41.3 saves 0.00071 bit; DEV -> 0 saves 7e-7 bit.",
 "Policy row, not arithmetic: A_C is a bound by comparison, the 37-step search time is unpublished (proof Limitations). Rate numbers are single runs under heavy load (the portable-C figure is a floor); they are not part of the filed argument. With the OpenSSL rate a CPU-second would be priced 4.5x higher than the accepted calibration, so the 593,858 CPU-s re-run would be worth more units and the ratio 2^60/re-run would be about 151,000x; with our portable-C rate (1.43 M/s) it would be about 1.36 million x. The 2^60 allowance stays above the re-run in all three. The 25 ms per SFS-pair completion (organizer experiment a0-sfs-r37) was not re-run here (no experiment file for it in the package folder).",
 "PREM.H4")
c="sha256-37|PREM.H4|PREM|R3"
R[c]=rec(c,"H4 advice allowances A_C 2^60, A_S 2^50, DEV 2^40","R3: control - the recount and the ledger on a known answer, and a wrong-constant negative control that must fail",
 "Positive: the recount reproduces the package text (688,000x, 2^38.57 CPU-s, 2^8.7x) from its stated inputs (593,858; 2^21.427; 2^41.3); lowm.py ledger(ac_log2=60) reproduces the filed 60.99099 and ledger(ac_log2 = 52, 56, 58) is monotone (59.98762, 60.07046, 60.30749). Negative: pricing a CPU-second with the primitive constant C_REF = 2644 (primitives per compression, wrong unit) gives 2^60 / (593,858 x 2644) = 7.3e8x (2^29.45), which does not match 688,000x (fails as required): the price must be the 2^21.427 units-per-second figure. Cross-check with our own portable-C rate (1.43 M/s) gives 1.36e6x, same order as the claim.",
 "No judge dossier applies to H4 (not a judge cause in any ruling we hold), so the dossier-control arm was not run. The control checks that the recount is internally consistent and unit-correct; it does not validate the 2^21.427 calibration itself (taken from accepted filing 6eeefb64).",
 "PREM.H4")
c="sha256-37|PREM.H5|PREM|R4"
R[c]=rec(c,"H5 word-RAM plane-program pricing (166 / 404-431 / 88-95 primitives)","R4: score sensitivity in bits per primitive and slack candidates, exact ledger reruns of lowm.py",
 "Bits of time_log2 per ONE primitive off (exact ledger rerun, one parameter changed): per-first-block FIXED item (contains the 166-primitive F7 class test) 1.45e-5; F7 test 166 -> 0 saves 0.00241 bit; group body 31 -> 30: 0.003024 bit (31 -> 0: 0.0968); probe (11,12,12,12): 0.003024 bit per primitive per stage (all 47 -> 0: 0.1495); SCAN_LANE 8 -> 7: 0.006016 bit; EX_OPS 34 -> 33 and SURV_LANE 7 -> 6: 0.001512 each; SURV_FIX 8 -> 7: 0.001096; CLS_LANE 6 -> 5: 5.1e-5; ROWCOMP/ROWCHECK -1: 2.0e-5 each; W6 batch counts (404, 415, 420, 431) -1 each: 9.8e-6, 6.8e-5, 4.2e-5, 4.2e-5; subtraction runs (88-95) -1 each: 1.0e-5 to 4.2e-5 (all W6 -1: 1.6e-4; all SUBF -1: 2.3e-4); W6 all free: 0.0696; SUBF all free: 0.0210; all FIXED (615) free: 0.00895. 2^38 preprocessing ops -> 0: about 2^-34. Memory term stays 0 (607,744 B < 2^20) under the new scoring.",
 "The score is far more sensitive to the per-pair group/probe/scan primitives (0.003-0.006 bit each) than to the plane programs the premise names (W7 166, W6 404-431, SUBF 88-95: at most 7e-5 bit per primitive). Values are exact reruns of the shipped ledger with one parameter changed, not constructed programs: a lower count is a slack candidate only if a shorter straight-line text exists. Data-independence of the straight-line counts was not re-derived from other seeds here (R3 not requested for H5).",
 "PREM.H5")
c="sha256-37|PREM.H7|PREM|R3"
R[c]=rec(c,"H7 success floor mu0 = 0.49558494, Pcap = 0.00056206","R3: control - mu0 from the formula on a known answer, plus a negative control that must fail",
 "Positive (exact, 60-digit Decimal): mu_req(Pcap = 0.00056206) = 0.49558494, success 0.390000001931 > 0.39. Negative: mu0 - 1e-8 = 0.49558493 gives success 0.389999995841 < 0.39 (the 8th decimal is tight; fails as required). Known answer from an accepted filing: Pcap = 0.00035769 gives mu0 = 0.49524941, success 0.3900000043 (the values of the earlier R37X filing). Wrong-formula controls: dropping Pcap gives mu 0.49466242, dropping the (1 - 2^-10.4) divisor gives 0.49521816; neither matches a filed value. Pcap recomputed from ledger parts vmax_fb / (s^2 N_FB vbar), s = 2^-12: 0.000562052 <= assumed 0.00056206 (28103/5e7).",
 "Sensitivity: Pcap +1e-5 -> mu0 0.49560136 and log2 N_FB +4.8e-5 bit; +1e-4 -> +4.8e-4 bit; Pcap = 0 would lower log2 N_FB by 0.00269 bit. So the Chebyshev slack trade (Pcap versus V_MAX) is worth at most 0.0027 bit from the cap side. This control checks arithmetic only; whether Chebyshev with these moments is the right bound is a proof matter, not tested here.",
 "PREM.H7")
for cid,r in R.items():
    fn=os.path.join(out,cid.replace('|','_')+'.json')
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    print(os.path.basename(fn),add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()))
