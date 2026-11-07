"""Patches build_all.py (copied from ../pivot1) into the Lemma 2 v2 build of the r3 entry.  Run once: python3 -B mk_v2_build.py"""
import re, os
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "..", "pivot1", "build_all.py"), encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a))
    s = s.replace(a, b)


def sub1(pattern, repl, flags=re.S):
    global s
    s, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    assert n == 1, pattern[:70]


rep("import sys, json, os\nfrom math import log2, exp, log\n", "import sys, json, os, string, re as _re\nfrom math import log2, exp, log, ceil, expm1, log1p, comb\n")
# header block: TL, cut model, eps
a = s.index('N = lg["total"]; TL = 124.8123')
b = s.index("rows_R = {}")
s = s[:a] + '''N = lg["total"]
TLraw = log2(N / 638)
TL = ceil(TLraw * 100000) / 100000
assert TL >= TLraw and TL - TLraw < 1e-5
parts = lg["parts"]
pk2 = ls["cut_halt"]
L = p["L"]; Q = p["Q"]
sumloss = ls["sum"]
assert ls["P_lower"] >= 0.39
_orig = b._lossq
sens = []
for e in (0.01, 0.05, 0.10, 0.25):
    b._lossq = (lambda r: (lambda *a, **k: _orig(*a, **dict(k, rate=r))))(1 - e)
    b._B.clear()
    pe = b.plan(256); lge = b.ledger(pe)
    sens.append((e, log2(lge["total"] / lg["total"]), pe["Tp"]))
b._lossq = _orig; b._B.clear()
assert b.plan(256)["B"] == p["B"]
sens_txt = "; ".join("%.4f bit for eps = %.2f (Tp %d)" % (x[1], x[0], x[2]) for x in sens)
sens_short = ", ".join("%.4f bit for eps = %.2f" % (x[1], x[0]) for x in sens)
eps = 0.0
''' + s[b:]
rep('assert lsR["P_lower"] >= 0.39, (R, lsR["P_lower"])', 'assert lsR["P_lower"] >= 0.39, (R, lsR["P_lower"])')
rep('log2setup=log2((b.SETUP_FIXED + lg["gen"]) / 638)', 'log2setup=log2((b.SETUP_FIXED + lg["gen"]) / 638)')
# vals: remove the old cut-model entries, add the new ones
rep("TL=TL, slack=TL - log2(N / 638),", "TL=TL, slack=TL - TLraw,")
rep('M=b.INFLIGHT, tailages=exp(-256 * (b.INFLIGHT / 256 - 1 - log(b.INFLIGHT / 256))), f1=f1, trails=ls["trails"], mu=mu, pk0=pk[0], pk1=pk[1], pk2=pk[2], pk3=1 - sum(pk),\n',
    'trails=ls["trails"], pk2=pk2, kappa=b.KAPPA_256, cmax=b.CMAX, nmax=ls["nmax"], theta=ls["theta"], emain=ls["main"], zst=ls["z"], kap=ls["kap"], wfac=ls["w"],\n    destroy=ls["collision_on_path"], epsn=b.EPS, longf=ls["long_finish"], twoeps=2 * b.EPS, sens=sens_txt, sens_short=sens_short, kb=p["kb"], fb=p["fb"], keytop=p["D"] + p["kb"] - 1,\n')
rep("    allow=1.5e-4 / f1, d1=(f1 - 1.5e-4) * slope, d2=(2 * f1 - 1.5e-4) * slope, slope=slope, cutdef=cutdef, Uratio=U, log2inside=log2(ls[\"inside_trail\"]), inside=ls[\"inside_trail\"],\n", "")
rep('log2keys=56 + log2(p["Tp"]),', 'log2keys=p["kb"] + log2(p["Tp"]),')
sub1(r"    sumloss=sumloss, Pl=ls\[\"P_lower\"\], margin=ls\[\"P_lower\"\] - 0\.39, eps=eps, eps_cost=0\.5 \* log2\(1 / 0\.99\),",
     '    sumloss=sumloss, Pl=ls["P_lower"], margin=ls["P_lower"] - 0.39, eps=eps, eps_cost=0.5 * log2(1 / 0.99),')
