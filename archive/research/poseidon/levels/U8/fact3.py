# U8: check the split of C412 found by fact2.py and keep trying ECM on the 333-bit remainder (cap 900 s)
import time
from sympy import isprime
from sympy.ntheory import ecm as secm
P=0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
a=487887715480415483992657; b=21186043132281546156793608169660962271252226488966104018788253841360240111557635227669180162173314659
C412=10336410183878389456389411122965216970727148811023702430995384658173246000781176565624088163903039586972430848856941306458963
print("a*b == C412:",a*b==C412,"; a bits",a.bit_length(),"prime",isprime(a),"; b bits",b.bit_length(),"prime",isprime(b),"; a mod 3 =",a%3, flush=True)
print("(p^2+p+1) divisible by a:", (P*P+P+1)%a==0, flush=True)
t0=time.time()
for B1 in (250000,500000,1000000):
    if time.time()-t0>900 or isprime(b): break
    try: f=secm(b,B1=B1,B2=50*B1,max_curve=20)
    except Exception as e: f=None
    print("B1",B1,"elapsed",round(time.time()-t0),"result",f,flush=True)
    if f: print("FOUND",sorted(f),flush=True); break
print("done",flush=True)
