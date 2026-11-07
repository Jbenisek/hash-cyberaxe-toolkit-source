
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

import sys,random,struct,collections
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgB3U/pkg/blake3-r2/experiments'))
import frontline as F
M=0xffffffff; ror=F.ror
out=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.append(s)
PERM=F.PERM; GC=F.GCALLS; IV=F.IV
def gq(a,b,c,d,x,y):
    a=(a+b+x)&M; d=ror(d^a,16); q1=(a,d)
    c=(c+d)&M; b=ror(b^c,12); q2=(c,b)
    a=(a+b+y)&M; d=ror(d^a,8); q3=(a,d)
    c=(c+d)&M; b=ror(b^c,7); q4=(c,b)
    return a,b,c,d,(q1,q2,q3,q4)
def run(w,t,n,flags,inject=None):
    """returns per (round,call) quarter outputs; inject=(word,xor) applied to state before round 2 (index 1)"""
    v=list(IV)+list(IV[:4])+[t&M,t>>32,n,flags]
    s=list(w); tr={}
    for r in range(2):
        if r==1 and inject: v[inject[0]]^=inject[1]
        for i,(a,b,c,d) in enumerate(GC):
            v[a],v[b],v[c],v[d],q=gq(v[a],v[b],v[c],v[d],s[2*i],s[2*i+1])
            tr[(r,i)]=q
        if r==0: mid=list(v)
        s=[s[p] for p in PERM]
    return tr,[v[i]^v[i+8] for i in range(8)],mid,v
names=['K0','K1','K2','K3','D0','D1','D2','D3','C0','C1','C2','C3','E0','E1','E2','E3']
def key(r,i): return names[(r*8+i)] if False else None
# grid: round0 cols K0-3, round0 diags D0-3, round1 cols C0-3, round1 diags E0-3
def callname(rnd,i): return names[rnd*8+i]  # rnd 0 -> K(0-3)/D(4-7) ; rnd1 -> C/E
def ctx(seed):
    random.seed(seed)
    ow=[random.getrandbits(32) for _ in range(7)]
    e1,y=F.member(random.getrandbits(19)); v=F.rebuild(ow,y,e1); u=F.step_ct(v,random.getrandbits(32))
    return u
def words(msg): return list(struct.unpack('<16I',msg+bytes(64-len(msg))))
N=300
act=collections.Counter()
for sd in range(N):
    u=ctx(sd); t=u['t']
    wa,wb=words(u['A']),words(u['B'])
    ta,cva,_,_=run(wa,t,55,3); tb,cvb,_,_=run(wb,t,63,3)
    assert [cva[i] for i in (0,2,5,7)]==[cvb[i] for i in (0,2,5,7)]
    for k in ta:
        for q in range(4):
            for j in range(2):
                if ta[k][q][j]!=tb[k][q][j]: act[(k,q+1)]+=1
P('BASELINE trace over %d random constructed pairs (frontline CO/CT/CS, words 0,2,5,7 equal in all): fraction of pairs with a nonzero A^B at each quarter-step (non-listed = 0 of %d)'%(N,N))
for rnd in (0,1):
    for i in range(8):
        row=[act[((rnd,i),q)] for q in (1,2,3,4)]
        P('  %s q1..q4 nonzero counts: %s'%(names[rnd*8+i],row))
P('E1 q1 (a1,d1) nonzero count over %d pairs: %d  -> structurally zero in every constructed pair'%(N,act[((1,5),1)]))
# --- Relaxation: where could a nonzero diff in E1's a1/d1 come from? exact dependence + injection test
# E1 = G5 of round 2 = GCALLS[5]=(1,6,11,12); a1=v1+v6+m, d1=ror(v12^a1,16): depends on v1,v6,v12 at round-2 diag start.
# those are outputs of C1.a, C2.b, C0.d; each G output depends on all 4 inputs (check numerically below)
dep={}
for out_i,name in enumerate('abcd'):
    for in_i,nm in enumerate('abcd'):
        base=[random.getrandbits(32) for _ in range(6)]; ch=0
        for tr in range(200):
            base=[random.getrandbits(32) for _ in range(6)]
            x=base[:4]; y=list(x); y[in_i]^=1<<random.randrange(32)
            r1=gq(*x,base[4],base[5])[:4]; r2=gq(*y,base[4],base[5])[:4]
            if r1[out_i]!=r2[out_i]: ch=1;break
        dep[(name,nm)]=ch
P('G dependence (outputs a,b,c,d vs inputs a,b,c,d) all 16 true:',all(dep.values()))
P('  => E1.a1/d1 input words v1,v6,v12 are outputs of C1,C2,C0, each depending on all four of its round-2-start words; nonzero Delta(a1,d1) needs a nonzero difference in round-2-start state outside C3 inputs, i.e. leaving the Lemma L cancellation / pinned D-outputs')
# which message words differ between A and B: only w4,w5 (word-level)
u=ctx(1); wa,wb=words(u['A']),words(u['B'])
P('message words that differ A vs B:',[i for i in range(16) if wa[i]!=wb[i]],'(w4 diff and w5 = w5-8); initial v14 = block length 55/63')
# state after round 1 (K,D) equal?
ta,cva,mida,_=run(wa,u['t'],55,3); tb,cvb,midb,_=run(wb,u['t'],63,3)
P('state words differing after round 1 (before C):',[i for i in range(16) if mida[i]!=midb[i]],'(none expected: Lemma L cancellation + pinned constants)')
# Injection: flip one bit in word k of B's round-2 start state (as if round 1 did not cancel), count active calls/steps and output equality
res=collections.defaultdict(lambda:[0,0,0,collections.Counter()])
NI=40
tot_inj=0
for sd in range(NI):
    u=ctx(1000+sd); t=u['t']; wa,wb=words(u['A']),words(u['B'])
    ta,cva,_,_=run(wa,t,55,3); tb0,cvb0,_,_=run(wb,t,63,3)
    for k in range(16):
        for bt in (0,15,31):
            tb,cvb,_,_=run(wb,t,63,3,inject=(k,1<<bt))
            actc=set(); 
            for (r,i),q in ta.items():
                if r==1 and any(q[s][j]!=tb[(r,i)][s][j] for s in range(4) for j in range(2)): actc.add(names[8+i])
            eq=sum(cva[i]==cvb[i] for i in (0,2,5,7))
            res[k][0]+=len(actc); res[k][1]+=1; res[k][2]+=(eq==4)
            for c in actc: res[k][3][c]+=1
            tot_inj+=1
P('INJECTION of a one-bit difference into round-2-start word k of B (%d trials per word; baseline active calls in round 2 are C3 and E1,E3 per the construction):'%(NI*3))
for k in range(16):
    r=res[k]; P('  v%-2d: mean #round-2 calls with nonzero output diff = %.2f ; words 0,2,5,7 still equal in %d/%d ; calls hit: %s'%(k,r[0]/r[1],r[2],r[1],dict(r[3])))
open('q1relax_out.txt','w').write('\n'.join(out)+'\n')
