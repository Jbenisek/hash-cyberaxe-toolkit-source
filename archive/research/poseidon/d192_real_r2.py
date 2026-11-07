"""D192 real r=2 sample driver.

Builds the exact degree-5^8 digest polynomial over the audited Orchard line,
forms each centre's odd part of degree 195312, sends only the powering step to
the local RTX 3090 CUDA path, and verifies every returned witness twice.
"""
from __future__ import annotations
import json, math, os, random, shlex, subprocess, sys, time
from pathlib import Path
import flint

HERE = Path(__file__).resolve().parent
REF_DIR = HERE / "orchard" / "impl"
sys.path.insert(0, str(REF_DIR))
from poseidon_ref import hash_reduced  # type: ignore

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
CAPACITY = 1 << 65
R = flint.fmpz_mod_poly_ctx(P); X = R.gen()
CONST = HERE / "pareto_clone" / "pareto" / "orchard-pallas-constants.json"
if not CONST.exists():
    CONST = HERE / "orchard" / "impl" / ".." / ".." / "pareto_clone" / "pareto" / "orchard-pallas-constants.json"
D = json.loads(CONST.read_text())
RC = [[int(x, 16) for x in row] for row in D["round_constants"]]
M = [[int(x, 16) for x in row] for row in D["mds"]]
# The exponent inverse is taken modulo |F*| = P-1, not modulo P.
INV5 = pow(5, -1, P - 1)

def solve2(a,b,c,d,e,f):
    z = pow((a*d-b*c) % P, P-2, P)
    return (e*d-b*f)*z % P, (a*f-e*c)*z % P

def line_setup(j=0):
    cap = pow((CAPACITY + RC[0][2]) % P, 5, P)
    base = [(M[i][2]*cap + RC[1][i]) % P for i in range(3)]
    i,k = [q for q in range(3) if q != j]
    U,V = solve2(M[i][0],M[i][1],M[k][0],M[k][1],-base[i] % P,-base[k] % P)
    Q = [(base[t] + M[t][0]*U + M[t][1]*V) % P for t in range(3)]
    a,b = M[j][1] % P, (-M[j][0]) % P
    Dv = [(M[t][0]*a + M[t][1]*b) % P for t in range(3)]
    assert Q[i] == 0 and Q[k] == 0 and Dv[j] == 0
    return a,b,U,V,Q,Dv

def inputs_for_tau(tau,line):
    a,b,U0,V0,_,_ = line
    U,V = (U0+a*tau)%P, (V0+b*tau)%P
    return (pow(U,INV5,P)-RC[0][0])%P, (pow(V,INV5,P)-RC[0][1])%P

def build_F(line):
    _,_,_,_,Q,Dv = line
    # Exactly one Dv coordinate is zero (the selected line j).  That
    # round-1 S-box input is constant Q[j]; the other two start at zero and
    # are affine in tau, hence contribute Dv[t]^5 * W with W=tau^5.
    sb = [R([pow(Q[t],5,P)]) if Dv[t] == 0 else R([0,pow(Dv[t],5,P)]) for t in range(3)]
    state = [sum((int(M[i][t])*sb[t] for t in range(3)), R([0])) for i in range(3)]
    def full(st,rnd):
        z = [st[t] + RC[rnd][t] for t in range(3)]
        y = [v**5 for v in z]
        return [sum((int(M[i][t])*y[t] for t in range(3)), R([0])) for i in range(3)]
    def partial(st,rnd):
        z = [st[t] + RC[rnd][t] for t in range(3)]
        z = [z[0]**5,z[1],z[2]]
        return [sum((int(M[i][t])*z[t] for t in range(3)), R([0])) for i in range(3)]
    for rnd in (2,3): state = full(state,rnd)
    for rnd in (4,5): state = partial(state,rnd)
    for rnd in range(60,64): state = full(state,rnd)
    F = state[0]
    assert F.degree() == 5**8, (F.degree(),5**8)
    return F

def shifted_coeffs(F,c):
    d = F.degree(); fc = F.coeffs(); fact=[1]*(d+1)
    for i in range(1,d+1): fact[i]=fact[i-1]*i%P
    ifact=[1]*(d+1); ifact[d]=pow(fact[d],P-2,P)
    for i in range(d,0,-1): ifact[i-1]=ifact[i]*i%P
    arev=R([int(fc[d-i])*fact[d-i]%P for i in range(d+1)])
    C=[]; cp=1
    for _ in range(d+1): C.append(cp*ifact[len(C)]%P); cp=cp*c%P
    conv=arev*R(C)
    return [int(conv[d-j])*ifact[j]%P for j in range(d+1)]

def write_poly(poly,path):
    with path.open('wb') as f:
        for x in poly.coeffs(): f.write(int(x).to_bytes(32,'little'))

