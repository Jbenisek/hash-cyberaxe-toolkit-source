import sys
ev=[]
for l in open('/tmp/r2l2/trace_ev.txt'):
    p=l.split()
    if len(p)==3 and p[0]=='A': ev.append(('A',int(p[2]),64+((int(p[1])+63)&~63)))
    elif len(p)==2 and p[0]=='F': ev.append(('F',int(p[1]),0))
print(len(ev),'events',flush=True)
T=196608
def run(ARENA):
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
live=0;peak=0;sz={}
for t,i,need in ev:
    if t=='A': live+=need; sz[i]=need; peak=max(peak,live)
    else: live-=sz.pop(i)
print('peak bytes in use',peak,flush=True)
lo=peak//64; hi=(110<<20)//64
assert run(hi*64) is not None
while lo<hi:
    mid=(lo+hi)//2
    if run(mid*64) is None: lo=mid+1
    else: hi=mid
print('min arena (binary search)',lo*64, 'ratio', lo*64/peak)
print('verify', run(lo*64) is not None, flush=True)
