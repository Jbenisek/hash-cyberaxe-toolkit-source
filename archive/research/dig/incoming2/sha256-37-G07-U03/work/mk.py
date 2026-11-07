
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
base=dict(hash="sha256-37",row_i=16,row_j=36,labels=["Z"],source="our workflow: scan-once-wave2",own_test=True,
 evidence="research/dig/incoming2/sha256-37-G07-U03/work/ (smc.c = copy of research/retest/dense_boring/smc.c with absolute chi path; run.sh, out_np*.txt, an.py)",
 date="2026-10-12",lever=False,gain_bits=None,topic="sha256-37|PREM.SMC")
tbl="NP 8192: 12 reps mean log2 q3 -73.9977 sd 0.0252; NP 2048: 24 reps -74.0049 sd 0.0742; NP 512: 48 reps -73.9963 sd 0.1122; NP 64: 96 reps -73.9538 sd 0.3055; NP 8: 150 reps -74.2042 sd 0.9215"
recs={
"R1":dict(object="SMC q3 estimator: value charged and how its uncertainty is stated",question="What q3 does the shipped R37M3 ledger charge, and on what SMC evidence (R1)?",status="COMPUTED",
 number="Charged: Q3_LOG2 = -71.47 in lowm.py (R37M3, four-pattern rows 18-19 credit; slack 2^-12 in the ledger). Base-characteristic SMC evidence behind it: q3_used -74.08 / model -74.03 (dense_boring), ffbe30bb re-derived 2^-74.02 -> 2^-72.04 by preregistered full-path SMC. Uncertainty is stated as a spread over independent seeds/reps (sd/sqrt(reps)), not as a within-run particle SE.",
 notes="universe cell sha256-37|PREM.SMC|PREM|R1. Read from the lowm_copy.py scratch copy (grep Q3_LOG2) and research/FILINGS.md line for ffbe30bb. The 222-class four-pattern SMC for R37M3 is not re-run here (verify_grok103.md says it does not exist). Reads only; the measurement is in R2."),
"R2":dict(object="SMC q3 estimator: resampling correlation, fresh-seed re-measurement",question="Do repeated SMC runs (fresh seeds) agree, and does the spread scale as NP^-1/2 (no correlation floor from resampling) (R2)?",status="SAMPLED",
 number="Base characteristic, G, own smc.c, M512 MT22 4096 MT 1024, fresh seeds 9101-9105. "+tbl+". sd*sqrt(NP) = 2.28, 3.36, 2.54, 2.44, 2.61: flat from NP 8 to 8192 (no floor). sd ratio NP512/NP8192 = 4.45 (rule: within [2.5,6.4] around 4; passed). Mean log2 q3 at NP>=512: -73.998 +- 0.007 (NP8192 se), all NP>=512 agree within 1 se of -74.00 (linear-mean agrees to 0.005 bit).",
 notes="universe cell sha256-37|PREM.SMC|PREM|R2. Rule written in run.sh BEFORE the run. NP2048/NP8192 sd ratio 2.94 vs 2 (12-rep sd at NP8192 has wide chi2 interval); not a failure of the NP512 rule but noted. Earlier dense_boring: 8 reps NP8192 sd 0.0414 (pooled with this run sd*sqrt(NP) ~3). Particle correlation inside one run is not estimated directly; between-rep spread is the quantity that matters and it is what the ledger uses. Slack in filed q3_used (-74.08) vs measured -73.998: 0.08 bit."),
"R3":dict(object="SMC q3 estimator: control arm",question="Does the same tool show the expected failure signature when particles are starved (negative control) (R3)?",status="SAMPLED",
 number="Control NP 8 (150 reps): mean log2 q3 -74.2042 (bias -0.21 bit vs NP>=512 mean, log scale, Jensen), sd 0.9215 (x36 of NP8192); linear-scale mean gives -73.9448 (+0.05 bit, within 1 se 0.075 of the others). NP 64: log-mean -73.954, sd 0.3055. Known answer: stage means reproduce the exact stages -16.994, -13.000, -15.00, -6, -7, -1, -11, -4 (rows 16,17,18,19,20,21,22,24).",
 notes="universe cell sha256-37|PREM.SMC|PREM|R3. Control fires: small NP gives larger sd and a log-scale low bias, as theory predicts; the shipped NP 8192 has bias below 0.001 bit by var/2 ln2 (var ~ 0.0006-0.0017 log2^2). 0 failed reps in all arms."),
"R4":dict(object="SMC q3 estimator: score sensitivity",question="How many bits of score per bit of q3, and what slack does the resampling noise leave (R4)?",status="COMPUTED",
 number="nfb = ceil(XREQ/(g*32*q3)) in lowm.ledger, so time_log2 moves ~1 bit per bit of log2 q3 (per-FB cost fixed). Resampling noise of the q3 estimate: sd 0.025-0.04 bit per NP8192 rep; with 16 reps se <= 0.01 bit. Filed base q3_used -74.08 sits 0.08 bit below measured -73.998 (conservative side); a 0.01 bit se is 0.01 bit of T.",
 notes="universe cell sha256-37|PREM.SMC|PREM|R4. Sensitivity from reading lowm_copy.py line 793-800 (ledger), not re-run. The four-pattern -71.47 value was not re-measured in this unit."),
}
import os
for k,r in recs.items():
    d=dict(base); d.update(r)
    f=f"sha256-37_PREM.SMC_PREM_{k}.json"
    json.dump(d,open(f,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(f,encoding='utf-8')),add_cell.load()); print(k,'ok')
    os.replace(f,'../'+f)