# Lemma 2 v2 values + need()
v2 = '''
# ---- Lemma 2 v2 values ----
appOutText = appOut
Pcert = _re.search(r"certified \\(exact rationals, 60-digit decimals\\) = ([\\d.]+)", appOutText).group(1)
assert float(Pcert) >= 0.39
CM = b.CMAX
kk = ls["k"]; n2 = kk + 256 + CM; _kp = b.KAPPA_256; _pp = exp(-_kp)
_q = float(ls["trails"]); _l2n = float(L * L / (1 << 256)); _s0 = _q * _q / 2
hq = _s0 * _l2n; ql = _q * _l2n
pbin = 1 - sum(comb(n2, j) * _pp ** j * exp((n2 - j) * log1p(-_pp)) for j in range(CM + 1))
ES = ql; EX = ql * (2 + _kp) * exp(-_kp / 2) + hq * _pp * (1 + _kp); EJ2a = 2 * ql * hq; EJ2b = hq * _pp * (1 + _kp); EY = hq * _pp
assert abs(pbin + ES + EX + EJ2a + EJ2b + EY - pk2) < 1e-12 * pk2 + 1e-18, (pbin + ES + EX + EJ2a + EJ2b + EY, pk2)
Mnum = float(p["c"] + (1 << 48)); Qnum = float(Q)
assert 240 * Mnum <= Qnum
_tiny = [Qnum * 2 ** 16 / 2.0 ** 256, Qnum * kk / 2.0 ** 256, kk * kk * float(L) / 2.0 ** 256, exp(-300 + (exp(5) - 1) * hq), 2.0 ** -99]
assert max(_tiny) < 2.0 ** -96 * 1.0001 and sum(_tiny) < 2.0 ** -90, _tiny
V2 = dict(Pcert=Pcert, kk=kk, Hq=hq, pbin=pbin, ES=ES, EX=EX, EJ2a=EJ2a, EJ2b=EJ2b, EY=EY, Mnum=Mnum, Qnum=Qnum)
vals.update(V2)


def need(text, label):
    names_ = {f[1] for f in string.Formatter().parse(text) if f[1]}
    missing = sorted(n for n in names_ if n not in vals)
    assert not missing, (label, missing)


'''
rep('tpl = open(os.path.join(HERE, "proof_t.md"), encoding="utf-8").read()\n', v2 + 'tpl = open(os.path.join(HERE, "proof_t.md"), encoding="utf-8").read()\nneed(tpl, "proof_t")\n')
# H1, H2, H3 dicts
a = s.index("H1 = dict(")
b2 = s.index("H3 = dict(")
H1new = '''H1 = dict(
    id="H1-random-function-model", role="score-critical",
    statement=("Model premise, four clauses. Let F be a uniformly random function from 256-bit values to 256-bit values. For the fixed target, the probability that the single attempt of the search succeeds, with the walk g(x) = f(x) XOR q (f(x) = the complete 3-round digest of the 64-byte message 0^32 || x, q the fixed digest-plane mask of the generated circuit), "
               "is at least the probability P_F, over the fresh word r and a uniformly random F, that the same search succeeds when every evaluation of g is replaced by F (lazy sampling). Clauses: (a) distinct evaluated inputs collide with probability 2^-256, uniform and independent outputs; (b) the iterates from r + t have the first-collision law of a random mapping; "
               "(c) a point is a distinguished point (low 32 bits zero and the next 90 bits below %d) with probability %d / 2^122, independently of the collision events; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of g; given the whole history of the run and which later outputs are distinguished points, a fresh evaluation equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard of F). "
               "Proof.md Section 4 (Lemma 2 v2) proves P_F >= %s for F from the hazard alone, by a supermartingale over the evaluations, with no conditioning on which trails finish and no fixed-size birthday step; (d) is the premise that g has that hazard. This is a comparison of two success events, not a statement about the entropy of r. Nothing else in the success bound is heuristic." % (Tp, Tp, Pcert)),
    scope=("The fixed target blake3-r3-prefix-v1 restricted to 64-byte messages 0^32 || x, the fixed mask q, the 2^128-scale evaluation of g along about %d trails of mean length 2^%.2f started from r + t, 256 trails at a time. Not claimed for other messages, other round counts, or evaluations beyond this scale." % (round(ls["trails"], -2), log2(L))),
    extrapolation=("Declared and not proved: an assumption, no proof is known. The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. The organizer experiments bsrho-n18 and proj-k0-w256 run this program on the real target at reduced width (the search at width 18) and at full width for 2048 points with 21-bit projections; they are program checks, no number of the claim is estimated from their counts, and no sampling premise is used. "
                   "Extrapolation from these sizes to width 256 and 2^128 evaluations is by the premise only. If the collision hazard is (1 - eps) / N instead of 1 / N (clause (d), or a deficit eps in clause (a)), the plan of this program needs, to restore 0.39: %s." % sens_short),
    evidence_ids=["experiment:bsrho-n18", "experiment:proj-k0-w256", S4, S5, S6],
    limitations=("A model premise about one fixed function, not a theorem: on the target the run is a deterministic function of r. It cannot be tested at width 256; the experiments reach width 18 and 21-bit projections of 2048 points per trial and do not measure collision structure at 2^128 evaluations. "
                 "The bound has no margin above 0.39 (B is the least multiple of 10^24 that reaches it), so any hazard deficit is repaired by extra time, priced above: %s." % sens_txt),
)
'''
s = s[:a] + H1new + s[b2:]
# H3 texts: nothing to change; restrictions
a = s.index('R.append("Success probability at least 0.39 holds under the model premise H1')
b3 = s.index('R.append("The declared experiments run this program')
s = s[:a] + '''R.append("Success probability at least 0.39: Lemma 2 of proof.md Section 4 proves it for a uniformly random function from the lazy-sampling hazard (a supermartingale over the evaluations, no conditioning on which trails finish, the cut count bounded by a proved theorem; bound %.5f, exact certificate %s in Appendix A, none spare); H1, score-critical (clauses (a) to (d), declared and not proved), says the real attempt succeeds at least as often. Nothing else in the bound is heuristic. If the hazard were (1 - eps) / N the plan needs extra time: %s." % (ls["P_lower"], Pcert, sens_short))
''' + s[b3:]
rep('claim = {"schema_version": 3,', 'claim = {"schema_version": 3,')
rep('"heuristics": [H1, H2, H3]', '"heuristics": [H1, H3]')
# dependencies
a = s.index("deps = [")
b4 = s.index('w(os.path.join(PKG, "dependencies.json")')
old_deps = s[a:b4]
new62 = '''deps = [
    {"submissionId": "62cfd777-5613-463f-b561-e2340e00e528",
     "rationale": "Our own B3R3PV (time_log2 124.8123), filed 10-14, the filed version of this entry: the program, circuit generator (pivot full adders), mask walk, ledger method, experiments, certificates and every section of this entry are those of 62cfd777. Changed in this revision (v2): Section 4 (Lemma 2) is replaced by Lemma 2 v2 (a theorem about the random function with no premise besides H1; the heuristic H2 withdrawn; the Chernoff tail certified in exact arithmetic by Appendix A) answering the findings of the ruling on our B3R7 (1cd0dd3b) and of the ruling on our round-4 entry 41b32afc (the same Lemma 2), H1 gets the adaptivity clause (d), and B and Tp are re-planned (time_log2 %s)." % TL,
     "evidence": "proof.md first paragraph, Section 4 and Section 9, and Appendix A."},
'''
s = s[:a] + new62 + old_deps[len("deps = [\n"):] + s[b4:]
# note vals
rep("vals.update(gain=124.91252 - TL,", "vals.update(gain=124.91252 - TL,")
rep('epsp=100 * eps,', 'epsp=100 * eps,')
open(os.path.join(HERE, "build_all.py"), "w", encoding="utf-8", newline="\n").write(s)
print("ok", len(s))
