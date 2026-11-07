import sys,random,math,time
sys.path.insert(0,'.')
from b3ctr import *
R=random.Random(12345)
QM,QV=0x0e09818b,0x02008000
def cstar(L,t0):
    K0a1=rol(L['K0d1'],16)^t0
    w0=(K0a1-IV[0]-IV[4])&M
    Y2=(w0+L['C2a1']+L['C2b1'])&M
    Y14=ror(Y2^L['C2d1'],8)
    Y10=(Y14+L['C2c1'])&M
    Y6=ror(Y10^L['C2b1'],7)
    E1a1=(Y6+L['Y1']+L['w12'])&M
    E1d1=ror(E1a1^L['Y12'],16)
    return (E1d1+Y11)&M
def rf():
    f=rnd_free(R,1); f['t_hi']=0
    e1=(R.getrandbits(32)&~0x03cf8303&M)|0x030c0303; f['Y4']=(e1-Y3)&M; f['c1']=0
    return f
T0=[1,1000,0xdeadbeef]
# roundtrip validation: building with c1* gives t_lo == t0
bad=0
for _ in range(3000):
    f=rf(); w,t,L=build(f)
    for t0 in T0:
        f2=dict(f); f2['c1']=cstar(L,t0); w2,t2,_=build(f2); bad+= (t2&M)!=t0
print("roundtrip c1*(t0) -> t_lo==t0: bad",bad,"of",3000*len(T0))
# also: c1 -> t_lo injective on random c1 (permutation): check 2000 draws x 50 c1
col=0
for _ in range(200):
    f=rf(); seen=set()
    for _ in range(50):
        f['c1']=R.getrandbits(32); w,t,_=build(f); seen.add(t&M)
    col+= 50-len(seen)
print("collisions among c1->t_lo images (should be 0):",col)
N=int(sys.argv[1]); hits=[0]*len(T0); t=time.time()
for i in range(N):
    f=rf(); w,tt,L=build(f)
    for j,t0 in enumerate(T0):
        c=cstar(L,t0); hits[j]+= (c&QM)==QV
print("N",N,"hits",hits,"expected 2^-11*N =",N/2048,"time",round(time.time()-t))
for h in hits:
    p=h/N; z=1.96; d=1+z*z/N; ctr=(p+z*z/(2*N))/d; hw=z*math.sqrt(p*(1-p)/N+z*z/(4*N*N))/d
    print(" p=%.4e  log2=%.3f  Wilson95 log2 [%.3f,%.3f]"%(p,math.log2(p),math.log2(ctr-hw),math.log2(ctr+hw)))
