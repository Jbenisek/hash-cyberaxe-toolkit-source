"""Turns proof_t8.md, note_t8.md and build_all8.py (copies of B3R6c's) into the B3R6d versions (exact-match edits)."""
import re
OLDTL = "125.25234"
B3R6C = "1cf99082-22c0-493f-8dcc-5a34b659d885"


def edit(path, fn):
    t = open(path, encoding="utf-8", newline="").read()
    box = [t]

    def rep(a, b, cnt=1):
        assert box[0].count(a) == cnt, (path, box[0].count(a), a[:90])
        box[0] = box[0].replace(a, b)
    fn(rep, box)
    open(path, "w", encoding="utf-8", newline="").write(box[0])


def proof(rep, box):
    # first paragraph
    rep("Credited derivative of our own {predid} ({predlabel}, blake3 round {Rn}, time_log2 {TLpred}, memory_log2_bytes {MTpredlog}, scalar score {SCpred}: the same search, plan method, success proof (Section 4) and experiments;",
        "Credited derivative of our own " + B3R6C + " (B3R6c, blake3 round {Rn}, time_log2 " + OLDTL + ", filed 10-16: this program with the earlier Section 4) and of our own {predid} ({predlabel}, blake3 round {Rn}, time_log2 {TLpred}, memory_log2_bytes {MTpredlog}, scalar score {SCpred}: the same search, plan method and experiments;")
    rep("the entry that introduced the supermartingale Lemma 2 of Section 4 and clause (d) of H1,", "the entry that introduced the hazard form of Lemma 2 and clause (d) of H1,")
    rep("The experiments and the proof of Section 4 are those of {pred8} and a2e94df7 with the new numbers.", "The experiments are those of {pred8} and a2e94df7 with the new numbers; Section 4 is rewritten (below).")
    rep("the generator, the ledger method, Section 4 and the experiments are a2e94df7's with these numbers.",
        "the generator, the ledger method and the experiments are a2e94df7's with these numbers.\n\nWhat changed against 1cf99082 (B3R6c; same step, rolled round body, generator, recovery circuit, 10-byte table entry with a 64-bit key, registers and experiments): Section 4 is rewritten as a first-collision proof (Lemma 2, Steps 2 to 5) and B and Tp are re-planned with it (Tp {oldTp} -> {Tp}, kappa {oldkappa} -> {kappa}, B {oldB} -> {B}); time_log2 " + OLDTL + " -> {TL}.")
    # section 5
    rep("Lemma 2 now proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish)", "Lemma 2 now proves the bound for F from the hazard alone (the first collision of the run and the detection delay, no conditioning on which trails finish)")
    rep("Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs, the Chernoff bounds and the cut count are proved in Section 4 for F", "Lemma 1, the lazy-sampling facts, the first-collision bound, the Chernoff bounds and the cut count are proved in Section 4 for F")
    # section 8
    rep("Credited to our own {pred8} and a2e94df7: the search, the plan method, Section 4, the experiments' form, the rolled step and the generator; this entry takes the machine plan of a2e94df7 to {Rw} rounds.",
        "Credited to our own 1cf99082 (B3R6c), {pred8} and a2e94df7: the search, the plan method, the experiments' form, the rolled step and the generator, and from 1cf99082 Lemma 1 and Steps 0, 1, 6 and 7 of Section 4; this entry takes the machine plan of a2e94df7 to {Rw} rounds.")
    rep("(the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding)", "(the floating-point bound only selects B and Tp; the printed rows do not depend on rounding)")
    t = box[0]
    i = t.index("## 4. Success probability")
    j = t.index("## 5.")
    sec4 = open("sec4_t9.md", encoding="utf-8").read()
    box[0] = t[:i] + sec4.rstrip("\n") + "\n\n" + t[j:]


def note(rep, box):
    rep("the search, the plan method, the proof of the success bound (Section 4, the supermartingale Lemma 2) and the experiments are those of a2e94df7 with the {Rw}-round numbers.",
        "the search, the plan method and the experiments are those of a2e94df7 with the {Rw}-round numbers. It is also our own B3R6c, " + B3R6C + " (time_log2 " + OLDTL + "), with Section 4 rewritten.")
    rep("## What changed against {pred8}\n", "## What changed against 1cf99082 (B3R6c)\n\nSection 4 is rewritten as a first-collision proof (Lemma 2, Steps 2 to 5; the detection delay is the main loss, {t_delay:.4f} of the probability) and B and Tp are re-planned with it: Tp {oldTp} -> {Tp}, kappa {oldkappa} -> {kappa}, B {oldB} -> {B}, certified P_F >= {Pcert}; time_log2 " + OLDTL + " -> {TL}. The step, rolled round body, generator, recovery circuit, 10-byte table entry, registers and experiments are unchanged.\n\n## What changed against {pred8}\n")
    rep("(a supermartingale over the evaluations, with no conditioning on which trails finish and no random U)", "(from the first collision of the run, with no conditioning on which trails finish and no random U)")
    rep("Lemma 2 v2 proves P_F", "Lemma 2 proves P_F")


