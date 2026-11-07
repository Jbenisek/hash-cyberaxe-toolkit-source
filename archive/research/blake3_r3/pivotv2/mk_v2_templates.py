"""Lemma 2 v2 rebuild of the r3 pivot entry (62cfd777): rewrites proof_t.md, note_t.md from the filed templates (kept in ../pivot1) and the r4 v2 sections.
Run once: python3 -B mk_v2_templates.py   (reads ../pivot1/proof_t.md, ../pivot1/note_t.md, ../../blake3_r4/b4e/proof_t.md; writes proof_t.md, note_t.md here)."""
import os, re, sys, json, glob
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(RES, "lemma_v2"))
sys.dont_write_bytecode = True
import text_v2_blake3 as T

old = open(os.path.join(HERE, "..", "pivot1", "proof_t.md"), encoding="utf-8").read()
r4 = open(os.path.join(RES, "blake3_r4", "b4e", "proof_t.md"), encoding="utf-8").read()


def sub1(pattern, repl, text, flags=re.S):
    new, n = re.subn(pattern, lambda m: repl, text, count=1, flags=flags)
    assert n == 1, pattern[:70]
    return new


def rep(text, a, b, cnt=1):
    assert text.count(a) == cnt, (a[:70], text.count(a))
    return text.replace(a, b)


# ---------- section 4 body (from r4 b4e) ----------
i = r4.index("Lemma 2 (for the random function F; no premise).")
j = r4.index("\n## 5. Premise H1 and its evidence")
sec4 = r4[i:j].rstrip("\n")
sec4 = rep(sec4, "CMAX = 1 (the program halts when a second trail would be cut)", "CMAX = 2 (the program halts when a third trail would be cut)")
sec4 = rep(sec4, "    P0 = 256^2 B (B - 1) / 2,   CUT = M Q + min( (M - h) Q, z* L^2 / 257 + S Q ).", "    P0 = 256^2 B (B - 1) / 2,   CUT = CMAX (M Q + min( (M - h) Q, z* L^2 / 257 + S Q )) = 2 (M Q + min( (M - h) Q, z* L^2 / 257 + S Q )).")
sec4 = rep(sec4, "P_cut = P(Binomial(k + 257, p) >= 2) + E_S", "P_cut = P(Binomial(k + 258, p) >= 3) + E_S")
sec4 = rep(sec4, "P_long = (k + 257) e^(-c/L) S / L,", "P_long = (k + 258) e^(-c/L) S / L,")
sec4 = rep(sec4, "the run lasts Q evaluations; K <= 1 (K the number of cut trails);", "the run lasts Q evaluations; K <= 2 (K the number of cut trails);")
# 5.1 (c)
a = sec4.index("(c) the cut trail (K <= 1 on A;")
b = sec4.index("For the remaining trails (free trails that are finished or open")
c_new = ("(c) the cut trails (K <= CMAX = 2 on A; a cut trail that is colliding is already in (b)). Take one of them, T0. As y: (iii) fails for all its y, at most M Q pairs. As t: its evaluations are fresh with xi = 0 and conditions (i) to (iii) concern y only, so a pair (y, t) is lost through t only by (iv) second part, a(t) + d(y) > c. For a y on a free finished trail with d(y) = d, the evaluations of T0 with age above c - d are at most d + S (its ages are below M), so these pairs are at most the sum of d(y) + S over y, which is at most the sum over free finished trails of X(m) + S Q, X(m) = m (m + 1) / 2; and also at most (M - h) Q (the t of age above h, each with at most Q partners; for a(t) <= h the loss needs d(y) > c - h and is charged to y in (g)). Since 257 X(m) <= z(m), on Z <= z* L^2 each cut trail costs at most M Q + min((M - h) Q, z* L^2 / 257 + S Q), and the at most CMAX = 2 cut trails cost at most CUT = CMAX (M Q + min((M - h) Q, z* L^2 / 257 + S Q)) (each cut trail is bounded on its own; no sharing of the sum is used).\n")
sec4 = sec4[:a] + c_new + sec4[b:]
sec4 = rep(sec4, "(the cut trail, which may share a block with one of them, is charged in (c))", "(the cut trails, which may share a block with one of them or with each other, are charged in (c))")
sec4 = rep(sec4, "(the second one halts the run)", "(the third one halts the run)")
sec4 = rep(sec4, "and two successes before that failure mean two successes among the first n2 = k + 257 trials:\n    P(K_A >= 2, N1 <= k - 1) <= P(Binomial(n2, p) >= 2) = 1 - (1 - p)^n2 - n2 p (1 - p)^(n2 - 1)",
           "and CMAX + 1 = 3 successes before that failure mean three successes among the first n2 = k + 256 + CMAX = k + 258 trials (three successes and at most k + 255 failures):\n    P(K_A >= 3, N1 <= k - 1) <= P(Binomial(n2, p) >= 3) = 1 - (1 - p)^n2 - n2 p (1 - p)^(n2 - 1) - C(n2, 2) p^2 (1 - p)^(n2 - 2)")