def read_poly(path):
    b=path.read_bytes(); assert len(b)%32==0
    return R([int.from_bytes(b[i:i+32],'little') for i in range(0,len(b),32)])

def gpu_power(gpath,qpath,logpath):
    def wsl_path(p):
        s = str(Path(p).resolve()).replace('\\','/')
        return '/mnt/' + s[0].lower() + '/' + s[3:]
    d = wsl_path(HERE / "gpu_ntt")
    cmd = f"cd {shlex.quote(d)} && nice -n 10 ./d192_gpu --real-g-r2 {shlex.quote(wsl_path(gpath))} {shlex.quote(wsl_path(qpath))}"
    with logpath.open('w',encoding='utf-8') as out:
        # CUDA is installed in the explicitly selected Ubuntu-22.04 distro;
        # the default WSL distro has a separate runtime and may hang at CUDA init.
        cp=subprocess.run(['wsl.exe','-d','Ubuntu-22.04','bash','-lc',cmd],stdout=out,stderr=subprocess.STDOUT)
    if cp.returncode: raise RuntimeError(f'GPU exit {cp.returncode}')

def square_root(a):
    a %= P
    if a == 0 or pow(a,(P-1)//2,P) != 1: return None
    q,s=P-1,0
    while q%2==0: q//=2; s+=1
    z=5
    while pow(z,(P-1)//2,P)!=P-1: z+=1
    c=pow(z,q,P); r=pow(a,(q+1)//2,P); t=pow(a,q,P); m=s
    while t != 1:
        i,u=1,t*t%P
        while u != 1: u=u*u%P; i+=1
        b=pow(c,1 << (m-i-1),P); r=r*b%P; c=b*b%P; t=t*c%P; m=i
    return r

def main():
    n=int(sys.argv[1]) if len(sys.argv)>1 else 40
    seed=int(sys.argv[2]) if len(sys.argv)>2 else 19220261012
    out=Path(sys.argv[3]) if len(sys.argv)>3 else HERE/'d192_r2_results.jsonl'
    line_idx=int(sys.argv[4]) if len(sys.argv)>4 else 0
    work=HERE/'d192_gpu_work'; work.mkdir(exist_ok=True)
    print('building real r=2 F degree',5**8,'line',line_idx,flush=True); line=line_setup(line_idx); F=build_F(line)
    for tau in (0,1,2,7,12345):
        nk,rho=inputs_for_tau(tau,line); assert int(F.evaluate(pow(tau,5,P)))==hash_reduced(nk,rho,2)
    print('validated_degree',F.degree(),'direct_checks',5,flush=True)
    rng=random.Random(seed); rows=[]; t0=time.time(); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8') as fp:
        for i in range(n):
            c=rng.randrange(P); sh=shifted_coeffs(F,c)
            g=R([sh[2*k+1] for k in range((F.degree()+1)//2)]).monic()
            gp=work/f'g_{i:03d}.bin'; qp=work/f'q_{i:03d}.bin'; lp=work/f'gpu_{i:03d}.txt'; write_poly(g,gp)
            t1=time.time(); gpu_power(gp,qp,lp); q=read_poly(qp); gpu_s=time.time()-t1
            t2=time.time()
            H=g.gcd((q-1)%g); roots=g.gcd((X*((q*q-1)%g))%g); rep=g.gcd(g.derivative())
            verified=[]
            for root,_ in H.roots()[:4]:
                s=square_root(int(root))
                if not s: continue
                wp,wm=(c+s)%P,(c-s)%P
                nk,rho=inputs_for_tau(pow(wp,INV5,P),line); nk2,rho2=inputs_for_tau(pow(wm,INV5,P),line)
                d1=hash_reduced(nk,rho,2); d2=hash_reduced(nk2,rho2,2); assert d1==d2 and (nk,rho)!=(nk2,rho2)
                verified.append({'S':int(root),'digest':int(d1),'inputs_distinct':True})
            gcd_s=time.time()-t2
            row={'index':i,'line':line_idx,'seed':seed,'center':str(c),'gpu_seconds':round(gpu_s,3),'gcd_seconds':round(gcd_s,3),'roots':int(roots.degree()),'nonzero_square_roots':int(H.degree()),'squarefree':rep.degree()==0,'verified':verified}
            fp.write(json.dumps(row,sort_keys=True)+'\n'); fp.flush(); rows.append(row)
            print('centre',i,'roots',row['roots'],'nonzero_square',row['nonzero_square_roots'],'squarefree',row['squarefree'],'gpu_s',row['gpu_seconds'],'verified',len(verified),flush=True)
    k=sum(r['nonzero_square_roots']>0 for r in rows); print('SUMMARY',json.dumps({'n':n,'success':k,'fraction':k/n if n else None,'wilson95_lower':None,'expected':1-math.exp(-.5),'elapsed_s':round(time.time()-t0,3),'out':str(out)}),flush=True)

if __name__=='__main__': main()
