import itertools,random,json
from lines import *
random.seed(77)
base=['t_lo','t_hi','b','flags','h0','h1','h2','h3']
bad=0;tot=0;dirtyseen={}
for r in range(1,9):
  for sub in itertools.combinations(base,r):
    for _ in range(8):
        host=([R() for _ in range(8)],R(),R(),random.randrange(65),random.choice([1,3,11]))
        alt=alt_host(host,sub); m=[R() for _ in range(16)]; m2=pair(host,alt,m)
        chg=set(i for i in range(16) if m[i]!=m2[i])
        def afterC(host,m):
            h,tl,th,b,d=host
            v=states(h,m,tl,th,b,d,1)[-1]; mm=[m[p] for p in PI]
            for i,(a,bb,c,dd) in enumerate(COLS): G(v,a,bb,c,dd,mm[2*i],mm[2*i+1])
            return v
        y1=afterC(host,m); y2=afterC(alt,m2)
        for j,(A,B,C,D) in enumerate(COLS):
            tot+=1
            same=all(y1[x]==y2[x] for x in (A,B,C,D))
            if not (CREAD[j]&chg) and not same: bad+=1
            if (CREAD[j]&chg) and same: dirtyseen[j]=dirtyseen.get(j,0)+1
print('C-call clean-prediction violations',bad,'of',tot,'; dirty-predicted-but-equal',dirtyseen)
# replay the record's C3 pin numbers (BLAKE3_2ROUND_MAP 2.2)
def c3(w4):
    v=[0]*16; v[3]=0x29d4fa98; v[7]=0xbee3af28; v[11]=0x44036000; v[15]=0x40c58500
    G(v,3,7,11,15,w4,0x0007c006); return v
a=c3(0x97475638); b=c3(0x97475640)
print('record claims Y3 8127c181/7edf3e7e Y11 7af77f38/850000c3 d bbfbdffe b 76f7aefd')
print('got   Y3 %08x/%08x Y11 %08x/%08x d %08x/%08x b %08x/%08x'%(a[3],b[3],a[11],b[11],a[15],b[15],a[7],b[7]))
