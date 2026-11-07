import numpy as np, json
from math import log2
from sympy import Poly, symbols, GF
x=symbols('x')
rng=np.random.default_rng(777)
p=10007; deg=120; bad=0; T=400
for t in range(T):
    co=[1]+[int(v) for v in rng.integers(0,p,size=deg)]
    g=Poly(co,x,modulus=p)
    d=g.diff(x)
    gg=g.gcd(d)
    if gg.degree()>0: bad+=1
print('toy squarefree: nonsquarefree',bad,'of',T)
C=237
def tot(dbud, nc=2):
    pc=3910+3+43338189+45559521537+dbud+214000000+400000
    return 143597+nc*pc+10000000+2500000+200000
base=tot(8800000000)
for b in (6.1e9,6.4e9):
    print(b, log2(base/C), log2(tot(b)/C), log2(base/tot(b)))
# fresh run stage D observed 5,850,480,330 -> budget exactly observed
print('obs D 5850477654+', log2(base/tot(5850480330)))
