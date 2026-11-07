import json, sys
from polylib import *
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 99)
j=int(sys.argv[2]) if len(sys.argv)>2 else 0
F=get_F(j); a,b,U0,V0,dd,base=setup(MDS,round_opts(0,{}),j)
INV5=pow(5,-1,P-1)
def sqrt_mod(x):
    # p = 1 mod 4: use flint poly sqrt? use Tonelli-Shanks
    if x==0: return 0
    if pow(x,(P-1)//2,P)!=1: return None
    q=P-1; s=0
    while q%2==0: q//=2; s+=1
    z=2
    while pow(z,(P-1)//2,P)==1: z+=1
    m=s; c=pow(z,q,P); t=pow(x,q,P); r=pow(x,(q+1)//2,P)
    while t!=1:
        i=0; tt=t
        while tt!=1: tt=tt*tt%P; i+=1
        bb=pow(c,1<<(m-i-1),P); m=i; c=bb*bb%P; t=t*c%P; r=r*bb%P
    return r
out={}
c=random.randrange(P)
t0=time.time()
Fs=taylor_shift(F,c); g=odd_part(Fs); n=g.degree()
Sx=PC([0,1])
tt=time.time()
h=(P-1)//2
pw=Sx.pow_mod(h,g)
out['pow_sec']=round(time.time()-tt,1); print('pow done',out['pow_sec'],flush=True)
tt=time.time()
gc=g.gcd(pw-1); out['gcd_sec']=round(time.time()-tt,1)
out['deg_gcd']=gc.degree(); out['bits_h']=h.bit_length(); out['popcount_h']=bin(h).count('1')
print('gcd',out,flush=True)
if gc.degree()>=1:
    rts=[int(r) for r,m in gc.roots()] if gc.degree()>0 else []
    out['nroots_nonzero_square']=len(rts)
    for Sroot in rts:
        s=sqrt_mod(Sroot)
        W1=(c+s)%P; W2=(c-s)%P
        ins=[]
        for W in (W1,W2):
            tau=pow(W,INV5,P)
            nk=(pow((U0+a*tau)%P,INV5,P)-RC[0][0])%P
            rho=(pow((V0+b*tau)%P,INV5,P)-RC[0][1])%P
            ins.append((nk,rho))
        h1=hash_reduced(*ins[0],1); h2=hash_reduced(*ins[1],1)
        out['collision']=dict(distinct=ins[0]!=ins[1], equal_digest=(h1==h2), digest=hex(h1), nk1=hex(ins[0][0]),rho1=hex(ins[0][1]),nk2=hex(ins[1][0]),rho2=hex(ins[1][1]))
        print(out['collision'])
        break
out['total_sec']=round(time.time()-t0,1)
out['c']=hex(c); out['j']=j
json.dump(out,open('root_j%d_s%s.json'%(j,sys.argv[1] if len(sys.argv)>1 else '99'),'w'),indent=1)
print(out)
