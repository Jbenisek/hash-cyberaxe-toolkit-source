import re,json,math
def parse(f):
    s=open(f,encoding='utf-8').read()
    return ([float(x) for x in re.findall(r'prefix log2 P\(rows 6\.\.21\) = (-?[\d.]+)',s)],
            [int(x) for x in re.findall(r'EXACT\s+zero output difference after the last step:\s+(\d+)',s)],
            [int(x) for x in re.findall(r'cells\s+rows 22\.\.37:\s+(\d+)',s)])
def get(n,base=False):
    a=parse('out/_regression_base.txt' if n=='base' else 'out/%s.txt'%n)
    b=parse('out2/%s.txt'%n)
    return [a[i]+b[i] for i in range(3)]
B=get('base'); bp=sum(B[0])/4; bx=sum(B[1])
print('base',bp,bx,sum(B[2]),B[0],B[1])
R={'base':dict(pre=bp,ex=bx,cells=sum(B[2]),pre_each=B[0],ex_each=B[1])}
tot=0
for n in ['A17_p01','A17_p02','E21_p01','E21_p02']:
    p,e,c=get(n); pp=sum(p)/4
    w=[2**(p[i]-B[0][i])*e[i]/B[1][i] for i in range(4)]  # per seed weight
    # pooled weight: mean prefix-diff, total ex ratio
    wt=2**(pp-bp)*sum(e)/bx
    sd=(sum((x-sum(w)/4)**2 for x in w)/3)**.5
    R[n]=dict(pre=pp,pre_each=p,ex=sum(e),ex_each=e,cells=sum(c),delta_pre=pp-bp,weight=wt,weight_seed_sd=sd)
    print(n,'pre %.3f d %+.3f EX %d (base %d) weight %.5f per-seed %s'%(pp,pp-bp,sum(e),bx,wt,['%.4f'%x for x in w]))
json.dump(R,open('pooled4.json','w'),indent=1)
