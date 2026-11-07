# validation + tree enumerator (own tree walker, same logic as organizer verifier but instrumented)

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

import sys,random,struct
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash')); sys.path.insert(0,'.')
from verifier import blake3 as vb
from b3lib import *
CS,CE,PA,RT=1,2,4,8
def comp(h,w,t,b,f,r):
    st,o=compress(h,w,t&M,t>>32,f,r) if False else compress(h,w,t&M,t>>32,f,r)
    # compress() returns (st, digest8) with n=block_len passed as 3rd arg; fix argument order below
    return None
def cmp8(h,w,t,b,f,r):
    # compress(h,w,n,tlo,thi,flags,rounds): n = block_len
    st,o=compress(list(h),list(w),b,t&M,t>>32,f,r)
    # CV = digest first 8 words (v[i]^v[i+8]) -- same as verifier's first 8 outputs
    return o
def chunk_out(chunk,ctr,r,log):
    cv=list(IV); last=max(0,(len(chunk)-1)//64*64)
    for off in range(0,last+1,64):
        blk=chunk[off:off+64]; fl=CS if off==0 else 0
        w=struct.unpack('<16I',blk.ljust(64,b'\0'))
        if off==last: return cv,w,ctr,len(blk),fl|CE
        cv=cmp8(cv,w,ctr,64,fl,r); log.append(('chunkblk',ctr,off//64,fl))
def tree(data,r,log):
    cc=max(1,(len(data)+1023)//1024); stack=[]
    for c in range(cc-1):
        out=chunk_out(data[c*1024:(c+1)*1024],c,r,log)
        cv=cmp8(*out,r); log.append(('chunkend',c,out[4]))
        tot=c+1
        while tot&1==0:
            cv=cmp8(IV,stack.pop()+cv,0,64,PA,r); log.append(('parent',)); tot>>=1
        stack.append(cv)
    out=chunk_out(data[(cc-1)*1024:],cc-1,r,log)
    while stack:
        cv=cmp8(*out,r); log.append(('lastchunkend',out[4]))
        out=(IV,tuple(stack.pop())+tuple(cv),0,64,PA)
        if stack: raise SystemExit('unexpected')  # only reached once per loop; handled below
    return out
def tree2(data,r):
    log=[]; cc=max(1,(len(data)+1023)//1024); stack=[]
    for c in range(cc-1):
        out=chunk_out(data[c*1024:(c+1)*1024],c,r,log)
        cv=cmp8(*out,r); log.append(('chunk_end',c))
        tot=c+1
        while tot&1==0:
            cv=cmp8(IV,stack.pop()+cv,0,64,PA,r); log.append(('parent_nonroot',)); tot>>=1
        stack.append(cv)
    out=chunk_out(data[(cc-1)*1024:],cc-1,r,log)
    while stack:
        cv=cmp8(*out,r); log.append(('chunk_end',cc-1))
        out=(IV,tuple(stack.pop())+tuple(cv),0,64,PA)
    h,w,_,b,f=out
    o=cmp8(h,w,0,b,f|RT,r)
    log.append(('ROOT',f|RT,b,'h=IV' if tuple(h)==tuple(IV) else 'h=CV'))
    return struct.pack('<8I',*o),log
if __name__=='__main__':
    # known vector
    d,_=tree2(b'',7); assert d.hex()=='af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262'; print('known BLAKE3 empty vector (7 rounds) ok')
    rng=random.Random(5); n=0
    lens=[0,1,55,63,64,65,127,128,129,1023,1024,1025,1088,2047,2048,2049,3072,3073,4096,4097,5000,8192,8193]
    for r in (2,7):
        for L in lens:
            for _ in range(3):
                dd=bytes(rng.randrange(256) for _ in range(L))
                assert tree2(dd,r)[0]==vb.blake3(dd,r),(r,L); n+=1
    print('own tree walker == organizer verifier on',n,'messages (rounds 2 and 7, lengths up to 8193)')
