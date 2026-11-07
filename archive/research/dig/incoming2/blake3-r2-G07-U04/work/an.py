import sys,glob,math
DIV=20802.919921875
def load(files,skip=None):
    R=[]
    for fn in files:
        for l in open(fn):
            p=l.split()
            if len(p)>=6 and p[0].lstrip('-').isdigit(): R.append(tuple(map(int,p[:6])))
    return R
def stats(R,div=DIV):
    n=len(R); w=sum(r[1] for r in R); k=sum(r[2] for r in R)
    x=[r[3]/div for r in R]; m=sum(x)/n; v=sum((a-m)**2 for a in x)/(n-1); se=math.sqrt(v/n)
    return dict(n=n,words=w,pf=k,kept=k/w if w else None,lf=m,se=se,lo6=m-6*se,mm=sum(r[4] for r in R),halt=sum(r[5] for r in R))
if __name__=="__main__":
    print(stats(load(sys.argv[1:])))
