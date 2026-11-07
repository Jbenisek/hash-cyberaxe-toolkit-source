import sys
ev=[]
for l in open('logs/trace2_run.txt'):
    p=l.split()
    if len(p)==3 and p[0]=='A': ev.append(('A',int(p[2]),64+((int(p[1])+63)&~63)))
    elif len(p)==2 and p[0]=='F': ev.append(('F',int(p[1]),0))
print(len(ev))
def run(ARENA,T):
    H={0:[ARENA,0,0]}; ids={}; ext=0
    for t,i,need in ev:
        if t=='A':
            small=need<=T; cand=None; o=0
            while o<ARENA:
                b,pv,u=H[o]
                if not u and b>=need:
                    cand=o
                    if not small: break
                o+=b
            if cand is None: return None
            o=cand; b=H[o][0]; rem=b-need
            if rem>=128:
                nn=o+b
                if small:
                    n=o+rem; H[o][0]=rem; H[n]=[need,rem,1]
                    if nn<ARENA: H[nn][1]=need
                    o=n
                else:
                    n=o+need; H[n]=[rem,need,0]
                    if nn<ARENA: H[nn][1]=rem
                    H[o][0]=need; H[o][2]=1
            else:
                H[o][2]=1
            ids[i]=o; ext=max(ext,o+H[o][0])
        else:
            o=ids.pop(i); b,pv,u=H[o]; H[o][2]=0
            n=o+b
            if n<ARENA and not H[n][2]:
                b+=H[n][0]; H[o][0]=b; del H[n]; nn=o+b
                if nn<ARENA: H[nn][1]=b
            if pv:
                po=o-pv
                if not H[po][2]:
                    pb=pv+b; H[po][0]=pb; del H[o]; nn=po+pb
                    if nn<ARENA: H[nn][1]=pb
    return ext
def minarena(T):
    lo,hi=8469440//64,9500000//64
    if run(hi*64,T) is None: return None
    while lo<hi:
        mid=(lo+hi)//2
        if run(mid*64,T) is None: lo=mid+1
        else: hi=mid
    return lo*64
for T in (131135,196671,262207,393279):
    m=minarena(T); print(T,m,flush=True)
