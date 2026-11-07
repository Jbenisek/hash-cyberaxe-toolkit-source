"""Builds build_all9.py of B3R7d from build_all8.py (exact-match edits)."""
s = open("build_all8.py", encoding="utf-8", newline="").read()
assert "\r" not in s


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("of the blake3-r7 entry B3R7b (rolled round body)", "of the blake3-r7 entry B3R7d (rolled round body)")
rep("python -B build_all.py", "python -B build_all9.py")
rep('kfin = ls["nmax"] - 256\n', "")
# vals: lines with the old lemma values
i = s.index('    trails=ls["trails"], pk2=pk2,')
j = s.index('    kb=p["kb"], fb=p["fb"]')
s = s[:i] + '    trails=ls["trails"], pk2=pk2, kappa=b.KAPPA_256, cmax=b.CMAX, tfull=tmax - 59, sens=sens_txt, sens_short=sens_short, k10=9 * pk2, sparereq=b.SPARE,\n' + s[j:]
rep('    sumloss=sumloss, Pl=ls["P_lower"],', '    sumloss=sumloss, t_coll=ls["collision"], t_delay=ls["delay"], t_own=ls["own_trail"], t_long=ls["long_partner"], t_age=ls["age_cap"], t_dist=ls["disturbance"], nbins=fm(22000), PPq=ls["hq"], keybits=64,\n    Pl=ls["P_lower"],')
# the Lemma 2 block
i = s.index("# ---- Lemma 2 v2 values")
j = s.index("vals.update(V2)")
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
padded = _ceil(tmax / 4) * 32 + _ceil(tmax / 16) * 32; padx = padded - 10 * tmax
_memfit = mem + padx
termextra = 3800 + 3 * tmax
slackops = int(N * (2.0 ** (TL - TLraw) - 1))
lblbody = fm(lg["parts"]["main"] // p["B"])
V2 = dict(Pcert=Pcert, kk=kk, Hq=ls["hh"], pbin=pbin, ES=ES, EX=EX, EJ2a=EJ2a, EJ2b=EJ2b, EY=EY, Mnum=Mnum, Qnum=Qnum,
          oldTL='125.29113', oldTp=228, pred='a2e94df7', padded=fm(padded), padx=padx, memfit=fm(_memfit), termextra=fm(termextra), slackops=fm(slackops), lblbody=lblbody, body=body)

'''
s = s[:i] + new + s[j:]
rep('open(os.path.join(HERE, "proof_t8.md")', 'open(os.path.join(HERE, "proof_t9.md")')
rep('open(os.path.join(HERE, "note_t8.md")', 'open(os.path.join(HERE, "note_t9.md")')
# claim texts
rep("by a supermartingale over the evaluations, with no conditioning on which trails finish and no fixed-size birthday step; (d) is the premise", "from the first collision of the run and the detection delay (no conditioning on which trails finish, no fixed-size birthday step); (d) is the premise")
rep("(a supermartingale over the evaluations, no conditioning on which trails finish, the cut count bounded by a proved theorem;", "(the first collision of the run and the detection delay, no conditioning on which trails finish, the cut count bounded by a proved theorem;")
rep("Credited derivative: our own 1cd0dd3b (the same search, plan method and proof, with a straight-line seven-round step),", "Credited derivative: our own a2e94df7 (B3R7c, the same program with the earlier Section 4), 1cd0dd3b (the same search and plan method, with a straight-line seven-round step),")
# dependencies
rep('deps = [\n    {"submissionId": "1cd0dd3b-eb60-4572-a75f-937cd771ec4a",',
    'deps = [\n    {"submissionId": "a2e94df7-bff4-4461-ad40-7f75930cb241",\n     "rationale": "Our own B3R7c (time_log2 125.29113), filed: the program of this entry. Taken from it: the target form, the rolled seven-round step, the generator, the search, handlers, recovery, ledger, the 10-byte table entry, the register file, the experiments, and Section 4 Step 1 (lazy sampling), Step 6 (the cut count), Lemma 1 and Appendix A (certification method). Changed: Section 4 is rewritten as a first-collision proof of Lemma 2 (Steps 2 to 5), B and Tp are re-planned on it (time_log2 125.29113 to %s); step, generator and experiments unchanged." % TL,\n     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."},\n    {"submissionId": "1cd0dd3b-eb60-4572-a75f-937cd771ec4a",')
rep("the proof Section 4 (the supermartingale Lemma 2, clause (d) of H1), the experiments,", "clause (d) of H1, the experiments,")
rep(" Changed in this revision (v2): Section 4 (Lemma 2) is replaced by Lemma 2 v2 answering the rulings on 1cd0dd3b (Section 9 of the proof); program, ledger and experiments unchanged.", "")
rep("its Section 4 (the supermartingale Lemma 2, clause (d) of H1, the plan method with the Chernoff trail sums) is used unchanged in structure with the new parameters.", "its clause (d) of H1 and its plan method are used with the new parameters.")
rep("its finding is answered in a6ee439c and in Section 4 of this entry (the new Lemma 2 and clause (d) of H1).", "its finding is answered by clause (d) of H1 and Section 4 of this entry.")
open("build_all9.py", "w", encoding="utf-8", newline="\n").write(s)
print("ok", len(s))
