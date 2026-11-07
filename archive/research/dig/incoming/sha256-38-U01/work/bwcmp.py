import re,glob,os,json
def parse(f):
    d={};row=None;k=0
    for l in open(f,encoding='utf-8'):
        m=re.match(r'== row (\d+) ==',l)
        if m: row=int(m.group(1));k=0;continue
        m=re.match(r'\s+needed X = (\w+) : Pr (\S+)',l)
        if m:
            d[(row,'E' if k==0 else 'A')]=(m.group(1),float(m.group(2)));k+=1
    return d
base=parse('bw/base.txt');out={}
for f in sorted(glob.glob('bw/*_p*.txt')):
    n=os.path.basename(f)[:-4];d=parse(f);diff=[]
    prod_b=1;prod_v=1
    for key in sorted(base):
        if d.get(key)!=base[key]:
            diff.append('r%d%s: %s Pr %g -> %s Pr %g'%(key[0],key[1],base[key][0],base[key][1],d[key][0],d[key][1]))
    # product of Pr over rows 17..25 E and A, ratio
    import math
    rb=1;rv=1
    for key in base: rb*=base[key][1]; rv*=d[key][1]
    out[n]=dict(diffs=diff,ratio=(rv/rb))
    print(n,'ratio of product of needed-X Pr over rows 17..25 (variant/base): %.6g'%(rv/rb),'|','; '.join(diff))
json.dump(out,open('bw_results.json','w'),indent=1)
