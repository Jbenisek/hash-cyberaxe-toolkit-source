# tc_pf_013.py : time of the pf_013 pair from its own 24-window ledger, both ways.
# convention = one-sided 99% ledger bounds (mu+, c-, r-) + declared tail QDECL; best = ledger means + tail at its measured linear mean.
import json, math, glob
from fractions import Fraction
W=[json.load(open(f))[0] for f in sorted(glob.glob("pf_013/led/win_*.json"))]
n=len(W); ops=[w["ops"] for w in W]; cl=[w["distinct_claws"] for w in W]; gr=[w["distinct_groups"] for w in W]
T99={23:2.499867}[n-1]
def st(x): m=sum(x)/n; s=math.sqrt(sum((v-m)**2 for v in x)/(n-1)); return m,s
mo,so=st(ops); mc,sc=st(cl); mg,sg=st(gr); rr=[g/c for g,c in zip(gr,cl)]; mr,sr=st(rr)
D="../pkg_r39_combined/work/tail_var/pf_013"; NCH,NB,LF=20,80,2048; ql=[]
for i in range(1,15):
    d=json.load(open("%s/out_%02d.json"%(D,i)))["trials"]; ql.append((2.0**d[0]["observations"]["log2_carrier"])*(sum(t["observations"]["hits"] for t in d[1:NCH+1])/float(NCH*NB*LF)))
qmean=math.log2(sum(ql)/14)
def tm(q,mu,c,r):
    lp=math.log2(585/524288)-32+q; lam=-math.log(0.60999); G=lam/2**lp; N=G/r; B=math.floor(N*(1+2**-19)/c)+1
    WB=math.floor(B*mu*(1+2**-20))+1; T=Fraction(WB+2**51+6*B,2812)+2**36
    return math.log2(T.numerator)-math.log2(T.denominator),B,WB,G,N
print("windows",n,"claws",sum(cl),"groups",sum(gr),"ops",sum(ops),"ops/claw %.1f"%(sum(ops)/sum(cl)))
print("means mu %.2f c %.4f g %.4f r %.6f | sd %.0f %.2f %.2f %.6f | tail mean_lin %.6f"%(mo,mc,mg,mr,so,sc,sg,sr,qmean))
cv=(math.ceil(mo+T99*so/math.sqrt(n)),mc-T99*sc/math.sqrt(n),mr-T99*sr/math.sqrt(n))
for lab,q,(mu,c,r) in (("convention",-74.53,cv),("best",qmean,(math.ceil(mo),mc,mr)),("best_q4",-74.3772,(math.ceil(mo),mc,mr))):
    t,B,WB,G,N=tm(q,mu,c,r)
    print("%-10s q %.6f mu %d c %.4f r %.6f: log2G %.4f log2N %.4f B=%d (2^%.4f) W_BUDGET=%d (2^%.4f) time %.5f"%(lab,q,mu,c,r,math.log2(G),math.log2(N),B,math.log2(B),WB,math.log2(WB),t))
