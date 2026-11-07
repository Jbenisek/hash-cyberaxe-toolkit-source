"""Own Keccak (numpy, N messages at once) + the leader's structured prefix model (def724e5 proof Sec 2-3) for scan sha3-r6-U02."""
import numpy as np, hashlib
M64 = np.uint64
RC = [0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,0x000000000000808B,0x0000000080000001,
 0x8000000080008081,0x8000000000008009,0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,
 0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,0x8000000000008002,0x8000000000000080,
 0x000000000000800A,0x800000008000000A,0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
RHO = [0,1,62,28,27,36,44,6,55,20,3,10,43,25,39,41,45,15,21,8,18,2,61,56,14]
def rotl(v,n):
    n%=64
    if n==0: return v
    return (v<<M64(n))|(v>>M64(64-n))
def theta(A):
    C=[A[x]^A[x+5]^A[x+10]^A[x+15]^A[x+20] for x in range(5)]
    D=[C[(x-1)%5]^rotl(C[(x+1)%5],1) for x in range(5)]
    return np.stack([A[i]^D[i%5] for i in range(25)])
def rhopi(A):
    B=[None]*25
    for x in range(5):
        for y in range(5):
            B[y+5*((2*x+3*y)%5)]=rotl(A[x+5*y],RHO[x+5*y])
    return np.stack(B)
def chi(B):
    return np.stack([B[x+5*y]^((~B[(x+1)%5+5*y])&B[(x+2)%5+5*y]) for y in range(5) for x in range(5)])
def rnd(A,r):
    B=chi(rhopi(theta(A))); B[0]^=M64(RC[r]); return B
def perm(A,rounds=6):
    for r in range(rounds): A=rnd(A,r)
    return A
def msg_to_lanes(msgs):
    """msgs: (N,135) uint8 -> state (25,N) uint64 with SHA3 padding byte 135=0x86, capacity 0"""
    N=msgs.shape[0]; buf=np.zeros((N,200),np.uint8); buf[:,:135]=msgs; buf[:,135]=0x86
    L=buf.view('<u8').reshape(N,25).T.copy()
    return L
def lanes_to_msg(A):
    buf=np.ascontiguousarray(A.T).astype('<u8').view(np.uint8).reshape(A.shape[1],200)
    return buf[:,:135].copy()
PAD16 = (1<<57)|(1<<58)|(1<<63)
FREE=[0,1,2,3,4,6,7,9,10,11,13,14]
def r64(rng,N): return rng.integers(0,2**64,size=N,dtype=np.uint64)
def leader_state(rng,N,drop=None,z=None):
    """N structured prefixes (state lanes incl. padding). drop in {None,'L5','L15','D3','L8','L16'}: that condition group replaced by random."""
    L=np.zeros((25,N),np.uint64)
    for i in FREE: L[i]=r64(rng,N)
    if drop=='L16': L[16]=r64(rng,N)&np.uint64((1<<56)-1)
    L[16]|=np.uint64(PAD16)
    C4=L[4]^L[9]^L[14]; C1=L[1]^L[6]^L[11]^L[16]
    if drop!='L5': L[5]=C4^rotl(C1,1)
    else: L[5]=r64(rng,N)
    if drop!='L15': L[15]=L[5]^L[5]^C4^rotl(C1,1) if drop!='L5' else C4^rotl(C1,1)
    else: L[15]=r64(rng,N)
    L[8]=np.zeros(N,np.uint64) if drop!='L8' else r64(rng,N)
    if drop!='D3': L[12]=~rotl(C4,1)^L[2]^L[7]
    else: L[12]=r64(rng,N)
    if z is not None: L[4]^=np.uint64(z); L[14]^=np.uint64(z)
    return L
