import random,json,sys
from initlib import *
rng=random.Random(20261012)
N=int(sys.argv[1]) if len(sys.argv)>1 else 20000
def rnd(): return rng.getrandbits(32)
def trial(H,flags,params):
    A,B,W4p=build(H,*params,flags=flags)
    sa,oa=compress(H,A,55,0,0,flags); sb,ob=compress(H,B,63,0,0,flags)
    X=sa['X']
    pins=(X[3],X[7],X[11],X[15])==(X3,X7,X11,X15) and sa['X']==sb['X']
    half=all(oa[i]==ob[i] for i in (0,2,5,7))
    return pins,half,oa,ob,((W4p-W4)&M),sa,sb
LOW=63  # low 6 bits
def run(label,Hf,flags=11,cond=None):
    r=dict(label=label,n=0,pins=0,half=0,dW4_plus8=0,agree={1:0,3:0,4:0,6:0},all4=0,notall=0)
    for _ in range(N):
        params=[rnd() for _ in range(8)]
        H=Hf()
        pins,half,oa,ob,d,sa,sb=trial(H,flags,params)
        r['n']+=1; r['pins']+=pins; r['half']+=half; r['dW4_plus8']+= (d==8)
        a=0
        for i in (1,3,4,6):
            if (oa[i]^ob[i])&LOW==0: r['agree'][i]+=1; a+=1
        r['all4']+= (a==4)
        r['notall']+= (not all(oa[i]==ob[i] for i in range(8)))
    return r
out=[]
def Hvar(k,constrain=False):
    def f():
        H=IV[:]
        while True:
            H[k]=rnd()
            if k!=2 or not constrain or (((H[2]+H[6]+W4)>>3)&1)==0: return H
    return f
out.append(run('control h=IV',lambda: IV[:]))
for k in range(4):
    out.append(run('h[%d] random uniform, others IV'%k,Hvar(k)))
for k in (2,):
    out.append(run('h[2] random with bit3(h2+h6+W4)=0',Hvar(2,True)))
def allfour():
    H=IV[:]
    for k in (0,1,3): H[k]=rnd()
    while True:
        H[2]=rnd()
        if (((H[2]+H[6]+W4)>>3)&1)==0: return H
    return H
out.append(run('h[0..3] all random (h2 with bit3 ok), h4..7=IV',allfour))
def cvlike():
    H=[rnd() for _ in range(8)]
    while (((H[2]+H[6]+W4)>>3)&1): H[2]=rnd()
    return H
out.append(run('multi-block chunk: h = arbitrary 8-word CV, flags 10 (CHUNK_END|ROOT), h2+h6 ok',cvlike,flags=10))
def cvany():
    return [rnd() for _ in range(8)]
out.append(run('multi-block chunk: h arbitrary 8-word CV, flags 10, no filter',cvany,flags=10))
json.dump(out,open('scan_init.out.json','w'),indent=1)
for r in out: print(r)
