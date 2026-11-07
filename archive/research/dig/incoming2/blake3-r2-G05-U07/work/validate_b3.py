import sys,struct,random,subprocess,json
from b3 import *
# known answer 1: BLAKE3("") 7 rounds
o=compress(IV,[0]*16,0,0,0,11,rounds=7)
hx=b''.join(struct.pack('<I',x) for x in o).hex()
print('empty 7r',hx, hx=='af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262')
# cross-check against organizer verifier in WSL on random 2-round and 7-round compressions
random.seed(5); cases=[]
for _ in range(200):
    h=[random.getrandbits(32) for _ in range(8)]; m=[random.getrandbits(32) for _ in range(16)]
    cases.append((h,m,random.getrandbits(32),random.getrandbits(32),random.randrange(65),random.choice([1,2,3,8,10,11,4,12]),random.choice([2,7,1])))
json.dump(cases,open('cases.json','w'))
mine=[compress(*c[:6],rounds=c[6],full=True) for c in cases]
json.dump(mine,open('mine.json','w'))
