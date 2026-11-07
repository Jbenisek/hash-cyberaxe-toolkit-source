import itertools, json
from b3 import *
K2=(IV[2]+IV[6])&M
X3,X7,X11,X15=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500
W4=0x97475638; W13=0x0007c006
def c3(x):
    v=[0]*16; v[3]=X3;v[7]=X7;v[11]=X11;v[15]=X15
    g(v,3,7,11,15,x,W13); return v[3],v[7],v[11],v[15]
base=c3(W4)
print('C3 base out a,b,c,d', [hex(t) for t in base], 'expect b=76f7aefd d=bbfbdffe')
a1=(K2+W4)&M; print('K2+W4 =',hex(a1),'bit3=',(a1>>3)&1)
print('55->63 w4 diff by construction', ((a1^55^63)-a1)&M, 'i.e. w4prime=', hex((((a1^8)-K2))&M))
res={}
for b2 in range(1,65):
    if b2==55: continue
    dl=55^b2; bits=[k for k in range(32) if dl>>k&1]
    # actual D for the pinned W4 (forced by construction)
    D=((a1^dl)-a1)&M
    o=c3((W4+D)&M)
    res[b2]=dict(delta=dl,D=D if D<2**31 else D-2**32,pins_hold=(o[1]==base[1] and o[3]==base[3]))
holds=[b for b,r in res.items() if r['pins_hold']]
print('length partners of 55 for which the existing C3 pins (X3,X7,X11,X15,W4,W13) still give equal b,d outputs:',holds)
# all D values for delta=8: both signs
for D in (8,-8,16,-16):
    o=c3((W4+D)&M); print('D',D,'pins hold',o[1]==base[1] and o[3]==base[3])
# legal pairs with W13 as pinned (top byte 0, bytes 52..54 nonzero) -> shorter length >= 55
legal=[(b1,b2) for b1 in range(55,65) for b2 in range(55,65) if b1<b2]
print('pairs both in 55..64:',len(legal))
tab={f'{a}/{b}':dict(delta=a^b, D=(((a1^(a^b))-a1)&M if True else 0)) for a,b in legal}
json.dump(dict(base=[hex(t) for t in base],holds=holds,per_partner_of_55=res,pairs_55_64=tab),open('t2_out.json','w'),indent=1)
