
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
OUT=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U03')
AC=open('t5_out.txt').read()
ACRES="NOT demonstrated in 20 min: 4 random instances tried, the exhaustive search over x' (2^32) found 0, 0, 1, 2 candidates for a1+b1 = a1'+b1'; for the 2 instances that had one, the exhaustive search over y (2^32) for c2 = c2' found 0 solutions (a third was cut off at the time limit), so no (a,c)-equal pair was produced"
VAL=("Validated first: our 2-round compress equals verifier/blake3.py _compress on 3000/3000 random inputs (64-bit counters, random flags, block length, cv); 7-round BLAKE3('') = af1349b9...3262 reproduced and equals verifier blake3(b'',7); construction b3ctr.py (pkgB3S2 proof Sec 8 lines) reproduces Lemma L (round-0 state equal for A,B), pins X3/X7/X11/X15 and digest words 0,2,5,7 equal on 3000/3000 trials at t_hi=0.")
EV="research/dig/incoming2/blake3-r2-G05-U03/work/ (t1.py, t2.py, t3.py, t3_out.txt, t4.py, t5.py, t5_out.txt, b3ctr.py copied from research/dig/incoming/blake3-r2-U07/work)"
base=dict(hash="blake3-r2",row_i=None,row_j=None,source="our workflow: scan-once-wave2",own_test=True,evidence=EV,date="2026-10-12",lever=False,gain_bits=0.0,gain_basis="count")
recs={}
recs["blake3-r2_INIT.v13_INIT_Q2"]=dict(base,
 object="state word v13 = t_hi (chunk counter high), necessity of v13 = 0",
 question="Q2: is v13 = 0 (t < 2^32) needed; relax it to any t_hi and recount the exact outcome mass",
 labels=["N","K","I"],status="SAMPLED",
 number="Not needed. v13 enters the construction in ONE line (K1.a1 = ROL(K1.d1,16) XOR t_hi, giving w2, then w3). Relaxed to t_hi = 0 / random <2^16 / random <2^32: round-0 state equal, pins X3,X7,X11,X15 kept, digest words 0,2,5,7 equal on 3000/3000 each. Outcome structure with c1 in Q* and Y4 in the class: beta = 18b0e098 and eta = 830303cf on 4000/4000 for t_hi = 0 and 4000/4000 for random 32-bit t_hi (95% lower bound 0.9992 each). Residual R (words 1,3,4,6 XOR) mean Hamming weight 63.173 (t_hi=0) vs 63.075 (random t_hi), sd 6.5, difference -0.098, z -0.68. Outcome mass per trial unchanged (c1 and Y4 are free words, not functions of t_hi). With the 9 other free words fixed, changing t_hi alone changes w0,w1,w2,w3,w8,w9 and t_lo (300/300) and every call state from K0 on: a fresh trial, not an alias.",
 topic="b3.r2.INIT.v13",
 notes="universe cell blake3-r2|INIT.v13|INIT|Q2. "+VAL+" v13 = 0 is a convenience of the filed claim (restriction 1 <= t < 2^32), not a necessity; the verifier accepts messages below 2^61 bytes, so t_hi >= 1 means a message of at least 4 TiB. The counts are samples of a structural identity (the line list), reported as sampled with the rule-of-three interval. No gain: it only adds a 10th free word. Not tested: a judge ruling on messages above 4 TiB, time cost of materialising F for t_hi >= 1.")
recs["blake3-r2_INIT.v13_INIT_Q4"]=dict(base,
 object="state word v13 = t_hi, alternatives (free 10th word; counter-high difference as the A/B difference)",
 question="Q4: alternatives to v13 = 0: t_hi as a free word, or a v13 difference absorbed in K1 by (m2,m3) in place of the length difference",
 labels=["Z","N"],status="LOCAL_ONLY",
 number="(1) t_hi as a free word: a 10th free word, each value a fresh trial of the same rate (300/300 end states differ); per-context cost is 2^59.3 of 2^71.9 machine units (BLAKE3_2ROUND_MAP Sec 2.7), so even free fresh contexts could save at most 2^-12.6 of the total. No saving. (2) v13 difference absorbed in K1 by (m2,m3): round-0 state equal 5000/5000; m2 and m3 are the FIRST words of C0 and C1, so C0, C1 and all of E0..E3 are active; for random states 0 of 8 digest words equal in 5000/5000 (the length-route control, same procedure without its solved pins, is also 0/5000; its 4 pinned words come from the solved X3,X7,X11,X15). Local pin feasibility of one first-word-difference call (identical inputs, only x differs, same y), outputs a and c equal while b,d differ: "+ACRES+". So E1,E3 could be clean only if C1 gets (a,c) equal and C0 (b,d) equal; that mirrors the length route (4 pins, residual E0+E2 = 128 bits) and is NOT shown to be completable (needs joint pin equations on X0,X4,X8,X12,X1,X5,X9,X13 plus a host with two chunk indices differing by a multiple of 2^32).",
 topic="b3.r2.INIT.v13.alt",
 notes="universe cell blake3-r2|INIT.v13|INIT|Q4. "+VAL+" Window: one-call pin existence on one random instance (eq1 by exhaustive search of x' over 2^32, eq2 over y, verified with scalar G); not a count, and the two-call pin system was not solved. Structural catch: A and B with different t_hi sit at different chunk indices, so their trees differ above the chunk (CLOSED_DOORS row 3, tighten/b3_parent_node_scout.md); this is a possible distinct attack path only if a host exists; none found. No gain claimed.")
