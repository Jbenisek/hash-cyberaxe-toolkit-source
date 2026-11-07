
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

import json, glob, statistics as S, sys, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
W = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/sha3-r5-U01')
th = json.load(open(W + r'\work\theta_scan.json'))
ok = []
for f in glob.glob(W + r'\work\conn_k*.json'):
    d = json.load(open(f))
    ok += [a for a in d["attempts"] if a.get("status") == "ok"]


def rg(fn):
    v = [fn(a) for a in ok]
    return "%d-%d (mean %.1f)" % (min(v), max(v), S.mean(v))


m2 = rg(lambda a: a["EM_M2"] - a["EM_M1"])
m3 = rg(lambda a: a["EM_M3"] - a["EM_M2"])
m4 = rg(lambda a: a["EM_M4"] - a["EM_M3"])
dfm3 = rg(lambda a: 1600 - a["EM_M3"])
dff = rg(lambda a: a["DF"])
inact = rg(lambda a: a["inactive_rows"])
edz = rg(lambda a: a["ED_after_zero"] - a["ED_F"])
nacc = len(ok)
imp_lo = 127 - max(a["EM_M4"] - a["EM_M3"] for a in ok)
imp_hi = 127 - min(a["EM_M4"] - a["EM_M3"] for a in ok)
base_ev = ("research/dig/incoming/sha3-r5-U01/work/conn_count.py; work/conn_k1,2,5,6,8,9,11 .json/.log; work/summ.txt")
common = dict(hash="sha3-r5", source="our workflow: scan-once", own_test=True, date="2026-10-12", lever=False, gain_bits=0.0)


def rec(cid, rnd, obj, q, question, labels, status, number, evidence, notes, topic):
    r = dict(common, row_i=rnd, row_j=rnd, object=obj, question=question, labels=labels, status=status,
             number=number, evidence=evidence, notes="Universe cell " + cid + ". " + notes, topic=topic)
    return cid, r


recs = []
scope = ("Scope: 7 advice runs of the shipped constructor (R7 labels k=1,2,5,6,8,9,11; bprime candidate 0, its (c,j,DF) matches "
         "the proof table), up to 40 connector attempts each, %d accepted attempts; instrumented copy of r5.py _attempt that only adds rank "
         "counters. Not the 50 historical R7 spaces (not persisted); a sample, not the full population." % nacc)
recs.append(rec("sha3-r5|round0.chi|chi|Q1", 0, "r5 round-0 chi connector conditions (beta0 -> alpha1)", "Q1",
                "How many connector conditions does the package constructor use at round 0 chi?", ["C"], "SAMPLED",
                "F fixed bits = 520 exactly (every attempt; rank 520 in E_D and E_M); E_D zero-difference rows: %s inactive alpha1 rows (E_D rank gain %s); "
                "M2 row conditions add E_M rank %s (of 1600); M3 linearisation adds %s; active alpha1 rows 307-318." % (inact, edz, m2, m3),
                base_ev, scope + " 520 = bits 1080..1599 (capacity plus the 0x86 pad byte). M2 rank = E_M rank gain from the chosen (d, affine W) per active row.",
                "sha3.r5.conn.r0.count"))
recs.append(rec("sha3-r5|round0.chi|chi|Q3", 0, "r5 round-0 chi connector freedom", "Q3",
                "How many degrees of freedom of the 1600-bit space remain after the round-0 conditions (F, M2, M3)?", ["C"], "SAMPLED",
                "DF after F+M2+M3 = 1600 - rank(E_M) = %s (before M4); needed final DF is 33 (final DF is the round-1 cell). E_D reaches full rank 1600 in every attempt (beta0 fully determined)." % dfm3,
                base_ev, scope, "sha3.r5.conn.r0.df"))
recs.append(rec("sha3-r5|round1.chi|chi|Q1", 1, "r5 round-1 chi conditions M4 (beta1' -> alpha2, 59 rows)", "Q1",
                "How many round-1 linear conditions (M4) does the constructor add, and how many are independent?", ["C"], "SAMPLED",
                "M4 = 127 conditions in all 7 beta1 candidates (exact, from annih of the 59 alpha2 rows); independent E_M rank gain %s, so %d to %d of the 127 are implied by earlier conditions." % (m4, imp_lo, imp_hi),
                base_ev, scope + " Attempts ending in status cond (M4 inconsistent) are excluded from rank figures (8-34 of 40 per advice).",
                "sha3.r5.conn.r1.count"))
recs.append(rec("sha3-r5|round1.chi|chi|Q3", 1, "r5 round-1 chi connector freedom (final DF)", "Q3",
                "What DF is left after M4, against the needed 33?", ["C"], "SAMPLED",
                "final DF = 1600 - rank(E_M after M4) = %s over %d accepted attempts; min 33 = the threshold (2 attempts at 33), none below; DF drop M3->M4 = %s. "
                "The atlas's 45-60 'typical' is not what this sample shows: %d of %d accepted attempts have DF >= 45." % (dff, nacc, m4, sum(a["DF"] >= 45 for a in ok), nacc),
                base_ev, scope + " DF depends on the advice (per advice runs: 36-37, 41-44, 49-53). Not binding for cost: only 32 window dimensions are used.",
                "sha3.r5.conn.r1.df"))


def get(r):
    pc = th["round%d" % r]["per_cert"]
    kern = th["round%d" % r]["in_kernel"]
    cols = (min(p["colparity_cols"] for p in pc), max(p["colparity_cols"] for p in pc))
    ra = (min(p["rows_alpha"] for p in pc), max(p["rows_alpha"] for p in pc))
    rb = (min(p["rows_beta"] for p in pc), max(p["rows_beta"] for p in pc))
    al = [v for k, v in th["alts"].items() if k.endswith("/r%d" % r)]
    return kern, cols, ra, rb, al


