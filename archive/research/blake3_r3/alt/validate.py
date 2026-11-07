import numpy as np, os, struct, random
from b3h import *
from verifier.blake3 import blake3 as ref, _compress as rc, IV as RIV
# official 7-round empty hash
e = ref(b"",7).hex(); print("empty7", e, e.startswith("af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"))
# single-block compare vs verifier (all rounds 1..7, random flags/counter/len)
random.seed(1); bad=0
for r in range(1,8):
  for t in range(200):
    w=[random.getrandbits(32) for _ in range(16)]; cv=[random.getrandbits(32) for _ in range(8)]
    ctr=random.getrandbits(40); bl=random.choice([1,17,64]); fl=random.getrandbits(4)
    a=rc(tuple(cv),tuple(w),ctr,bl,fl,r)
    b=compress(np.array(w,dtype=np.uint32)[:,None],np.array(cv,dtype=np.uint32),ctr,bl,fl,r,full=True)[:,0]
    if tuple(int(x) for x in b)!=tuple(a): bad+=1
print("single-compress mismatches (7 rounds sizes x200):",bad)
# whole-message: 0^32||x at 3 and 7 rounds
bad=0
for r in (3,7):
  for t in range(300):
    x=os.urandom(32); msg=bytes(32)+x
    w=bytes_to_words(msg)[:,None]
    d=compress(w.astype(np.uint32),IV,0,64,11,r)[:,0]
    if words_to_bytes(d)!=ref(msg,r): bad+=1
print("0^32||x vs verifier.blake3 mismatches:",bad)
