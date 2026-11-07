import json, math, glob
from fractions import Fraction
W=[json.load(open(f))[0] for f in sorted(glob.glob("led/win_*.json"))]
n=len(W); ops=[w["ops"] for w in W]; cl=[w["distinct_claws"] for w in W]; gr=[w["distinct_groups"] for w in W]
T99={23:2.499867,72:2.379}[n-1]
def st(x): m=sum(x)/n; s=math.sqrt(sum((v-m)**2 for v in x)/(n-1)); return m,s
mo,so=st(ops); mc,sc=st(cl); mg,sg=st(gr); rr=[g/c for g,c in zip(gr,cl)]; mr,sr=st(rr)
mu_p=math.ceil(mo+T99*so/math.sqrt(n)); c_m=mc-T99*sc/math.sqrt(n); g_m=mg-T99*sg/math.sqrt(n); r_m=mr-T99*sr/math.sqrt(n)
print("windows",n,"claws",sum(cl),"groups",sum(gr),"ops",sum(ops),"ops/claw %.1f (range %.1f-%.1f)"%(sum(ops)/sum(cl),min(o/c for o,c in zip(ops,cl)),max(o/c for o,c in zip(ops,cl))))
print("mu %.0f sd %.0f mu+ %d | c %.2f c- %.2f | g %.2f g- %.2f | r %.6f r- %.6f | c-r- %.2f <= g- %s"%(mo,so,mu_p,mc,c_m,mg,g_m,mr,r_m,c_m*r_m,c_m*r_m<=g_m))
for q in (-74.46,-74.50,-75.36):
    lp=math.log2(585/524288)-32+q; lam=-math.log(0.60999)
    G=lam/2**lp; N=G/r_m; B=math.floor(N*(1+2**-19)/c_m)+1
    WB=math.floor(B*mu_p*(1+2**-20))+1; R=2**51
    T=Fraction(WB+R+6*B,2812)+2**36
    t=math.log2(T.numerator)-math.log2(T.denominator)
    print("q %.4f: log2G %.4f log2N %.4f B=%d (2^%.4f) W_BUDGET=%d (2^%.4f) time %.5f"%(q,math.log2(G),math.log2(N),B,math.log2(B),WB,math.log2(WB),t))
