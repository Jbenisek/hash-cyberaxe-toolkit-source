import random, sys
import b3m, blake3 as ver
print('empty r7', b3m.hash_(b'',7).hex()[:32], ver.blake3(b'',7).hex()[:32], 'known af1349b9f5f9a1a6a0404dea36dcc949')
random.seed(8); bad=0; n=0
lens=list(range(0,200))+[255,256,1023,1024,1025,1087,1088,1089,2047,2048,2049,3071,3072,3073,4096,5000]
for L in lens:
    for r in (2,7):
        m=bytes(random.getrandbits(8) for _ in range(L)); n+=1
        if b3m.hash_(m,r)!=ver.blake3(m,r): bad+=1
print('hash mismatches vs organizer verifier',bad,'of',n,'(lengths 0..199 + chunk/tree boundaries, r=2 and r=7)')
