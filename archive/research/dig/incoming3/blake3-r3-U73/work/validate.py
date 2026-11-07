# Known answers first: own numpy compress and rho.py scalar/packed code vs organizer verifier blake3.py at 7 and 3 rounds.
import random, numpy as np
from common import *
from b3own import compress, IV
random.seed(3)
bad=0
for rounds in (1,2,3,7):
    for _ in range(300):
        cv=[random.getrandbits(32) for _ in range(8)]; m=[random.getrandbits(32) for _ in range(16)]
        t=random.getrandbits(32); b=random.choice((55,63,64)); f=random.choice((1,2,3,8,11,12))
        ref=vb._compress(cv,m,t,b,f,rounds)[:8]
        v,d=compress(cv,m,t,b,f,rounds)
        if tuple(int(x[0]) for x in d)!=ref: bad+=1
print('own numpy compress vs verifier _compress, 1200 random (rounds 1,2,3,7):',bad,'mismatches')
print('verifier blake3("") 7r =',vb.blake3(b'',7).hex(),'expected af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262')
v,d=compress(list(IV),[0]*16,0,0,11,7)
print('own 7r empty =',b''.join(int(x[0]).to_bytes(4,'little') for x in d).hex())
# rho.py scalar digest on 0^32||x at 7 and 3 rounds vs verifier blake3()
bad7=bad3=0
for _ in range(300):
    x=random.getrandbits(256); msg=rho.message(x)
    import struct
    w=[0]*8+[(x>>(32*i))&0xFFFFFFFF for i in range(8)]
    for r in (7,3):
        dw=rho.digest_words(w,rounds=r)
        ref=vb.blake3(msg,r)
        if struct.pack('<8I',*dw)!=ref:
            if r==7: bad7+=1
            else: bad3+=1
print('rho.digest_words vs verifier blake3(0^32||x): 300 each, mismatches r7',bad7,'r3',bad3)
# packed 7-lane circuit (595 ops) vs verifier at 3 rounds
bad=0
for s in range(100):
    xs=[random.getrandbits(256) for _ in range(7)]
    out=rho.batch(*rho.pack_x(xs))
    for l in range(7):
        if struct.pack('<8I',*[rho.lane(out[i],l) for i in range(8)])!=vb.blake3(rho.message(xs[l]),3): bad+=1
print('rho.batch packed circuit vs verifier blake3 r3: 700 lanes, mismatches',bad,'; ops per batch',rho.PH,rho.PH_BY)
