"""Own vectorised Keccak-f[1600] with round-component access. Lane index L=x+5y, arrays shape (25,N) uint64."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import numpy as np, sys
RC=[0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,0x000000000000808B,0x0000000080000001,
0x8000000080008081,0x8000000000008009,0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,
0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,0x8000000000008002,0x8000000000000080,
0x000000000000800A,0x800000008000000A,0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
# rho offsets by lane x+5y
RHO=[0]*25
x,y=1,0
for t in range(24):
    RHO[x+5*y]=((t+1)*(t+2)//2)%64
    x,y=y,(2*x+3*y)%5
U=np.uint64
def rotl(a,n):
    n%=64
    if n==0: return a.copy()
    return (a<<U(n))|(a>>U(64-n))
def theta(A):
    C=[A[x]^A[x+5]^A[x+10]^A[x+15]^A[x+20] for x in range(5)]
    D=[C[(x-1)%5]^rotl(C[(x+1)%5],1) for x in range(5)]
    return np.stack([A[l]^D[l%5] for l in range(25)])
def rhopi(A):
    B=np.zeros_like(A)
    for x in range(5):
        for y in range(5):
            B[y+5*((2*x+3*y)%5)]=rotl(A[x+5*y],RHO[x+5*y])
    return B
def chi(B):
    A=np.zeros_like(B)
    for y in range(5):
        for x in range(5):
            A[x+5*y]=B[x+5*y]^((~B[(x+1)%5+5*y])&B[(x+2)%5+5*y])
    return A
def rnd(A,r):
    A=chi(rhopi(theta(A))); A[0]^=U(RC[r]); return A
def perm(A,r0,r1):
    for r in range(r0,r1): A=rnd(A,r)
    return A
def state_from_msg(m128, pad=True):
    """m128: (N,128) uint8 -> (25,N) uint64 lanes of one 136-byte block with 0x06...0x80"""
    N=m128.shape[0]; A=np.zeros((25,N),dtype=np.uint64)
    lanes=m128.reshape(N,16,8).copy().view('<u8').reshape(N,16)
    for l in range(16): A[l]=lanes[:,l]
    A[16]=U(0x8000000000000006)
    return A
def digest_bits_mask(A):  # lanes 0..3
    return A[:4]
if __name__=='__main__':
    import hashlib, os
    sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
    from verifier import keccak as vk
    rng=np.random.default_rng(1)
    for N in range(3):
        m=bytes(rng.integers(0,256,128,dtype=np.uint8))
        A=state_from_msg(np.frombuffer(m,dtype=np.uint8)[None,:])
        out24=perm(A,0,24)[:4,0].astype('<u8').tobytes()
        assert out24==hashlib.sha3_256(m).digest(),'24-round mismatch'
        out6=perm(A,0,6)[:4,0].astype('<u8').tobytes()
        assert out6==vk.sha3_256(m,6),'6-round mismatch vs organizer verifier'
    print('keccak validated: 24r vs hashlib, 6r vs organizer verifier, 3 msgs each')
