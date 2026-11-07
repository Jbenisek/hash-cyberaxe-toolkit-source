import sys
ev=[]
for l in open('logs/trace_run.txt'):
    p=l.split()
    if p and p[0]=='A' and len(p)==3: ev.append(('A',int(p[1]),int(p[2])))
    elif p and p[0]=='F' and len(p)==2: ev.append(('F',int(p[1]),0))
print(len(ev),'events', sum(1 for e in ev if e[0]=='A'),'allocs')
BIG=1<<40
def sim(policy, ARENA=BIG):
    # blocks: list of [off,size,used,id]
    blocks=[[0,ARENA,False,None]]
    ext=0; ids={}
    live=0; peak=0
    for k,(t,off,sz) in enumerate(ev):
        if t=='A':
            need=sz  # block size as traced (first-fit sizes may include unsplit slack; recompute from need)
            cands=[i for i,b in enumerate(blocks) if not b[2] and b[1]>=need]
            if not cands: return None
            if policy=='first': i=cands[0]
            elif policy=='best': i=min(cands,key=lambda i:(blocks[i][1],blocks[i][0]))
            elif policy=='last': i=cands[-1]
            elif policy=='topfirst': i=cands[-1]
            elif policy.startswith('split'):
                T=int(policy[5:]); i=cands[0] if need>=T else cands[-1]
            elif policy.startswith('bsplit'):
                T=int(policy[6:]); i=min(cands,key=lambda i:(blocks[i][1],blocks[i][0])) if need>=T else cands[-1]
            b=blocks[i]; rem=b[1]-need
            if (policy=='topfirst' or (policy.startswith('split') and need<int(policy[5:])) or (policy.startswith('bsplit') and need<int(policy[6:]))) and rem>=128:
                # carve from the top end of the free block
                blocks[i]=[b[0],rem,False,None]; blocks.insert(i+1,[b[0]+rem,need,True,off]); idx=i+1
            elif rem>=128:
                blocks[i]=[b[0],need,True,off]; blocks.insert(i+1,[b[0]+need,rem,False,None]); idx=i
            else:
                b[2]=True; b[3]=off; idx=i
            ext=max(ext,blocks[idx][0]+blocks[idx][1]); live+=blocks[idx][1]; peak=max(peak,live)
        else:
            i=next(j for j,b in enumerate(blocks) if b[2] and b[3]==off)
            live-=blocks[i][1]; blocks[i][2]=False; blocks[i][3]=None
            if i+1<len(blocks) and not blocks[i+1][2]:
                blocks[i][1]+=blocks[i+1][1]; del blocks[i+1]
            if i>0 and not blocks[i-1][2]:
                blocks[i-1][1]+=blocks[i][1]; del blocks[i]
    return ext,peak

def minarena(pol):
    lo,hi=8400000//64,9500000//64
    if sim(pol,hi*64) is None: return None
    while lo<hi:
        mid=(lo+hi)//2
        if sim(pol,mid*64) is None: lo=mid+1
        else: hi=mid
    return lo*64
import sys
for T in (156353,196673,262209,393281,524353):
    print('bsplit%d'%T, minarena('bsplit%d'%T), flush=True)
