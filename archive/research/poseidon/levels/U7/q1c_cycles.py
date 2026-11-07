# Q1c: exact cycle spectrum of x->x^5 on F_p^* (multiplication by 5 on Z/(p-1) after discrete log). Uses full factorisation of p-1.
from math import gcd
from itertools import product
from sympy import factorint, n_order, totient
from collections import defaultdict
p=0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
q1=539204044132271846773; q2=8999194758858563409123804352480028797519453
F={2:32,3:1,463:1,q1:1,q2:1}
N=p-1
assert N==2**32*3*463*q1*q2
# ord_m(5) for prime powers
def ordpp(q,e):
    m=q**e
    return 1 if m==1 else n_order(5,m)
from math import lcm
# enumerate divisors by exponent choice
primes=list(F)
spec=defaultdict(int)   # cycle length -> number of elements (nonzero)
ncount=0
ords={}
for pr in primes:
    for e in range(F[pr]+1):
        ords[(pr,e)]=ordpp(pr,e)
print("ord of 5 mod prime-power parts:")
for pr in (2,3,463):
    print(" ",pr,[ (e,ords[(pr,e)]) for e in range(F[pr]+1) if e<=6 or e==F[pr]])
print("  mod q1:",ords[(q1,1)],"mod q2:",ords[(q2,1)])
tot=0
for es in product(*[range(F[pr]+1) for pr in primes]):
    m=1; L=1; ph=1
    for pr,e in zip(primes,es):
        m*=pr**e
        if e: ph*=(pr-1)*pr**(e-1)
        L=lcm(L,ords[(pr,e)])
    spec[L]+=ph; tot+=ph
assert tot==N
print("total nonzero elements",tot==N)
print("distinct cycle lengths:",len(spec))
ncyc=sum(c//L for L,c in spec.items())
print("number of cycles on F_p^*: ",ncyc, "(plus the fixed point 0)")
print("longest cycle length:",max(spec), " elements on cycles of that length:",spec[max(spec)], "fraction",spec[max(spec)]/N)
print("Cycle lengths <= 1000 (length: #elements, #cycles):")
for L in sorted(spec):
    if L<=1000: print(" ",L,spec[L],spec[L]//L)
big=sum(c for L,c in spec.items() if L>10**6)
print("fraction of elements on cycles longer than 1e6:",big/N)
print("fraction on cycles longer than 2^20 =",sum(c for L,c in spec.items() if L>2**20)/N)
import math
print("shortest cycle lengths>1:", sorted(spec)[:12])
# which elements have period dividing L: gcd(5^L-1,p-1) nonzero elements, + zero
for L in (1,2,3,4,5,6,8,10,12,16,24,32):
    print("points with x^(5^%d)=x (incl 0):"%L, gcd(5**L-1,N)+1)
# fraction on cycle of period <= T
for T in (2**10,2**20,2**30):
    print("elements with period <= %d: fraction %.3e"%(T,sum(c for L,c in spec.items() if L<=T)/N))