sec4 = rep(sec4, "So P(K >= 2) <= P(K_A >= 2, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 2) + E_S",
           "So P(K >= 3) <= P(K_A >= 3, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 3) + E_S")
sec4 = rep(sec4, "P(Binomial(n2, p) >= 2) = {pbin:.3e} and P_cut", "P(Binomial(n2, p) >= 3) = {pbin:.3e} and P_cut")
sec4 = rep(sec4, "the complement of A, whose parts are: K >= 2 (P_cut)", "the complement of A, whose parts are: K >= 3 (P_cut)")
sec4 = rep(sec4, "Early halts: the second cut (P_cut, counted once)", "Early halts: the third cut (P_cut, counted once)")
sec4 = rep(sec4, "(finished trails <= N1 + collisions, at most one cut restart), and k + 257 >= q + 256 + H + 1:", "(finished trails <= N1 + collisions, at most CMAX = 2 cut restarts), and k + 258 >= q + 256 + H + 2:")
sec4 = rep(sec4, "(second cut, table full, stage-1 budget, key false match)", "(third cut, table full, stage-1 budget, key false match)")
chk = sec4.replace("second part", "").replace("second one", "")
assert "second" not in chk, [m.group(0) for m in re.finditer(r".{40}second.{40}", chk)]
assert ">= 2" not in sec4 and "k + 257" not in sec4, [m.group(0) for m in re.finditer(r".{40}(>= 2|k \+ 257).{40}", sec4)]
sec4 += "\n\nRemark on CMAX = 2 (the only difference from the CMAX = 1 form of Lemma 2 v2 used in our later entries): every use of CMAX in the proof is explicit. The cut trails enter only through K <= CMAX on A (Step 5), through CUT = CMAX (M Q + min(...)) (5.1 (c), each cut trail bounded on its own), through the number of trials n2 = k + 256 + CMAX and the threshold CMAX + 1 in Step 6 (i), through the term K_B >= 1 (which does not depend on CMAX) and through the restarts counted in P_long (Step 7). Setting CMAX = 1 gives the text of the later entries."

# ---------- section 4 head, section 5 H1 paragraph ----------
h1i = r4.index("Heuristic H1 (model premise, Section 5).")
h1j = r4.index("\n\nLemma 1 (a statement about g itself")
h1_intro = r4[h1i:h1j].strip()
s5i = r4.index("H1 is the model premise of Section 4.")
s5j = r4.index("\nEvidence that the program is right")
h1_sec5 = r4[s5i:s5j].strip()
h1_sec5 = rep(h1_sec5, "Clause (d) replaces the fixed-U birthday step of the earlier Lemma 2, which the judges asked to be either proved or declared (41b32afc, finding F1-adaptive-finished-trail-conditioning, aggregate heuristic H4);",
              "Clause (d) replaces the fixed-U birthday step of the earlier Lemma 2 of this entry (62cfd777), which the judges asked to be either proved or declared in their ruling on our round-4 entry 41b32afc (same Lemma 2; finding F1-adaptive-finished-trail-conditioning, aggregate heuristic H4);")

