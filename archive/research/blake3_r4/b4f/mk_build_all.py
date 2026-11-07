"""Builds build_all.py of B3R4f from build_all_b4e.py (exact-match edits)."""
import re
s = open("build_all_b4e.py", encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("TL3 = 124.8123\nTL1 = 125.35348\n", "")
rep('kfin = ls["nmax"] - 256\n', "")
rep('PH7 = b.packed_circuit(st.qwords)[1]\n', 'PH7 = b.packed_circuit(st.qwords)[1]\nCODE7 = b.packed_circuit(st.qwords)[2]\n_fl = b.packed_circuit(st.qwords)[0].flat\n_ix = {o: [i for i, c in enumerate(_fl) if c[0] == o] for o in "IDZJ"}\nRB = _ix["D"][0] - _ix["I"][0] - 1\nMV = _ix["J"][0] - _ix["Z"][0] - 1\nassert CODE7 == 24 + 1 + RB + 3 + MV + 1 + 16 and PH7 == 24 + 1 + 4 * (RB + 3) + 3 * (MV + 1) + 16\n')
# vals
i = s.index('    trails=ls["trails"], pk2=pk2,')
j = s.index("    kb=p[\"kb\"], fb=p[\"fb\"]")
s = s[:i] + '    trails=ls["trails"], pk2=pk2, kappa=b.KAPPA_256, cmax=b.CMAX, tfull=tmax - 59, sens=sens_txt, sens_short=sens_short, sparereq=b.SPARE,\n' + s[j:]
rep('    sumloss=sumloss, Pl=ls["P_lower"],', '    t_coll=ls["collision"], t_delay=ls["delay"], t_own=ls["own_trail"], t_long=ls["long_partner"], t_age=ls["age_cap"], t_dist=ls["disturbance"], nbins=fm(22000), PPq=ls["hq"], keybits=40,\n    CODE7=CODE7, RB=RB, MV=MV, Pl=ls["P_lower"],')
rep("    TL=TL, TL3=TL3, dr3=TL - TL3, TL1=TL1, dr1=TL1 - TL, dTL=TL - 125.02375, slack", "    TL=TL, slack")
rep("PH7=PH7, PH7p=PH7 + b.RECOVER_EXTRA,", "PH7=PH7, PH7p=PH7 + b.RECOVER_EXTRA,")
rep('recov=fm(PH7 + b.RECOVERY_CODE)', 'recov=fm(CODE7 + b.RECOVERY_CODE)')
# the V2 block
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
slackops = int(N * (2.0 ** (TL - TLraw) - 1))
V2 = dict(Pcert=Pcert, kk=kk, Hq=ls["hh"], pbin=pbin, ES=ES, EX=EX, EJ2a=EJ2a, EJ2b=EJ2b, EY=EY, Mnum=Mnum, Qnum=Qnum, slackops=fm(slackops), body=body)

'''
s = s[:i] + new + s[j:]
# claim texts
rep("by a supermartingale over the evaluations, with no conditioning on which trails finish and no fixed-size birthday step; (d) is the premise", "from the first collision of the run and the detection delay (no conditioning on which trails finish, no fixed-size birthday step); (d) is the premise")
rep("Memory: %d table entries of 10 bytes (%d bytes)", "Memory: %d table entries of 7 bytes (%d bytes)")
rep("(a supermartingale over the evaluations, no conditioning on which trails finish, the cut count bounded by a proved theorem;", "(the first collision of the run and the detection delay, no conditioning on which trails finish, the cut count bounded by a proved theorem;")
# dependencies
i = s.index("deps = [")
j = s.index('    {"submissionId": "75d5e1f9')
newdeps = '''deps = [
    {"submissionId": "a6ee439c-5b82-41f2-8acb-9917c8c70756",
     "rationale": "Our own B3R4d (time_log2 125.06000), filed 10-15, in review: the filed version of this program. Taken from it: the target form, the bit-sliced 256-lane step, the circuit generator (rerun with the new code size), the search, handlers, ledger method, Lemma 1, the lazy-sampling facts and the cut count of Section 4, and the experiments. Changed: the success proof of Section 4 (Steps 2 to 5), the recovery circuit (rolled), the table entry (7 bytes), and the plan constants that follow.",
     "evidence": "proof.md first paragraph and Sections 2, 3.3, 4, 7 and Appendix A."},
    {"submissionId": "9f69f1cc-f6b2-4e86-a668-19b5a2085a2c",
     "rationale": "Our own B3R4e (time_log2 125.06177), in review: the same program as a6ee439c with Lemma 2 v2 (cut-count heuristic withdrawn and proved, Chernoff tail certified in exact arithmetic). Taken from it: Step 6 of Section 4 (the cut count), Lemma 1, the lazy-sampling facts and the certification method of Appendix A.",
     "evidence": "proof.md Section 4 Steps 0, 1, 6, 7 and Appendix A."},
    {"submissionId": "41b32afc-ed4c-4ef1-b9f2-8c72ab163582",
     "rationale": "Our own round-4 entry B3R4b (125.02375), rejected by the judges (not_evaluable) on one finding about the success-probability step of its Lemma 2. The program, circuit, ledger method and experiments of this entry descend from 41b32afc; its Lemma 2 is replaced (Section 4).",
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.6, 4, 5, 6, 7, 8 and Appendix A."},
'''
s = s[:i] + newdeps + s[j:]
open("build_all.py", "w", encoding="utf-8", newline="\n").write(s)
print("ok", len(s))
