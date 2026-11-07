"""Reference/research implementation of the pinned Orchard Poseidon instance.
Not a wallet, transaction tool, or claim of production cryptanalytic weakness.
Constants regenerated from the published Grain specification; no network required.
"""
from __future__ import annotations
import functools
P=int('40000000000000000000000000000000224698fc094cf91b992d30ed00000001',16)
CAP=1<<65
RF,RP=8,56
ROOT5=pow(5,-1,P-1)

class Grain:
    def __init__(self):
        self.s=[]
        for value,width in [(1,2),(0,4),(255,12),(3,12),(8,10),(56,10)]:
            self.s.extend(map(int,f'{value:0{width}b}'))
        self.s.extend([1]*30)
        for _ in range(160): self.raw()
    def raw(self):
        s=self.s
        b=s[62]^s[51]^s[38]^s[23]^s[13]^s[0]
        self.s=s[1:]+[b]
        return b
    def bit(self):
        while True:
            a,b=self.raw(),self.raw()
            if a:return b
    def word(self,reject=True):
        while True:
            x=0
            for _ in range(255): x=2*x+self.bit()
            if not reject:return x%P
            if x<P:return x

def mat_vec(m,x,p=P):
    return [sum(a*b for a,b in zip(row,x))%p for row in m]

def mat_mul(a,b,p=P):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))%p for j in range(len(b[0]))] for i in range(len(a))]

def rank(a,p=P):
    a=[list(map(lambda v:v%p,row)) for row in a]
    if not a:return 0
    i=0
    for j in range(len(a[0])):
        pivot=next((k for k in range(i,len(a)) if a[k][j]),None)
        if pivot is None:continue
        a[i],a[pivot]=a[pivot],a[i]
        inv=pow(a[i][j],-1,p);a[i]=[v*inv%p for v in a[i]]
        for k in range(len(a)):
            if k!=i:
                f=a[k][j];a[k]=[(x-f*y)%p for x,y in zip(a[k],a[i])]
        i+=1
        if i==len(a):break
    return i

def inverse_matrix(m,p=P):
    n=len(m); a=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(m)]
    for j in range(n):
        k=next((i for i in range(j,n) if a[i][j]%p),None)
        if k is None:raise ValueError('singular matrix')
        a[j],a[k]=a[k],a[j];v=pow(a[j][j],-1,p)
        a[j]=[x*v%p for x in a[j]]
        for i in range(n):
            if i!=j:
                t=a[i][j];a[i]=[(x-t*y)%p for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a]

@functools.lru_cache(1)
def parameters():
    g=Grain()
    rc=[[g.word() for _ in range(3)] for _ in range(64)]
    while True:
        xy=[g.word(False) for _ in range(6)]
        if len(set(xy))==6:break
    m=[[pow((xy[i]+xy[3+j])%P,-1,P) for j in range(3)] for i in range(3)]
    return rc,m,inverse_matrix(m)

def full(i):return i<4 or i>=60

def step(s,i,params=None):
    rc,m,_=parameters() if params is None else params
    z=[(x+c)%P for x,c in zip(s,rc[i])]
    if full(i):z=[pow(x,5,P) for x in z]
    else:z[0]=pow(z[0],5,P)
    return mat_vec(m,z)

def backstep(s,i):
    rc,_,mi=parameters();z=mat_vec(mi,s)
    if full(i):z=[pow(x,ROOT5,P) for x in z]
    else:z[0]=pow(z[0],ROOT5,P)
    return [(x-c)%P for x,c in zip(z,rc[i])]

def permutation(s,rounds=64,trace=False):
    if type(rounds)is not int or not 1<=rounds<=64:raise ValueError('rounds must be integer in 1..64')
    if len(s)!=3 or any(type(x)is not int or not 0<=x<P for x in s):raise ValueError('noncanonical state')
    s=list(s);out=[s[:]]
    for i in range(rounds):s=step(s,i);out.append(s[:])
    return out if trace else s

def decode(data):
    if type(data)is not bytes or len(data)!=64:raise ValueError('requires exactly 64 bytes')
    a,b=int.from_bytes(data[:32],'little'),int.from_bytes(data[32:],'little')
    if a>=P or b>=P:raise ValueError('noncanonical field element')
    return a,b

def encode(a,b):
    if any(type(x)is not int or not 0<=x<P for x in (a,b)):raise ValueError('noncanonical input')
    return a.to_bytes(32,'little')+b.to_bytes(32,'little')

def digest(data,rounds=64):
    a,b=decode(data)
    return permutation([a,b,CAP],rounds)[0].to_bytes(32,'little')

if __name__=='__main__':
    rc,m,mi=parameters()
    expected=[int(s,16) for s in ['2a526acd0b64b45394efb364f966240ff7e69a71d0b642a0aeb1bc024aeca456','13c5d1568b4aa43076ff7dae343d5512dcd42e7fbed9dafe012a3e9628e5b82a','0a49c868c6976544256fcd597984561af7cfdfe1bda42c7b359029a1d34e9ddd']]
    assert permutation([0,1,2])==expected
    print('Official full-width [0,1,2] permutation vector: PASS')
    print('MDS:',[[hex(x) for x in row] for row in m])
    print('constants0:',[hex(x) for x in rc[0]])
    print('root5',hex(ROOT5))