t = old
t = sub1(r"Heuristic H1 \(model premise, Section 5\)\..*?\n(?=Lemma 1 \(a statement)", h1_intro + "\n\n", t)
assert "H2 (a) the age" not in t
m1 = re.search(r"\nLemma 2 \(for the random function F, under H2\)", t)
m2 = t.index("\n## 5. Premise H1 and its evidence")
t = t[:m1.start() + 1] + sec4 + "\n" + t[m2:]
t = sub1(r"H1 is the model premise of Section 4\..*?\n(?=Evidence that the program is right)", h1_sec5 + "\n", t)
t = rep(t, "one that lowers it by eps costs the table of Section 4.", "one that lowers it by eps costs the extra time of Section 4.")
# section 7 last paragraph
t = sub1(r"and Tp = \{Tp\} is the largest integer for which the table-capacity bound of Section 4 stays below 2\^-40 \(Appendix A computes both\)\.",
         "and Tp = {Tp} is the plan of Appendix A: the mean number of trails is the largest that the table holds with a capacity tail below 2^-40, and Tp is the largest integer (found by bisection; any Tp is a valid plan) for which the success bound of Section 4 reaches the planning target 0.390000001 at that mean (Appendix A computes both and certifies P_F >= 0.39 in exact arithmetic).", t)
# section 8
t = sub1(r"The premises of this entry are: H1 \(the model premise of Section 4, score-critical\), H2 \(the named approximations of Lemma 2, supporting\), H3 \(the 1,024-register machine convention and the 36-byte instruction charge, score-critical\)\.",
         "The premises of this entry are: H1 (the model premise of Sections 4 and 5, clauses (a) to (d), score-critical) and H3 (the 1,024-register machine convention and the 36-byte instruction charge, score-critical). The cut-count heuristic H2 and the age-independence approximation of the filed text are withdrawn: Lemma 2 v2 proves them.", t)
# intro: revision note + derivative sentence
t = sub1(r"\n## 1\. Target and relation",
         "\nRevision note. This text revises our filed 62cfd777-5613-463f-b561-e2340e00e528 (B3R3PV, 124.8123): Section 4 (Lemma 2) is replaced by Lemma 2 v2 (a theorem about the random function F with no premise besides H1; the heuristic H2 of the filed text, which stated that the number of cut trails is Poisson and that the 256 trail ages are independent exponentials, is withdrawn and replaced by the proved Step 5.2 and Step 6; the Chernoff quantile is an upper bound certified in exact arithmetic by Appendix A; H1 gets clause (d), the adaptivity clause); the plan is re-run on the new bound (Tp {Tp} against 177, time_log2 {TL} against 124.8123); the target, the step, the generator, the program's search and every operation count are those of the filed entry. Section 9 answers the findings of the judges' ruling on 1cd0dd3b (whose Lemma 2 and H2 were the same text) by id.\n\n## 1. Target and relation", t)
t = sub1(r"^# blake3-r3: plain birthday with 256 bit-sliced lanes, pivot full adders and a mask walk\n\nCredited derivative of our own 0a9640ed",
         "# blake3-r3: plain birthday with 256 bit-sliced lanes, pivot full adders and a mask walk\n\nCredited derivative of our own 62cfd777-5613-463f-b561-e2340e00e528 (blake3 round 3, 124.8123: this program; this entry replaces its Lemma 2 by Lemma 2 v2 and re-plans, see the revision note below), of our own 0a9640ed", t, flags=re.S)
t = rep(t, "Everything else is the program of 0a9640ed and 3356413f:", "Everything else is the program of 62cfd777, 0a9640ed and 3356413f:")

# ---------- section 9 ----------
DS = {}
for rid in ("1cd0dd3b", "41b32afc"):
    p = glob.glob(os.path.join(RES, "dossiers", rid + "*", "review/reports/tracks/blake3-pareto/judge-dossier.json"))[0]
    DS[rid] = json.load(open(p)), json.load(open(p.replace("judge-dossier", "aggregate")))
