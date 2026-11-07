"""Own Keccak + leader-route linear-form tools (sha3-r6-U01). Lanes are python ints; state bit index = 64*lane+z, lane=x+5y."""
import hashlib, random
M64 = (1 << 64) - 1
ROTT = [[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]  # ROTT[x][y]
def rotl(v, r):
    r %= 64
    return ((v << r) | (v >> (64 - r))) & M64 if r else v
def _rc():
    out = []; R = 1
    for t in range(24):
        c = 0
        for j in range(7):
            if R & 1: c |= 1 << ((1 << j) - 1)
            R <<= 1
            if R & 0x100: R ^= 0x171
        out.append(c)
    return out
RC = _rc()
def theta(A):
    C = [A[x] ^ A[x+5] ^ A[x+10] ^ A[x+15] ^ A[x+20] for x in range(5)]
    D = [C[(x-1) % 5] ^ rotl(C[(x+1) % 5], 1) for x in range(5)]
    return [A[x+5*y] ^ D[x] for y in range(5) for x in range(5)]
def rhopi(A):
    B = [0]*25
    for x in range(5):
        for y in range(5):
            B[y + 5*((2*x + 3*y) % 5)] = rotl(A[x+5*y], ROTT[x][y])
    return B
def chi(B):
    return [B[x+5*y] ^ ((~B[(x+1) % 5 + 5*y] & M64) & B[(x+2) % 5 + 5*y]) for y in range(5) for x in range(5)]
def rnd(A, i):
    A = chi(rhopi(theta(A))); A[0] ^= RC[i]; return A
def f_(A, rounds=24):
    for i in range(rounds): A = rnd(A, i)
    return A
def sponge_sha3_256(msg, rounds=24):
    rate = 136; m = bytearray(msg) + b'\x06'
    while len(m) % rate: m += b'\x00'
    m[-1] |= 0x80
    A = [0]*25
    for off in range(0, len(m), rate):
        for i in range(17): A[i] ^= int.from_bytes(m[off+8*i:off+8*i+8], 'little')
        A = f_(A, rounds)
    return b''.join(A[i].to_bytes(8, 'little') for i in range(4))
def to_int(A): return sum(A[l] << (64*l) for l in range(25))
def to_lanes(v): return [(v >> (64*l)) & M64 for l in range(25)]
def parity(x): return bin(x).count('1') & 1

# ---- formats: variables are state bits 0..nv-1 (rate region); constants per format
def fmt_const(fmt):
    c = [0]*25
    if fmt == 'F64': c[8] = 0x06; c[16] = 0x80 << 56; return 512, c
    if fmt == 'F135': c[16] = 0x86 << 56; return 1080, c
    raise ValueError
def state_of(m, fmt):
    nv, c = fmt_const(fmt)
    A = list(c)
    for l in range(17):
        A[l] ^= (m >> (64*l)) & M64 if 64*l < nv else 0
    # F135: lane16 only low 56 bits are variable
    if fmt == 'F135': A[16] = (c[16]) ^ ((m >> 1024) & ((1 << 56) - 1))
    return A
def P_lin(v):  # theta,rho,pi on 1600-bit int (linear)
    return to_int(rhopi(theta(to_lanes(v))))
class Forms:
    """affine forms of every post-theta-rho-pi state bit over the format variables."""
    def __init__(s, fmt):
        s.fmt = fmt; s.nv, c = fmt_const(fmt)
        s.const = P_lin(to_int(c))
        s.rows = [0]*1600
        for k in range(s.nv):
            d = P_lin(1 << k)
            while d:
                p = d & -d; s.rows[p.bit_length()-1] |= 1 << k; d ^= p
    def lin(s, m):  # linear image of variable vector m (1600-bit int)
        return P_lin(to_int(state_of(m, s.fmt)) ^ to_int(fmt_const(s.fmt)[1]) if False else 0)
def lin_image(fmt, m):
    nv, c = fmt_const(fmt)
    A = state_of(m, fmt); A0 = state_of(0, fmt)
    return P_lin(to_int(A) ^ to_int(A0))
# ---- GF(2) system
class Sys:
    def __init__(s): s.piv = {}   # pivot -> (row, rhs), kept reduced against earlier pivots only
    def copy(s): n = Sys(); n.piv = dict(s.piv); return n
    def red(s, r, v):
        while r:
            p = r.bit_length() - 1
            if p not in s.piv: break
            pr, pv = s.piv[p]; r ^= pr; v ^= pv
        return r, v
    def add(s, r, v):  # returns 'new','dep','incons'
        r, v = s.red(r, v)
        if r == 0: return 'dep' if v == 0 else 'incons'
        s.piv[r.bit_length()-1] = (r, v); return 'new'
    def rank(s): return len(s.piv)
    def sample(s, nv, rng):
        x = rng.getrandbits(nv)
        for p in sorted(s.piv):   # ascending pivot: lower bits of row are other pivots (smaller) already final
            r, v = s.piv[p]
            rest = r ^ (1 << p)
            # value of bit p so that parity(r & x) == v
            want = v ^ parity(rest & x)
            x = (x & ~(1 << p)) | (want << p)
        return x