def build(rep, box):
    rep("TL3 = 124.8123\nTL1 = 125.35348\nTL4 = 125.06000\n", "TL3 = 124.8123\nTL1 = 125.35348\nTL4 = 125.06000\nOLD = dict(TL='" + OLDTL + "', Tp=241, kappa=13, B=1365545272934000000000000000000000000)\n")
    rep('kfin = ls["nmax"] - 256\n', "")
    rep('    trails=ls["trails"], pk2=pk2, kappa=b.KAPPA_256, cmax=b.CMAX, kfin=kfin, nmax=ls["nmax"], theta=ls["theta"], emain=ls["main"], zst=ls["z"], zfrac=ls["z"] / (ls["trails"] ** 2 / 2), kap=ls["kap"], wfac=ls["w"],\n',
        '    trails=ls["trails"], pk2=pk2, kappa=b.KAPPA_256, cmax=b.CMAX,\n    t_coll=ls["collision"], t_delay=ls["delay"], t_own=ls["own_trail"], t_long=ls["long_partner"], t_age=ls["age_cap"], t_dist=ls["disturbance"], nbins=fm(22000), PPq=ls["hq"], keybits=64,\n')
    rep('    destroy=ls["collision_on_path"], epsn=b.EPS, longf=ls["long_finish"], others=sumloss - ls["main"], sumall=sumloss, tfull=tmax - 59,', '    sumall=sumloss, tfull=tmax - 59,')
    i = box[0].index("# ---- Lemma 2 v2 values")
    j = box[0].index("padded = _ceil")
    new = '''# ---- Lemma 2 values ----
import re as _re
from math import expm1, log1p, exp as _exp, ceil as _ceil
Pcert = _re.search(r"certified \\(exact rationals, 60-digit decimals\\) = ([\\d.]+)", appOut).group(1)
assert float(Pcert) >= 0.39
kk = ls["k"]; n2 = ls["n2"]; _kp = b.KAPPA_256; _pp = ls["p"]
hq = ls["hq"]; ql = ls["ql"]
pbin = -expm1(n2 * log1p(-_pp)) - n2 * _pp * _exp((n2 - 1) * log1p(-_pp))
ES = ql; EX = ql * (2 + _kp) * _exp(-_kp / 2) + hq * _pp * (1 + _kp); EJ2a = 2 * ql * hq; EJ2b = hq * _pp * (1 + _kp); EY = hq * _pp
assert abs(pbin + ES + EX + EJ2a + EJ2b + EY - pk2) < 1e-12 * pk2 + 1e-18, (pbin + ES + EX + EJ2a + EJ2b + EY, pk2)
Mnum = float(p["c"] + (1 << 48)); Qnum = float(Q)
assert 240 * Mnum <= Qnum
'''
    box[0] = box[0][:i] + new + box[0][j:]
    rep("V2 = dict(Pcert=Pcert, kk=kk, Hq=hq,", "V2 = dict(Pcert=Pcert, kk=kk, Hq=ls[\"hh\"],")
    rep("Mnum=Mnum, Qnum=Qnum, twoeps=2 * b.EPS,\n          oldTL='125.29018', oldTp=229, pred='8fbecd8a', padded", "Mnum=Mnum, Qnum=Qnum,\n          oldTL=OLD['TL'], oldTp=OLD['Tp'], oldkappa=OLD['kappa'], oldB=OLD['B'], pred='8fbecd8a', padded")
    # claim texts
    rep("by a supermartingale over the evaluations, with no conditioning on which trails finish and no fixed-size birthday step; (d) is the premise", "from the first collision of the run and the detection delay (no conditioning on which trails finish, no fixed-size birthday step); (d) is the premise")
    rep("(a supermartingale over the evaluations, no conditioning on which trails finish, the cut count bounded by a proved theorem;", "(the first collision of the run and the detection delay, no conditioning on which trails finish, the cut count bounded by a proved theorem;")
    rep("Credited derivative: our own 57174971 (the same search, plan method and proof, with a straight-line six-round step),", "Credited derivative: our own 1cf99082 (B3R6c: the same program, with the earlier Section 4), 57174971 (the same search and plan method, with a straight-line six-round step),")
    # dependencies
    rep('deps = [\n    {"submissionId": PRED["id"],', 'deps = [\n    {"submissionId": "' + B3R6C + '",\n     "rationale": "Our own B3R6c (blake3 round 6, time_log2 ' + OLDTL + '), filed 10-16: the same program. Taken from it: the target form, the rolled round body, the circuit generator, the search, handlers, recovery circuit, 10-byte table entry, register file, ledger method, the experiments, and Lemma 1 and Steps 0, 1, 6 and 7 of Section 4. Changed: Section 4 (Lemma 2, Steps 2 to 5, rewritten as a first-collision proof), and B, Tp and the age cap (kappa 14) re-planned with it.",\n     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."},\n    {"submissionId": PRED["id"],')
    rep("the search, the plan method, the success proof (Section 4), the experiments and the ledger method of this entry are those of 57174971.", "the search, the plan method, the experiments and the ledger method of this entry are those of 57174971.")
    rep("the plan method and Section 4 (Lemma 2 v2) of this entry are those of a2e94df7", "the plan method of this entry are those of a2e94df7")


edit("proof_t8.md", proof)
edit("note_t8.md", note)
edit("build_all8.py", build)
print("ok")
