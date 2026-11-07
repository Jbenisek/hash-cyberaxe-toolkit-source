import glob,re,json,math,sys
d=sys.argv[1]; out=sys.argv[2]
R=[]
for f in sorted(glob.glob(d+'/seed_*.txt')):
    t=open(f).read(); m=re.search(r'^CENTRE 0 j=(\d) degG=(\d+) success=(\d)',t,re.M)
    if not m or 'SUMMARY' not in t: continue
    R.append(dict(seed=int(re.search(r'seed_(\d+)',f).group(1)),line=int(m[1]),success=int(m[3]),degG=int(m[2])))
open(out+'.jsonl','w').write(''.join(json.dumps(r)+'\n' for r in R))
def w(k,n,z=1.96):
    p=k/n;dd=1+z*z/n;c=p+z*z/(2*n);r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n));return (c-r)/dd
L=[]
s=''
for j in range(3):
    n=sum(r['line']==j for r in R);k=sum(r['line']==j and r['success'] for r in R);lo=w(k,n);L.append(lo)
    s+='line %d: %d/%d = %.3f, Wilson95 lower %.3f\n'%(j,k,n,k/n,lo)
q=min(L);s+='q_min = %.4f\n'%q
for C in (2,4,6):s+='C=%d: 1-(1-q)^C = %.3f\n'%(C,1-(1-q)**C)
c=1
while 1-(1-q)**c<0.39:c+=1
s+='smallest C clearing 0.39: %d\n'%c
open(out+'.md','w').write('# Per-line sample\nbinary lean_attack, args "1 1 seed j 1", seeds 100000.., j=seed%3\n\n'+s)
print(s)
