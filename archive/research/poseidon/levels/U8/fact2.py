# U8: longer ECM try on the 412-bit cofactor of p^2+p+1 (single process, wall cap 1500 s)
import time
from sympy.ntheory import ecm as secm
from gmpy2 import is_prime
C=10336410183878389456389411122965216970727148811023702430995384658173246000781176565624088163903039586972430848856941306458963
t0=time.time(); work=[C]; done=[]
for B1 in (250000,500000,1000000):
    while time.time()-t0<1500:
        m=work[0]
        try: f=secm(m,B1=B1,B2=50*B1,max_curve=25)
        except Exception as e: f=None
        print("B1",B1,"elapsed",round(time.time()-t0),"result",f,flush=True)
        if f:
            fs=sorted(f); print("FOUND",fs,flush=True)
            work=[x for x in fs]+work[1:]; break
        break
    if time.time()-t0>=1500 or len(work)>1: break
print("final pieces:",[(int(x).bit_length(),int(x),bool(is_prime(x))) for x in work],flush=True)
