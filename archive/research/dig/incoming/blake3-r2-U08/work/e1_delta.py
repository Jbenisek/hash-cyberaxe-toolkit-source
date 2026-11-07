# U08 m5: how E1's a2-tau condition depends on the shift delta5 = w5' - w5 (the cancelled K2 word).
# Criterion (proof.md 9.7, re-derived here and brute-force validated at width 10):
#   exists a with a ^ (a+Delta) = tau  iff  d=(tau-Delta) even, d/2 has no bit outside tau (tau[top]=0);
#   Delta(s) = beta - 2s + delta5   (s = b1 & beta, additive change of b1 is beta-2s; a2'-a2 = db1 + delta5)
import itertools, collections, random, json
M=0xffffffff
def subs(X):
    p=X
    while True:
        yield p
        if p==0: return
        p=(p-1)&X
def ok(tau,Delta,n=32):
    m=(1<<n)-1; d=(tau-Delta)&m
    if d&1: return False
    top=1<<(n-1)
    h=d>>1
    if tau&top: return None
    return (h & ~tau)==0
# brute-force validation of the criterion at width 10 (tau[top]=0)
n=10; m=(1<<n)-1; bad=0; cnt=0
random.seed(1)
for _ in range(400):
    tau=random.randrange(1<<(n-1)); Delta=random.randrange(1<<n)
    brute=any((a^((a+Delta)&m))==tau for a in range(1<<n))
    crit=ok(tau,Delta,n); cnt+=1
    if brute!=crit: bad+=1
print('criterion vs brute force (width 10): mismatches',bad,'of',cnt)
beta=0x18b0e098; beta2=0x18d0e098
taus=[0x175020a0,0x185020a0,0x275020a0,0x285020a0,0x385020a0,0x675020a0,0x685020a0]
print('popcount beta*',bin(beta).count('1'),'popcount tau 285020a0',bin(0x285020a0).count('1'))
print('control (proof 9.7 table 16,32,8,16,32,8,16), delta5=-8:',[sum(1 for s in subs(beta) if ok(t,(beta-2*s-8)&M)) for t in taus])
print('control beta2 285020a0, delta5=-8:',sum(1 for s in subs(beta2) if ok(0x285020a0,(beta2-2*s-8)&M)))
# histogram over every delta5 in 2^32: for each s and each submask p of tau, Delta=tau-2p => delta5=Delta-beta+2s
def hist(beta,tau):
    h=collections.Counter()
    for s in subs(beta):
        for p in subs(tau):
            Delta=(tau-2*p)&M
            h[(Delta-beta+2*s)&M]+=1
    return h
res={}
for name,b in (('beta*',beta),('beta2',beta2)):
    h=hist(b,0x285020a0)
    tot=sum(h.values())
    top=sorted(h.items(),key=lambda kv:-kv[1])[:8]
    dm8=(-8)&M
    print(name,'tau 285020a0: total (s,pattern) pairs',tot,'distinct delta5 values',len(h),'; delta5=-8 ->',h[dm8],'compatible s; delta5=+8 ->',h[8],'; delta5=0 ->',h[0])
    print('  top delta5 by compatible-s count:',[('%08x'%k,v) for k,v in top])
    mx=max(h.values()); print('  max compat s over all delta5:',mx,'attained at',sum(1 for v in h.values() if v==mx),'delta5 values')
    res[name]=dict(total=tot,distinct=len(h),at_m8=h[dm8],at_p8=h[8],at_0=h[0],maxv=mx,n_max=sum(1 for v in h.values() if v==mx),top=[('%08x'%k,v) for k,v in top])
# Distribution of shift sign: with delta5=-8 the fraction of s compatible among 2^11 submasks, and a-freedom
pc=bin(0x285020a0).count('1')
print('given a compatible s: a2 values giving tau: 2^%d of 2^32 -> P=2^-%d; s compatible 16 of 2^%d'%(32-pc,pc,bin(beta).count('1')))
json.dump(res,open('e1_delta_out.json','w'),indent=1)
