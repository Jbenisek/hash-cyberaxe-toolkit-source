import re,glob,math,statistics
def counts(k):
    c=[]
    for f in glob.glob('exact_k%d.out'%k)+glob.glob('exact%d_more.out'%k):
        for l in open(f):
            m=re.match(r'EXACT \S+ ctx \d+: of 2\^32 values of \S+, (\d+) give',l)
            if m:c.append(int(m.group(1)))
    return c
for k,n in ((1,'E_-3'),(2,'E_-2'),(3,'E_-1')):
    c=counts(k); 
    print(n,len(c),c,'mean %.2f sd %.2f se %.2f zero %d'%(statistics.mean(c),statistics.pstdev(c) if len(c)>1 else 0,(statistics.stdev(c)/math.sqrt(len(c))) if len(c)>1 else 0,c.count(0)))
def wil(k,n):
    z=1.96;p=k/n;d=1+z*z/n;ce=p+z*z/(2*n);a=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n));return (ce-a)/d,(ce+a)/d
for k,n in ((1,'E_-3'),(2,'E_-2'),(3,'E_-1')):
    F=D=0
    for f in glob.glob('steer_fix_%d_*.out'%k)+glob.glob('steer_fixbig_%d_*.out'%k):
        for l in open(f):
            m=re.search(r'draws (\d+), cheap-filter pass \d+ .*? rows0\.\.17 (\d+) =',l)
            if m: D+=int(m.group(1));F+=int(m.group(2))
    lo,hi=wil(F,D);print(n,'fixed-constant pooled: draws',D,'pass',F,'2^%.4f [2^%.4f, 2^%.4f]'%(math.log2(F/D),math.log2(lo),math.log2(hi)))
F=D=0
for f in ['steer_big.out','steer_base.out']:
    for l in open(f):
        m=re.search(r'draws (\d+), cheap-filter pass \d+ .*? rows0\.\.17 (\d+) =',l)
        if m: D+=int(m.group(1));F+=int(m.group(2))
lo,hi=wil(F,D);print('base pooled',D,F,'2^%.4f [2^%.4f, 2^%.4f]'%(math.log2(F/D),math.log2(lo),math.log2(hi)))
