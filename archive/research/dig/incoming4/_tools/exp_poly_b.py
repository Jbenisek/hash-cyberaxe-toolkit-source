import json
from polylib import *
random.seed(777)
res={}
F=get_F(0); n=F.degree()
cs=[0]+[random.randrange(P) for _ in range(3)]
for c in cs:
    t=time.time()
    Fs=taylor_shift(F,c); t1=time.time()-t
    g=odd_part(Fs); dg=g.degree()
    # direct check h(s)=F(c+s)-F(c-s) = 2 s g(s^2) at 3 random s
    ok=True
    for _ in range(3):
        s=random.randrange(P)
        lhs=(int(F((c+s)%P))-int(F((c-s)%P)))%P
        rhs=2*s*int(g(s*s%P))%P if False else (s*int(g(s*s%P)))%P
        ok &= (lhs==rhs)
    # g defined with factor 2 included in odd_part: h = s*g(s^2)  => lhs==s*g(s^2)
    t=time.time(); gd=g.derivative(); gg=g.gcd(gd); t2=time.time()-t
    lcg=int(g[dg]); lcF=int(F[n])
    rec=dict(c=hex(c) if c else '0', shift_sec=round(t1,2), deg_g=dg, nnz_g=nnz(g), lc_g_eq_2lcF=(lcg==2*lcF%P), shift_matches_direct_eval=ok,
             gcd_g_gprime_deg=gg.degree(), gcd_sec=round(t2,1))
    res[rec['c'][:12]]=rec; print(rec,flush=True)
json.dump(res,open('poly_b.json','w'),indent=1)