cfg = dict(rounds=3, own=None, pred="62cfd777", old_tl="124.8123", old_tp=177)
T.configure_answers(cfg)
cfg["round_ans"] = "Text only: the validation sentences of this 3-round entry say 3 rounds (blake3(M(x), 3)), the target's round count; unchanged by this revision."
cfg["label_ans"] = "Text only: the main-loop row of Appendix A of this entry is labelled B * 17275, equal to the body it computes; unchanged by this revision."
A = dict(T.ANS)
A["POIS"] = ("Confirmed. H2 is withdrawn (removed from claim.json, the proof, the restrictions and the note): no premise about the cut count remains, and the age-independence approximation of the filed Lemma 2 (the 256 ages independent exponentials) is gone too (Step 5.2 replaces it by i.i.d. lottery blocks without selection). Theorem of proof Section 4, Step 6: K = K_A + K_B; K_A (cut trails whose first c evaluations are fresh) is at most the number of successes of an i.i.d. Bernoulli(p) trial sequence before failure number k + 256, so P(K_A >= 3, N1 <= k - 1) <= P(Binomial(k + 258, p) >= 3) (CMAX = 2 in this entry: the program halts at the third cut trail; the proof is written with CMAX explicit); K_B (cut trails that join another path or close a cycle) needs one of five root events, each bounded by an expected count from the lazy-sampling hazard. P_cut = {pk2:.2e}; the finite support of K is no longer in conflict with any statement.")
A["POISX"] = ("Answered by the withdrawal of H2: no cut-count law is assumed any more, K is bounded by the theorem of proof Section 4, Step 6 for the random function F, so there is no cut-count premise left for an experiment to observe. What stays declared is H1 (the comparison of the real function with F, clauses (a) to (d)).")
A["MGF"] = ("Confirmed and fixed. The filed `_zq` of this entry (62cfd777) used the same midpoint sum. It is replaced by the trapezoid sum of the same convex integrand, which is an upper bound of the integral (proof Section 4, Step 5.3); the block-length coupling, the shift and the atom at the cap are bounded explicitly and the program multiplies by 1 + 2^-30. Appendix A (`certify`) recomputes z*, w and the whole bound in exact rationals and 60-digit decimals with outward rounding and asserts P_F >= 0.39 (certified value {Pcert}). B is re-planned on the new bound (Tp {Tp} against 177, time_log2 {TL} against 124.8123 of the filed 62cfd777).")
A["H3"] = ("Not a Lemma 2 matter and unchanged: the machine convention H3 and the ledger it supports are as in the filed entry (this revision changes no operation count of the main loop; the program differs only in the success-bound functions `_zq`, `_lossq`, `_b256`, `plan`, `loss`, which set Tp and B, and the ledger rows that follow from them).")
A["H1"] = ("Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.")
A["ADAPT"] = ("Answered by Lemma 2 v2: the fixed-size birthday step (a fixed number U of evaluations on finished trails) is gone. Step 4 is a supermartingale over the evaluations with the hazard (L1) alone, no conditioning on which trails finish; the facts it needs about the adaptivity of the program are declared as clause (d) of H1 (proof Section 5), the premise that g has the lazy-sampling hazard of F. The heuristic H4 of that ruling is therefore no longer an unproved step: Lemma 2 is a theorem about F and (d) is stated openly.")


def classify41(fid):
    if fid.startswith("F1-adaptive"):
        return "ADAPT"
    if fid in ("F-COST-REGISTERS", "F-COST-TIGHT-MEMORY", "EXP-F3"):
        return "H3"
    return "H1"


def block(rid, own_txt):
    d, agg = DS[rid]
    out = ["Ruling on %s%s: status %s, reasons %s." % (rid, own_txt, agg.get("status"), ", ".join(agg.get("reasons", [])))]
    for lane, rv in d["reviews"].items():
        for f in rv.get("findings", []):
            k = T.classify(f["id"]) if rid == "1cd0dd3b" else classify41(f["id"])
            a = A[k] if k in A else T.ANS[k]
            if k == "ROUND":
                a = cfg["round_ans"]
            elif k == "LABEL":
                a = cfg["label_ans"]
            out.append("- %s/%s (%s): %s" % (lane, f["id"], f["severity"], a))
    hs = d.get("heuristic_assessments", {})
    names = sorted({n.split("/heuristic/")[-1] for n in hs})
    for hn in names:
        if hn.startswith("H2"):
            out.append("- heuristic assessments %s (all lanes that rated it): H2 is withdrawn, see the answer to the H2 findings above; nothing remains to be rated." % hn)
        elif hn.startswith("H4"):
            out.append("- heuristic assessments %s (lane_cryptanalysis, unsupported): answered as the F1-adaptive-finished-trail-conditioning finding above (Step 4 and clause (d) of H1)." % hn)
        else:
            out.append("- heuristic assessments %s: unchanged (declared premise, see the H1 / H3 answers above)." % hn)
    if rid == "1cd0dd3b":
        out.append("- lane_adjudicator and lane_defender on lane_cryptanalysis/F1-mgf-midpoint-not-upper-bound and lane_cryptanalysis/F2-exact-poisson-cut-law-false (both confirmed): answered as the two findings above (Step 5.3 and Step 6).")
    return "\n".join(out)


