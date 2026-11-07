import sys,json,random; sys.path.insert(0,'.')
import b3core as B
prog,out=B.build(3)
r=json.load(open('hc_507.json')); w=r['witness']; x=sum(v<<(32*i) for i,v in enumerate(w))
rnd=random.Random(3)
res={}
for lanepos in (1,3,5):
    xs=[rnd.getrandbits(256) for _ in range(7)]; xs[lanepos]=x
    ok_ship=B.check(prog,B.build(3)[1],xs)
    ok_mut=B.check(prog,out,xs,(507,'a0'))
    o=B.run(prog,out,B.pack_x(xs),(507,'a0'))
    bad=[l for l in range(7) if any(B.lane(o[i],l)!=B.f_scalar(xs[l])[i] for i in range(8))]
    res[lanepos]=dict(shipped_correct=ok_ship,mask_removed_correct=ok_mut,wrong_lanes=bad)
print(res); json.dump(res,open('verify_witness_507.json','w'))
