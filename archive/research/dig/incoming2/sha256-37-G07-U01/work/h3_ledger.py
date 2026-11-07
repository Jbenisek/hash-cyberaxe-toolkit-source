# own: ledger sensitivity of the H3 premise delta (shipped pkgR37X ledger, Section 11 / H7 formulas)
from decimal import Decimal as D, getcontext
import math
getcontext().prec=60
A=D(2)**60+D(2)**50+D(2)**40; C=D(2644); vbar=D(95646); vmax_fb=D(1077541006432); PRE=D(2)**58; FIN=D(1606); s=1/D(3680)
def T_of(N):
    V=((1+s)*N*vbar).to_integral_value(rounding='ROUND_CEILING')
    return A+N+(N*232+V+vmax_fb+PRE+FIN)/C+6
Nprinted=D(3869945863831380)
print("T(printed N_FB) log2 =", math.log2(T_of(Nprinted)), "(printed 60.171440)")
def Pcap(N,s=s): return (-(s*s*N*vbar)/(2*vmax_fb*(1+s/3))).exp()
def mu0(delta,N):
    return -(D(1)-D(0.61)*0-0).ln() if False else -(D('0.61')-Pcap(N)-D(2)**-60).ln()/(1-delta/2)
Nref_mu=D('0.49466752'); 
def Nfb(delta):
    N=Nprinted
    for _ in range(5):
        m=mu0(delta,N); N=Nprinted*m/mu0(D(2)**D('-9.4'),Nprinted)   # N_FB proportional to mu0 (g,q3 fixed)
    return N
base=math.log2(T_of(Nfb(D(2)**D('-9.4'))))
print("base log2T at delta=2^-9.4:",base)
for lg in [-9.4,-9.415,-9.585,-9.68,-10,-11,-8,-7,-6]:
    d=D(2)**D(str(lg)); print("delta 2^%.3f"%lg, "mu0 %.8f"%mu0(d,Nprinted), "log2T %.6f"%math.log2(T_of(Nfb(d))), "dT(bit) %+.6f"%(math.log2(T_of(Nfb(d)))-base))
# charged pieces
a=2**-11; b=2**35*2**20.0*2**5*2**-70
print("H3(a)+(b) charged: 2^-11 + 2^-10.0 =",a+b,"= 2^%.4f ; bound 2^-9.4 = %.7f ; margin %.4f bit"%(math.log2(a+b),2**-9.4,math.log2(2**-9.4/(a+b))))
print("with size-biased 127,978 and no allowance 2^3: (b) = 2^35*127978*2^2*2^-70 ->",2**35*127978*4*2**-70, "=2^%.3f"%math.log2(2**35*127978*4*2**-70))
# the unit sensitivity
for dl in [1e-4,1e-3]:
    d1=D(2)**D('-9.4')+D(dl); print("delta +%g absolute: dlog2T %.7f"%(dl, math.log2(T_of(Nfb(d1)))-base))
print("elasticity of log2T to log2 N_FB:", (math.log2(T_of(Nprinted*D('1.01')))-math.log2(T_of(Nprinted)))/math.log2(1.01))
