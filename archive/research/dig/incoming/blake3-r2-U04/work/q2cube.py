
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

import sys,random,collections
import numpy as np
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgB3U/pkg/blake3-r2/experiments'))
import frontline as F
M=0xffffffff; D=F.DY11
ror=F.ror; rol=F.rol
out=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.append(s)
# --- Q3: exact carry DP over c1 -> X=c^(c+D), beta=ror(X,12)
# state = carry into bit i. count paths with multiplicity.
def dp_all():
    # dict (carry) -> {Xprefix: count}; too big (distinct X count?) -> count distinct X and multiplicity classes via path DP
    # paths: (carry_i) -> next carry options by c_i
    # number of distinct X = number of carry sequences (X bit = d_i ^ carry_i, carry_0=0); carry seq determines X bijectively.
    # count of c for a sequence = 2^(#positions with forced transition)
    from collections import defaultdict
    st={ (0,0):1 }   # (carry, nforced) -> number of sequences
    for i in range(32):
        d=(D>>i)&1; ns=defaultdict(int)
        for (cy,nf),cnt in st.items():
            nxt=defaultdict(int)
            for ci in (0,1):
                nxt[(ci&d)|(ci&cy)|(d&cy)]+=1   # maj
            for k,mult in nxt.items():
                ns[(k, nf+(1 if mult==2 else 0))]+=cnt
        st=ns
    return st
st=dp_all()
distinct=sum(st.values()); tot=sum(cnt*(1<<nf) for (cy,nf),cnt in st.items())
P('Q3 DP: distinct beta values over all 2^32 c1 =',distinct,' total c1 covered =',tot,'(must be 2^32=%d)'%(1<<32))
byfree=collections.Counter()
for (cy,nf),cnt in st.items(): byfree[32-nf]+=cnt   # fixed bits = 32-nf ; cube dim = nf
P('Q3 distribution: cube dimension (free c1 bits) -> number of betas:',sorted(((k,v) for k,v in collections.Counter({nf:cnt for (cy,nf),cnt in st.items()}.items()).items())) if False else sorted(collections.Counter({}).items()))
dimcount=collections.Counter()
for (cy,nf),cnt in st.items(): dimcount[nf]+=cnt
P('  free-dimension nf : #betas ->',dict(sorted(dimcount.items())))
P('  betas with dim 21 (11 fixed bits):',dimcount[21],' -> includes beta* and beta2')
# --- validation of DP vs brute force on beta* and beta2
def count_for(beta):
    X=rol(beta,12); cy=0; nf=0; seq=0; ok=True
    # reconstruct carry seq from X: X_i = d_i ^ carry_i
    cur=0
    for i in range(32):
        cyi=((X>>i)&1)^((D>>i)&1)
        if i==0 and cyi!=0: return 0
        if i>0:
            # transition from cur -> cyi possible?
            d=(D>>(i-1))&1; opts=set((c&d)|(c&cur)|(d&cur) for c in (0,1))
            if cyi not in opts: return 0
            if len(opts)==1: nf+=1
        cur=cyi
    # final transition (bit 31 -> carry out) has no X bit: both ci allowed -> free if forced
    d=(D>>31)&1; opts=set((c&d)|(c&cur)|(d&cur) for c in (0,1))
    if len(opts)==1: nf+=1
    return 1<<nf
P('Q3 DP check beta* count =',count_for(F.BETA),' beta2 count =',count_for(F.BETA2),' (C brute force over 2^32: 2097152 each, 0 mismatches vs cube mask: cube.c / cube_out.txt)')
# rate
P('Q3 rate: P(c1 in Q*) = 2^21/2^32 = 2^-11 exactly (c1 uniform under the translation by Y11, proof Lemma S1); x2^11 rate when c1 is prescribed in Q*')
# --- real pair check: c1 in Q* gives diff beta* on E1 b1; c1 outside gives other
random.seed(5)
def pair(c1):
    ow=[random.getrandbits(32) for _ in range(7)]
    e1,y=F.member(random.getrandbits(19)); v=F.rebuild(ow,y,e1); u=F.step_ct(v,c1)
    ch=F.chart(u); return ch
def inq(mask,val):
    j=random.getrandbits(32); c=(j&~mask&M)|val; return c
ok=0;n=40
for _ in range(n):
    ch=pair(inq(0x0e09818b,0x02008000)); ok+= (ch['cons'] and (ch['ea'][1]^ch['eb'][1])==F.BETA)
P('real-pair check (organizer-style reconstruction via frontline.step_ct): c1 in Q* -> E1 b1 diff == beta*:',ok,'/',n)
ok=0
for _ in range(n):
    ch=pair(inq(0x0e09818d,0x02008001)); ok+= (ch['cons'] and (ch['ea'][1]^ch['eb'][1])==F.BETA2)
P('real-pair check: c1 in Q_2 -> beta2:',ok,'/',n)
# --- Q2: necessity of each of 11 fixed bits; exact over carries (enumerate relaxed cube of 2^22)
mask=0x0e09818b; val=0x02008000
fixed=[i for i in range(32) if mask>>i&1]
freepos=[i for i in range(32) if not mask>>i&1]
base=np.zeros(1<<21,dtype=np.uint64)
idx=np.arange(1<<21,dtype=np.uint64)
for n_,p in enumerate(freepos): base|=((idx>>np.uint64(n_))&np.uint64(1))<<np.uint64(p)
base|=np.uint64(val)
def beta_of(c):
    c=c.astype(np.uint64); x=(c^((c+np.uint64(D))&np.uint64(M)))&np.uint64(M)
    return (((x<<np.uint64(32-12))|(x>>np.uint64(12)))&np.uint64(M)) if False else (((x>>np.uint64(12))|(x<<np.uint64(20)))&np.uint64(M))
b0=beta_of(base); assert (b0==F.BETA).all()
P('Q2 base: all 2^21 cube members give beta* (numpy re-check):',bool((b0==F.BETA).all()))
rows=[]
for i in fixed:
    flipped=base^np.uint64(1<<i)     # that bit toggled: the other half of the relaxed cube
    bf=beta_of(flipped); vals,cnts=np.unique(bf,return_counts=True)
    top=sorted(zip(cnts.tolist(),vals.tolist()),reverse=True)[:3]
    diffbits=bin(int(vals[0])^F.BETA).count('1') if len(vals)==1 else None
    rows.append((i,len(vals),int((bf==F.BETA).sum()),[(c,'%08x'%v) for c,v in top],('%08x'%(int(vals[0])^F.BETA)) if len(vals)==1 else 'multi'))
    P('  bit %2d (needs c1[%d]=%d): flipping gives %d distinct betas, %d of 2^21 still beta*, top %s, xor to beta* %s'%(i,i,(val>>i)&1,len(vals),int((bf==F.BETA).sum()),[(c,'%08x'%v) for c,v in top],rows[-1][4]))
nec=all(r[2]==0 for r in rows)
P('Q2 result: each of the 11 cube bits is individually necessary (flip -> beta != beta*):',nec,'; beta2 reachable by flipping bit(s)?',[r[0] for r in rows if any(v=='%08x'%F.BETA2 for _,v in r[3])])
# pairs of bits: is any proper subset of 11 enough? exact: number of c1 with beta==beta* is exactly 2^21 -> equals full 11-bit cube, so no subset is sufficient
P('Q2: sufficiency exact: #c1 with beta=beta* over all 2^32 =2^21 = size of the 11-bit cube, so no 10-bit subset suffices (C brute force).')
open('q2cube_out.txt','w').write('\n'.join(out)+'\n')
