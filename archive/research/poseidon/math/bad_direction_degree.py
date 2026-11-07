import numpy as np, random
q=1000003
xs=(0,1,2);ys=(3,4,5)
M=[[pow(xs[i]+ys[j],-1,q) for j in range(3)] for i in range(3)]
rc=[[(7*r+13*l+1)%q for l in range(3)] for r in range(6)]
n=[630,997903,1575]; B=224807
def tr(a):
    a=np.array(a,dtype=np.int64)%q
    nz=np.nonzero(a)[0]
    return a[:nz[-1]+1] if len(nz) else np.zeros(1,dtype=np.int64)
def add(a,b):
    c=np.zeros(max(len(a),len(b)),dtype=np.int64); c[:len(a)]+=a; c[:len(b)]+=b; return tr(c)
def sc(a,k): return tr(a*k%q)
def mul(a,b): return tr(np.convolve(a,b)%q) if len(a)*len(b)<2000 else tr(conv(a,b))
def conv(a,b):
    # split to keep int64 safe: a,b<2^20; products<2^40; sums up to 2^23 terms ok (<2^63)
    return np.convolve(a,b)%q
def p5(a):
    a2=tr(conv(a,a));a4=tr(conv(a2,a2));return tr(conv(a4,a))
def deg(a): return len(tr(a))-1 if np.any(a) else -1
def mv(v): return [tr(sum((sc(v[j],M[i][j]) for j in range(3)),np.zeros(1,dtype=np.int64))) if False else None for i in range(3)]
def matv(v):
    out=[]
    for i in range(3):
        acc=np.zeros(1,dtype=np.int64)
        for j in range(3): acc=add(acc,sc(v[j],M[i][j]))
        out.append(acc)
    return out
def addc(v,c): return [add(v[i],np.array([c[i]])) for i in range(3)]
def push(z):
    s=matv([p5(x) for x in z])             # s2
    dl=max(deg(x) for x in s)
    x=addc(s,rc[2]); s3=matv([p5(t) for t in x])
    g0=add(s3[0],np.array([rc[3][0]]))
    y=[p5(g0),addc(s3,rc[3])[1],addc(s3,rc[3])[2]]
    s4=matv(y)
    g1=add(s4[0],np.array([rc[4][0]]))
    y=[p5(g1),addc(s4,rc[4])[1],addc(s4,rc[4])[2]]
    s5=matv(y)
    x=addc(s5,rc[5]); 
    d=np.zeros(1,dtype=np.int64)
    for j in range(3): d=add(d,sc(p5(x[j]),M[0][j]))
    return dl,deg(g0),deg(g1),deg(d)
bad=[(1,30903,841206),(1,182900,377200),(1,270361,827149)]
ninv=pow(n[2],-1,q)
for al in bad:
    assert sum(n[i]*al[i] for i in range(3))%q==0
    for e in (1,2,3):
        random.seed(e*7+al[1])
        z=[np.zeros(e+1,dtype=np.int64) for _ in range(3)]
        for i in range(3):
            for k in range(e): z[i][k]=random.randrange(q)
            z[i][e]=al[i]
        # fix coordinate 2 lower terms: n.z=B
        for k in range(e+1):
            tgt=B if k==0 else 0
            z[2][k]=(tgt-n[0]*z[0][k]-n[1]*z[1][k])*ninv%q
        assert z[2][e]==al[2]%q
        assert all((n[0]*z[0][k]+n[1]*z[1][k]+n[2]*z[2][k])%q==(B if k==0 else 0) for k in range(e+1))
        zz=[tr(c) for c in z]
        dl,g0,g1,dg=push(zz)
        print(al[1],e,"delta",dl,"g0",g0,"g1",g1,"dig",dg,"625delta",625*dl,flush=True)