ev2 = "research/dig/incoming/sha3-r5-U01/work/theta_scan.py; work/theta_scan.log; work/theta_scan.json"
tscope = ("Method: own Keccak (tools/traillab/sha3_atlas/kk.py) on the 16 collision pairs of the pkgR5L certificates (all 16 reproduce the equal 4-lane digest, "
          "beta2 = trail BETA2 and alpha3 = trail alpha3 in the CP kernel, validated first); alternatives tested on the first 3 pairs: every single-bit flip of the "
          "round input (non-kernel) and every same-column bit pair (kernel-preserving), counting active chi rows of L(.) and reachability of the required next difference. "
          "Window only (16 pairs, local flips), not all kernel alternatives.")
k, cols, ra, rb, al = get(0)
recs.append(rec("sha3-r5|round0.theta|theta|Q4", 0, "r5 round-0 theta kernel membership and alternatives", "Q4",
                "Is the round-0 input difference alpha0 in the column-parity kernel, and what do non-kernel alternatives do?", ["Z"], "LOCAL_ONLY",
                "alpha0 NOT in kernel in %d of 16 pairs (%d-%d nonzero parity columns of 320); active chi rows alpha0 %d-%d -> beta0 %d-%d; single-bit flips of the 1088 rate bits give beta0 rows %d-%d, "
                "kernel-preserving same-column pairs %d-%d; no flip makes beta0 sparse (all >= 304 rows, base 307-318)." % (
                    16 - k, cols[0], cols[1], ra[0], ra[1], rb[0], rb[1], min(a["single_rows_beta_min"] for a in al), max(a["single_rows_beta_max"] for a in al),
                    min(a["pair_rows_beta_min"] for a in al), max(a["pair_rows_beta_max"] for a in al)),
                ev2, tscope + " Round 0 is dense by design: beta0 is chosen by the connector, no sparse path to protect.", "sha3.r5.theta.r0.kernel"))
k, cols, ra, rb, al = get(1)
recs.append(rec("sha3-r5|round1.theta|theta|Q4", 1, "r5 round-1 theta kernel membership and alternatives", "Q4",
                "Is alpha1 in the column-parity kernel, and do alternatives reach the same alpha2?", ["Z"], "LOCAL_ONLY",
                "alpha1 NOT in kernel in %d of 16 pairs (%d-%d nonzero parity columns); active rows alpha1 %d-%d -> beta1 exactly 59 rows in all 16 pairs (the 59 rows of alpha2). "
                "Exact alpha2 reachable through chi: base yes; all 1600 single-bit flips: 0 reach; kernel-preserving same-column pairs reaching: %s of 3200 (first 3 pairs)." % (
                    16 - k, cols[0], cols[1], ra[0], ra[1], "/".join(str(a["pair_reach_alpha2"]) for a in al)),
                ev2, tscope + " The few reaching pair flips are neighbouring beta1 row choices (the connector's own D2/M2 choices); not tested as new freedom.",
                "sha3.r5.theta.r1.kernel"))
k, cols, ra, rb, al = get(2)
recs.append(rec("sha3-r5|round2.theta|theta|Q4", 2, "r5 round-2 theta kernel membership and alternatives", "Q4",
                "Is alpha2 in the column-parity kernel, and do alternatives keep beta2 and reach alpha3?", ["Z"], "LOCAL_ONLY",
                "alpha2 NOT in kernel (exactly 20 nonzero parity columns in all 16 pairs); 59 active rows -> beta2 = 10 active rows (14 bits). Single-bit flips of alpha2 give beta2 rows %d-%d (> 10) and 0 of 1600 reach alpha3; "
                "same-column pairs (3200) give %d-%d rows and 0 of 3200 reach alpha3." % (
                    min(a["single_rows_beta_min"] for a in al), max(a["single_rows_beta_max"] for a in al), min(a["pair_rows_beta_min"] for a in al), max(a["pair_rows_beta_max"] for a in al)),
                ev2, tscope + " alpha2 is fixed by the trail (all 16 pairs identical beta2). Local-flip test only; the exact alpha3' cluster (chi, 2^24) is the existing ex.py result and was not redone.",
                "sha3.r5.theta.r2.kernel"))
k, cols, ra, rb, al = get(4)
recs.append(rec("sha3-r5|round4.theta|theta|Q4", 4, "r5 round-4 theta kernel membership and alternatives", "Q4",
                "Is alpha4 in the column-parity kernel, and do alternatives keep the zero-digest condition?", ["Z"], "LOCAL_ONLY",
                "alpha4 in kernel in %d of 16 pairs (the other %d have exactly 1 nonzero parity column); alpha4 has 9 active rows, weight 14-17; beta4 %d-%d rows. "
                "Digest condition (plane-0 rows q with DDT[q][0] or DDT[q][16] nonzero): base ok; single-bit flips keeping it: %s of 1600; same-column pairs keeping it: %s of 3200 (first 3 pairs)." % (
                    k, 16 - k, rb[0], rb[1], "/".join(str(a["single_digest_ok"]) for a in al), "/".join(str(a["pair_digest_ok"]) for a in al)),
                ev2, tscope + " Kernel membership at round 4 is common but not required (pairs with one parity column collide too); consistent with the atlas statement that round 4 is event-exact.",
                "sha3.r5.theta.r4.kernel"))
ex = add_cell.load()
for cid, r in recs:
    fn = W + "\\" + cid.replace("|", "_") + ".json"
    json.dump(r, open(fn, "w"), indent=1)
    print(cid, add_cell.validate(r, ex))