head = ("Revision of our own 62cfd777 (B3R3PV, 124.8123, filed 10-14; no ruling of its own yet). The success proof (Section 4, Lemma 2) is replaced by Lemma 2 v2, a theorem about the random function with no premise besides H1 (the cut-count heuristic H2 and the independent-ages approximation of the filed text are withdrawn, the Chernoff tail is an upper bound certified in exact arithmetic by Appendix A); the program changes only in the success-bound functions (`_zq`, `_lossq`, `_b256`, `plan`, `loss`; the generator, the step and the search are unchanged); B and Tp are re-planned (time_log2 {TL} against 124.8123, Tp {Tp} against 177); the cut limit CMAX = 2 of the filed program is kept and handled exactly by the proof (Step 6). "
        "The findings of the ruling on our B3R7 1cd0dd3b (its Lemma 2 and its heuristic H2 are the same text as the filed text of this entry) are answered here by id, and so are the findings of the ruling on our round-4 entry 41b32afc (the same Lemma 2 of the filed text). ")
resp = head + "\n" + block("1cd0dd3b", " (our B3R7, the sibling entry whose Lemma 2 and H2 are the same text)") + "\n\n" + block("41b32afc", " (our round-4 entry B3R4b, the same Lemma 2 of the filed text)") + "\n"
t = sub1(r"\n## Appendix A\.", "\n## 9. Response to the findings of the judges' rulings\n\n" + resp + "\n## Appendix A.", t)
open(os.path.join(HERE, "proof_t.md"), "w", encoding="utf-8", newline="\n").write(t)
print("H2 contexts in proof template:", [m.group(0) for m in re.finditer(r".{30}H2.{30}", t)][:20])

# ---------- note ----------
n = open(os.path.join(HERE, "..", "pivot1", "note_t.md"), encoding="utf-8").read()
n = rep(n, "## What this entry is\n\nA credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c",
        "## What this entry is\n\nA revision of our own filed 62cfd777-5613-463f-b561-e2340e00e528 (B3R3PV, 124.8123): same program, search and ledger, with the success-probability proof (Section 4, Lemma 2) replaced by Lemma 2 v2, a theorem about the random function with no premise besides H1 (heuristic H2 of the filed entry withdrawn, tail certified in exact arithmetic), and B and Tp re-planned (time_log2 {TL} against 124.8123). It is a credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c")
n = rep(n, "3. The success argument is restated for the judges' rulings on the earlier entries: the score-critical premise H1 compares the fixed target with a uniformly random function (success of the single attempt on the target is at least success against a random function, over r and F); the approximations used in the random-function computation (independent exponential ages, Poisson cut count, linear cut loss, geometric lengths) are a separate named heuristic H2; experiments are reported as program checks with no inference drawn from counts; every term of the ledger is enforced by a halt and printed by the program.",
        "3. The success argument is restated for the judges' rulings: the score-critical premise H1 compares the fixed target with a uniformly random function (success of the single attempt on the target is at least success against a random function, over r and F; clauses (a) to (d), (d) being the adaptivity clause); Lemma 2 v2 proves the bound for the random function with no further premise (the independent-ages approximation, the Poisson cut count and the linear cut loss of the filed entry are gone: Steps 5.2, 5.3 and 6 of the proof); experiments are reported as program checks with no inference drawn from counts; every term of the ledger is enforced by a halt and printed by the program.")
n = rep(n, "(the proof bounds {Pl:.4f} under H1 and H2)", "(the proof bounds {Pl:.5f}, exact certificate {Pcert}: Lemma 2 v2 for the random function, no premise besides H1)")
n = rep(n, " H2 (supporting): the named approximations of Lemma 2.", " There is no H2: the filed entry's cut-count heuristic is withdrawn (Lemma 2 v2 proves the cut count).")
n = rep(n, "a deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits, and eps up to {eps:.4f} is absorbed by the margin.", "a hazard (1 - eps) / N instead of 1 / N (clause (d)) or a deficit eps in the pair-collision rate costs extra time: {sens_short}.")
nresp = "## Response to the findings of the judges' rulings (1cd0dd3b, and 41b32afc as the same Lemma 2)\n\n" + resp
n = rep(n, "\n## Generator peak memory", "\n" + nresp + "\n## Generator peak memory")
open(os.path.join(HERE, "note_t.md"), "w", encoding="utf-8", newline="\n").write(n)
print("note template bytes", len(n.encode()))
