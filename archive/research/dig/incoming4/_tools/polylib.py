import time, random, math
from eng import *
def get_F(j, var=None):
    r = run_line(1, j, var or {})
    return r['poly']

def factorials(n):
    f=[1]*(n+1)
    for i in range(1,n+1): f[i]=f[i-1]*i%P
    return f

_fact = {}
def taylor_shift(F, c):
    n = F.degree()
    if n not in _fact:
        f = factorials(n); inv_f = [0]*(n+1); inv_f[n]=pow(f[n],P-2,P)
        for i in range(n,0,-1): inv_f[i-1]=inv_f[i]*i%P
        _fact[n]=(f,inv_f)
    f,inv_f=_fact[n]
    co=[int(x) for x in F.coeffs()]
    A=[co[i]*f[i]%P for i in range(n+1)]
    Arev=PC(A[::-1])
    C=[0]*(n+1); pw=1
    for m in range(n+1):
        C[m]=pw*inv_f[m]%P; pw=pw*c%P
    prod=Arev*PC(C)
    pc=[int(x) for x in prod.coeffs()]
    pc += [0]*(2*n+2-len(pc))
    b=[pc[n-k]*inv_f[k]%P for k in range(n+1)]
    return PC(b)   # F(c+s) as poly in s

def odd_part(Fs):
    """g(S) with F(c+s)-F(c-s) = 2 s g(s^2)"""
    b=[int(x) for x in Fs.coeffs()]
    return PC([2*b[k]%P for k in range(1,len(b),2)])
def nnz(f): return sum(1 for c in f.coeffs() if int(c)!=0)