recs["blake3-r2_INIT.v12_INIT_Q2"]=dict(base,
 object="state word v12 = t_lo (chunk counter low), necessity of solving it per trial",
 question="Q2: is the solved counter t_lo needed; replace it by a fixed counter and recount the exact outcome mass",
 labels=["I","E"],status="SAMPLED",
 number="Needed for the beta* concentration, worth exactly 11 bits. c1 -> t_lo is a permutation of the 32-bit words (0 collisions in 10,000 draws; the inverse c1*(t0) reproduces t_lo = t0 on 9000/9000 builds). So for a FIXED counter t0 each (outer words, y) has exactly one c1, and it lies in the beta* cube Q* with probability 2^21/2^32 = 2^-11. Measured on 4,194,304 draws: t0=1: 2092 hits (log2 p = -10.969, Wilson95 [-11.031,-10.908]); t0=1000: 2029 (-11.013, [-11.076,-10.951]); t0=0xdeadbeef: 2129 (-10.944, [-11.005,-10.883]); expected 2048. The solved counter keeps all 2^21 members of Q* per (outer, y); a fixed counter keeps one c1, in Q* with probability 2^-11: -11 bits (the 2^11 of Lemma S1 re-measured by inversion).",
 topic="b3.r2.INIT.v12",
 notes="universe cell blake3-r2|INIT.v12|INIT|Q2. "+VAL+" Fixed t0 tested with flags 3 (non-root last chunk, t0 >= 1). t0 = 0 is not a valid trial of this family (single chunk, root flags 11 changes the K3.d1 line); the counter-0 root instance was not re-priced here. The mass recount is the Q*-hit probability only; the rest of the rate (E1/E3 outcome counts) is unchanged by the counter because t_lo enters only the K0.a1 line. No gain: confirms the lever is already in the filed construction.")
recs["blake3-r2_INIT.v12_INIT_Q4"]=dict(base,
 object="state word v12 = t_lo, alternatives (fixed t >= 1; counter difference as the A/B difference)",
 question="Q4: alternatives to a solved t_lo: fixed chunk index t >= 1, or a v12 difference absorbed in K0 by (m0,m1) in place of the length difference (R1C transfer)",
 labels=["Z","E"],status="COMPUTED",
 number="(1) Fixed t0 >= 1: loses exactly 11 bits of beta* concentration (see INIT.v12 Q2: 2^-10.97 / 2^-11.01 / 2^-10.94 measured vs 2^-11); a small t0 would make F short but costs the 11 bits. (2) v12 difference absorbed in K0 by (m0,m1): round-0 state equal 5000/5000, but w0 is the SECOND word of C2 and its input state is identical for A and B, so all four C2 outputs differ (algebra: a2 differs, d2 = ROR(d1 XOR a2, 8) differs with d1 equal, then c2, b2); measured 4 of 4 outputs differ in 5000/5000, E0..E3 all active (w1 also enters E0) and 0 of 8 digest words equal in 5000/5000. No pin can fix it: the route has no clean E call, residual about 256 bits against 128 for the length route (4 digest words pinned by Fact P).",
 topic="b3.r2.INIT.v12.alt",
 notes="universe cell blake3-r2|INIT.v12|INIT|Q4. "+VAL+" This is the 2-round version of the 1-round R1C line (counter cancelled by m0,m1); at 1 round nothing re-reads w0,w1, at 2 rounds C2 and E0 re-read them. Not tested: a counter difference combined with a flag/length difference so that the C2 second-word difference is cancelled by a second source (CLOSED_DOORS rows 21,22), and the tree host for two chunk indices (row 3). No gain.")
os.makedirs(OUT,exist_ok=True)
cells=add_cell.load()
for k,r in recs.items():
    p=os.path.join(OUT,k+".json")
    json.dump(r,open(p,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(p,encoding='utf-8')),cells)
    print("valid",p)
