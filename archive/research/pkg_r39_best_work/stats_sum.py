import json, glob, re, math
S=[json.load(open(f)) for f in glob.glob('stats/s_*.json')]; S.sort(key=lambda s:s['seed'])
L={}
for f in glob.glob('led/win_*.txt'):
    m=re.search(r'(\d+) distinct claws', open(f).read()); L[int(re.search(r'win_(\d+)',f).group(1))*1000]=int(m.group(1))
bad=[s['seed'] for s in S if L.get(s['seed'])!=s['claws']]
print('windows',len(S),'claws match ledger in all:', not bad, bad)
N=sum(s['claws'] for s in S); f9=sum(s['f9'] for s in S); f8=sum(s['f8'] for s in S); bo=sum(s['both'] for s in S)
p9=52.65/3318; p8=233.30/3318; pj=3.70/3318     # the program's own expected rates (WIN_EXP 'expected' line)
z=lambda o,n,p:(o-n*p)/math.sqrt(n*p*(1-p))
print(f'N {N:,}  W9inF9 {f9:,} ({f9/N:.5f} vs {p9:.5f}, z={z(f9,N,p9):.2f})  W8inF8 {f8:,} ({f8/N:.5f} vs {p8:.5f}, z={z(f8,N,p8):.2f})  both {bo:,} ({bo/N:.6f} vs {pj:.6f}, z={z(bo,N,pj):.2f})')
for k in (8,12,16,20,24):
    o=sum(s['low'][str(k)] for s in S); print(f'  W17 low-{k} matches {o:,} (expected {N/2**k:.2f})')
def chi(h): e=sum(h)/len(h); return sum((c-e)**2/e for c in h)
def agg(key): h=[0]*len(S[0][key]); [h.__setitem__(i,h[i]+v) for s in S for i,v in enumerate(s[key])]; return h
for key,df in (('lo16',65535),('hi16',65535),('w18',255)):
    c=chi(agg(key)); print(f'  chi-square {key}: {c:.1f} on {df} df, z = {(c-df)/math.sqrt(2*df):.2f}')
zs=[(chi(s['lo16'])-65535)/math.sqrt(2*65535) for s in S]
ss=sum(x*x for x in zs); print(f'  per-window lo16 z: {min(zs):.2f} .. {max(zs):.2f}, mean {sum(zs)/len(zs):.2f}, mean square {ss/len(zs):.2f}; sum of squares {ss:.1f} on {len(zs)} df = {(ss-len(zs))/math.sqrt(2*len(zs)):.1f} sigma')
c9=sum((s['f9']-s['claws']*p9)**2/(s['claws']*p9*(1-p9)) for s in S); c8=sum((s['f8']-s['claws']*p8)**2/(s['claws']*p8*(1-p8)) for s in S)
print(f'  binomial chi-square over windows: F9 {c9:.1f}, F8 {c8:.1f} on {len(S)-1} df')
adj=sum(s['adj9'] for s in S); exp_adj=sum((s['claws']-1)*(s['f9']/s['claws'])**2 for s in S)
print(f'  F9 adjacent pairs {adj:,} vs {exp_adj:.1f} expected')
