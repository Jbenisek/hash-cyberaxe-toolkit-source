import re,math,glob
from statistics import mean,stdev
res={}
for np_ in (8192,2048,512,64,8):
    try: t=open(f'out_np{np_}.txt').read()
    except: continue
    v=[float(x) for x in re.findall(r'log2 q3 = (-?[\d.]+)\s*$',t,re.M) if True]
    # exclude SUMMARY line pattern (has 'mean log2 q3 =')
    v=[float(m) for m in re.findall(r'^rep \d+: .*log2 q3 = (-?[\d.]+)',t,re.M)]
    fails=len(re.findall(r'failed',t))
    lin=math.log2(mean(2**x for x in v)) if v else None
    res[np_]=v
    print(np_,len(v),'fail',fails,'mean log2 %.4f sd %.4f se %.4f  log2(mean q3) %.4f'%(mean(v),stdev(v),stdev(v)/len(v)**.5,lin))
if 8192 in res and 512 in res:
    print('sd ratio 512/8192 = %.2f (expect 4)'%(stdev(res[512])/stdev(res[8192])))
if 2048 in res and 8192 in res: print('sd ratio 2048/8192 = %.2f (expect 2)'%(stdev(res[2048])/stdev(res[8192])))
