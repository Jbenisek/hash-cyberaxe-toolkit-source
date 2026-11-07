import json,sys,math
fs=sys.argv[1:]; ds=[json.load(open(f)) for f in fs]
def z(c,e): return (c-e)/math.sqrt(e) if e>=1 else float('nan')
keys=ds[0]['cells'].keys()
out=[]
for k in keys:
    zs=[z(*d['cells'][k]) for d in ds]; es=[d['cells'][k][1] for d in ds]
    obs=[d['cells'][k][0] for d in ds]
    if max(es)>=5 and any(abs(x)>4 for x in zs if x==x): out.append((k,obs,[round(e,1) for e in es],[round(x,1) for x in zs]))
print(len(keys),'cells; flagged (|z|>4, E>=5):',len(out))
for o in sorted(out,key=lambda o:o[0].count(',')): print(*o)
# zero cells with big E
print('ZERO cells (all seeds obs=0, E>=20), minimal ones:')
zs=[k for k in keys if all(d['cells'][k][0]==0 for d in ds) and min(d['cells'][k][1] for d in ds)>=20]
mins=[k for k in zs if not any(set(j.split('|')[1].split(','))<set(k.split('|')[1].split(',')) and j.split('|')[0]==k.split('|')[0] for j in zs)]
print(mins)
