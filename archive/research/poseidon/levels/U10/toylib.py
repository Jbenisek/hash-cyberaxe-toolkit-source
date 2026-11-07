import random, math, numpy as np
def is_prime(n):
    if n<2: return False
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return True
def v2(n):
    k=0
    while n%2==0: n//=2;k+=1
    return k
def inv(a,q): return pow(a,-1,q)
def det3(M,q):
    return (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))%q
def is_mds(M,q):
    if any(M[i][j]%q==0 for i in range(3) for j in range(3)): return False
    for i1 in range(3):
        for i2 in range(i1+1,3):
            for j1 in range(3):
                for j2 in range(j1+1,3):
                    if (M[i1][j1]*M[i2][j2]-M[i1][j2]*M[i2][j1])%q==0: return False
    return det3(M,q)!=0
def is_cauchy(M,q):
    N=[[inv(M[i][j],q) for j in range(3)] for i in range(3)]
    return all((N[i][j]-N[i][0]-N[0][j]+N[0][0])%q==0 for i in range(3) for j in range(3))
class Toy:
    def __init__(self,q,seed,cauchy=True,zero_consts=False,cap=None,rows=64):
        self.q=q; rnd=random.Random(seed*1000003+q+(7 if not cauchy else 0))
        self.cap=pow(2,65,q) if cap is None else cap%q
        if cauchy:
            while True:
                xs=rnd.sample(range(q),3); ys=rnd.sample(range(q),3)
                if all((x+y)%q for x in xs for y in ys): break
            self.M=[[inv(x+y,q) for y in ys] for x in xs]
        else:
            while True:
                M=[[rnd.randrange(q) for _ in range(3)] for _ in range(3)]
                if is_mds(M,q) and not is_cauchy(M,q): break
            self.M=M
        self.RC=[[0,0,0] if zero_consts else [rnd.randrange(q) for _ in range(3)] for _ in range(rows)]
    def sched(self,r): return [(i,True) for i in range(4)]+[(i,False) for i in range(4,4+r)]+[(i,True) for i in range(60,64)]
    def perm(self,s,r,upto=None):
        q,M,RC=self.q,self.M,self.RC
        for n,(idx,full) in enumerate(self.sched(r)):
            if upto is not None and n>=upto: break
            s=[(s[i]+RC[idx][i])%q for i in range(3)]
            for i in (range(3) if full else range(1)):
                x2=s[i]*s[i]%q; x4=x2*x2%q; s[i]=x4*s[i]%q
            s=[(M[i][0]*s[0]+M[i][1]*s[1]+M[i][2]*s[2])%q for i in range(3)]
        return s
    def perm_int(self,s,r):
        q,M,RC=self.q,self.M,self.RC
        s=list(s)
        for idx,full in self.sched(r):
            s=[(s[i]+RC[idx][i])%q for i in range(3)]
            for i in (range(3) if full else range(1)): s[i]=pow(s[i],5,q)
            s=[sum(M[i][j]*s[j] for j in range(3))%q for i in range(3)]
        return s
    def grid(self,chunk=None):
        q=self.q
        chunk=chunk or max(1,min(q,4_000_000//q))
        rho=np.arange(q,dtype=np.int64)
        for st in range(0,q,chunk):
            nks=np.arange(st,min(q,st+chunk),dtype=np.int64)
            yield np.repeat(nks,q),np.tile(rho,len(nks))
    def run_all(self,r,upto=None):
        """generator of output lane lists per chunk (NK,RHO,[l0,l1,l2])"""
        for NK,RHO in self.grid():
            s=self.perm([NK,RHO,np.full_like(NK,self.cap)],r,upto)
            yield NK,RHO,s
def pairs(counts): 
    c=counts.astype(np.float64); return float((c*(c-1)/2).sum())
def keycounts(toy,r,keyf,nbins,upto=None):
    cnt=np.zeros(nbins,dtype=np.int64)
    for NK,RHO,s in toy.run_all(r,upto):
        cnt+=np.bincount(keyf(s),minlength=nbins)
    return cnt
def stat(cnt,N,nbins):
    """collision pairs / random expectation (N^2/2)/nbins ; var/mean of fibre sizes"""
    exp=N*(N-1)/2/nbins; mean=N/nbins
    return pairs(cnt), pairs(cnt)/exp, cnt.var()/mean, int((cnt>0).sum())
