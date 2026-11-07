# stage_freeze.py TAG : write the recomputed frozen sandbox values (freeze_TAG.json, t4_TAG.json) into pkg_r39_TAG's r39joint.py
import sys, json, re
tag = sys.argv[1]; F = json.load(open("freeze_%s.json" % tag)); T4 = json.load(open("t4_%s.json" % tag))
p = "../pkg_r39_%s/sha256/experiments/r39joint.py" % tag; t = open(p, encoding="utf-8").read()
def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a, t.count(a)); t = t.replace(a, b)
old = re.search(r"WIN_EXP=\{\n(.*?)\n\}", t, re.S).group(1)
rep(old, "\n".join("%s:(%s)," % (k, ",".join(map(str, v))) for k, v in F["WIN_EXP"].items()))
e1 = F["e1_tmpl"] if tag != "s108" else None
krec = (F["e1_tmpl"]["kernel_records"])
rep('"kernel_records":731,"claw_ops":6173', '"kernel_records":%d,"claw_ops":6173' % krec)
if tag == "s108":   # the advice's own A[4] is odd: claw equation through the even-branch formula, pair passed as claw(u, a0)
    rep("    a0,u=BA[4],MP_PUB[1]\n    assert a0%2==0 and fstep(a0,A.c)==(s0(u)-u)&M\n    A.check=False;o0=A.m.o\n    r=A.claw(a0,u);A.check=True",
        "    a0,u=BA[4],MP_PUB[1];cw,eb,c0,c1,c4,c5=A.c;e0=(a0+eb)&M\n    assert u%2==1 and(cw+S0(a0)+MAJ(a0,c0,c1)+S1(e0)+CH(e0,c4,c5)-a0)&M==(s0(u)-u)&M\n    A.check=False;o0=A.m.o\n    r=A.claw(u,a0);A.check=True")
assert T4["stop_grp"] == 1 and T4["off"] == 2000
rep("T4_EXP=(7466204727408384999,(473,477,32719,978,748,15,15,7317,21892301,1234,0,996,493))", "T4_EXP=(7466204727408384999,(%s))" % ",".join(map(str, T4["T4"])))
rep("C.idc0=(1<<20)-1998", "C.idc0=(1<<20)-2000")
n = F["nG"]
rep("len(_G_SEQ)==3318", "len(_G_SEQ)==%d" % n); rep("exp=3318/256.0", "exp=%d/256.0" % n); rep("m=sum(xs)/3318.0", "m=sum(xs)/%d.0" % n)
rep("for j in range(3317)", "for j in range(%d)" % (n - 1)); rep("*3318**0.5<3", "*%d**0.5<3" % n)
rep("assert round(c17,2)==268.01 and round(c18,2)==280.2", "assert round(c17,2)==%s and round(c18,2)==%s" % (repr(F["c17"]), repr(F["c18"])))
open(p, "w", encoding="utf-8", newline="\n").write(t); print(tag, "staged; bytes", len(t.encode()))
