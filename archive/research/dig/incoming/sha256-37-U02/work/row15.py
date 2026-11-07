# row-15 local model for chi37: derive constants from the published pair with own SHA-256 trace (validated against digest)

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import re,sys,json
M=0xffffffff
K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]
def rr(x,n): return ((x>>n)|(x<<(32-n)))&M
def S0(x): return rr(x,2)^rr(x,13)^rr(x,22)
def S1(x): return rr(x,6)^rr(x,11)^rr(x,25)
def s0(x): return rr(x,7)^rr(x,18)^(x>>3)
def s1(x): return rr(x,17)^rr(x,19)^(x>>10)
def Ch(e,f,g): return (e&f)^(~e&g&M)
def Maj(a,b,c): return (a&b)^(a&c)^(b&c)
def trace(cv,w16,steps=37):
    W=list(w16)
    for t in range(16,steps): W.append((s1(W[t-2])+W[t-7]+s0(W[t-15])+W[t-16])&M)
    a,b,c,d,e,f,g,h=cv
    A=[d,c,b,a]; E=[h,g,f,e]   # rows -4..-1 : A_-4=d? use standard: A_{-1}=a,A_-2=b,A_-3=c,A_-4=d
    A=[d,c,b,a]; E=[h,g,f,e]
    # standard: a=A_{-1}, b=A_{-2}, c=A_{-3}, d=A_{-4}; e=E_{-1}, f=E_-2, g=E_-3, h=E_-4
    A=[d,c,b,a]; E=[h,g,f,e]
    for t in range(steps):
        a_,b_,c_,d_=A[-1],A[-2],A[-3],A[-4]; e_,f_,g_,h_=E[-1],E[-2],E[-3],E[-4]
        T1=(h_+S1(e_)+Ch(e_,f_,g_)+K[t]+W[t])&M
        T2=(S0(a_)+Maj(a_,b_,c_))&M
        E.append((d_+T1)&M); A.append((T1+T2)&M)
    return A[4:],E[4:],W   # index = row t
def load():
    txt=open(_hca_public_path_text('__HCA_WORKSPACE__/research/tools/traillab/chi/chi37.txt')).read()
    d={}
    for k in ('cv','mx','my','digest'):
        m=re.search(r'^'+k+r' (.*)$',txt,re.M); d[k]=[int(x,16) for x in m.group(1).split()]
    return d
if __name__=='__main__':
    d=load()
    for nm in ('mx','my'):
        A,E,W=trace(d['cv'],d[nm])
        # digest check: output = cv + final state (a,b,c,d,e,f,g,h)= A36,A35,A34,A33,E36..E33
        fin=[A[36],A[35],A[34],A[33],E[36],E[35],E[34],E[33]]
        dig=[(x+y)&M for x,y in zip(d['cv'],fin)]
        print(nm,'digest ok' if dig==d['digest'] else 'DIGEST MISMATCH',[hex(x) for x in dig][:2])
    Ax,Ex,Wx=trace(d['cv'],d['mx']); Ay,Ey,Wy=trace(d['cv'],d['my'])
    print('E15x',hex(Ex[15]),'E15y',hex(Ey[15]),'dE15',hex((Ey[15]-Ex[15])&M),'W15x',hex(Wx[15]),'c',hex((Ex[15]-Wx[15])&M))
    print('A15 equal',Ax[15]==Ay[15])
