# Own Keccak-f[1600] backward cone of a digest key through round idx 5, reported at chi of round idx 4.
import random, json, sys
M=(1<<64)-1
def rol(a,n): n%=64; return ((a<<n)|(a>>(64-n)))&M if n else a
def _rc():
    R=1; out=[]
    for t in range(24):
        c=0
        for j in range(7):
            if R&1: c|=1<<((1<<j)-1)
            R<<=1
            if R&0x100: R^=0x171
        out.append(c)
    return out
RC=_rc()
ROT=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]] # ROT[x][y]
def theta(A):
    C=[A[x][0]^A[x][1]^A[x][2]^A[x][3]^A[x][4] for x in range(5)]
    D=[C[(x-1)%5]^rol(C[(x+1)%5],1) for x in range(5)]
    return [[A[x][y]^D[x] for y in range(5)] for x in range(5)]
def rhopi(A):
    B=[[0]*5 for _ in range(5)]
    for x in range(5):
        for y in range(5): B[y][(2*x+3*y)%5]=rol(A[x][y],ROT[x][y])
    return B
def chi(B): return [[B[x][y]^((~B[(x+1)%5][y])&B[(x+2)%5][y]&M) for y in range(5)] for x in range(5)]
def rnd(A,r): 
    A=chi(rhopi(theta(A))); A[0][0]^=RC[r]; return A
# validate against hashlib sha3 permutation: sha3_256 of empty msg = one block, 24 rounds
def f24(A):
    for r in range(24): A=rnd(A,r)
    return A
import hashlib
st=[[0]*5 for _ in range(5)]; st[0][0]=0x06; st[4][1]=1<<63  # rate 136 bytes: byte 135 = 0x80 -> lane 16 = x=1,y=3? compute below
# lane i = x+5y; byte 135 -> lane 16 -> x=1,y=3, bit 63 (byte 7 of lane, top)
st[4][1]=0; st[1][3]=1<<63
o=f24(st); dig=b''.join(o[x][0].to_bytes(8,'little') for x in range(4))
assert dig==hashlib.sha3_256(b'').digest(),"keccak validation FAILED"
print("keccak validated vs hashlib sha3_256('')")
# bit index
def ix(x,y,z): return (x*5+y)*64+z
def unpack(i): z=i%64; t=i//64; return t//5,t%5,z
def to_bits(A): return [(A[x][y]>>z)&1 for x in range(5) for y in range(5) for z in range(64)]
def from_lanes(L): return [[L[x*5+y] for y in range(5)] for x in range(5)]
# dependency maps (output bit -> set of input bits), by structure
def chi_dep(o):
    x,y,z=unpack(o); return {ix(x,y,z),ix((x+1)%5,y,z),ix((x+2)%5,y,z)}
# rho-pi: output B[y][(2x+3y)] bit z = A[x][y] bit z-rot
RP={}
for x in range(5):
    for y in range(5):
        for z in range(64):
            RP[ix(y,(2*x+3*y)%5,(z+ROT[x][y])%64)]=ix(x,y,z)
def theta_dep(o):
    x,y,z=unpack(o); s={ix(x,y,z)}
    for yy in range(5): s.add(ix((x-1)%5,yy,z)); s.add(ix((x+1)%5,yy,(z-1)%64))
    return s
def back(outs,dep): 
    s=set()
    for o in outs: s|=dep(o)
    return s
def cone(zs):
    key={ix(x,0,z) for x in range(4) for z in zs}
    I5=back(key,chi_dep)                       # chi5 inputs
    T5=back(I5,lambda o:{RP[o]})               # theta5 outputs (rhopi inverse)
    O4=back(T5,theta_dep)                      # theta5 inputs = chi4 outputs
    I4=back(O4,chi_dep)                        # chi4 inputs
    return key,I5,T5,O4,I4
def rows(S): return {(unpack(i)[1],unpack(i)[2]) for i in S}   # chi row = (y,z), 5 lanes x
def report(zs):
    key,I5,T5,O4,I4=cone(zs)
    return dict(key_bits=len(key),chi5_in=len(I5),theta5_out=len(T5),chi4_out_cone=len(O4),chi4_in_cone=len(I4),
                chi4_out_rows=len(rows(O4)),chi4_in_rows=len(rows(I4)),columns=len({(unpack(i)[0],unpack(i)[2]) for i in O4}))
res={}
res['z0..34 (35 planes, 140-bit key)']=report(range(35))
res['z0..28 (29 planes, 116-bit key)']=report(range(29))
res['z0..63 (all, 256-bit digest)']=report(range(64))
for k,v in res.items(): print(k,v)
# --- empirical necessity test ---
def keyvals(A,zs): return tuple((A[x][0]>>z)&1 for x in range(4) for z in zs)
def rest_from_chi4_out(A):  # A = state after chi4 (iota4 omitted: irrelevant constant); apply round idx 5
    return rnd(A,5)
def emp(zs,nst=24,seed=1):
    rng=random.Random(seed); key,I5,T5,O4,I4=cone(zs)
    nec_out=[0]*1600; nec_in=[0]*1600
    for _ in range(nst):
        A=[[rng.getrandbits(64) for y in range(5)] for x in range(5)]
        base=keyvals(rest_from_chi4_out(A),zs)
        for i in range(1600):
            x,y,z=unpack(i); B=[r[:] for r in A]; B[x][y]^=1<<z
            if keyvals(rest_from_chi4_out(B),zs)!=base: nec_out[i]=1
        # chi4 input X: state before chi4 = after rhopi4; simulate chi then round5
        base2=keyvals(rest_from_chi4_out(chi(A)),zs)
        for i in range(1600):
            x,y,z=unpack(i); B=[r[:] for r in A]; B[x][y]^=1<<z
            if keyvals(rest_from_chi4_out(chi(B)),zs)!=base2: nec_in[i]=1
    eo={i for i in range(1600) if nec_out[i]}; ei={i for i in range(1600) if nec_in[i]}
    return dict(emp_out=len(eo),emp_in=len(ei),out_outside_cone=len(eo-O4),in_outside_cone=len(ei-I4),
                cone_not_hit_out=len(O4-eo),cone_not_hit_in=len(I4-ei))
E={}
for name,zs in [('z0..34',range(35)),('z0..28',range(29)),('z0..63',range(64))]:
    E[name]=emp(list(zs),nst=int(sys.argv[1]) if len(sys.argv)>1 else 24); print(name,E[name])
# --- z-set sensitivity (one measurement): cone size at chi4 output for 35-plane sets
rng=random.Random(7)
sizes={'contiguous':len(cone(range(35))[3]),'stride2(0,2..68 mod64 distinct)':None}
rs=[len(cone(rng.sample(range(64),35))[3]) for _ in range(300)]
best=min(rs); 
# greedy: choose z set to minimise cone: columns needed depend on z via D: per chi5 input lane z-shifts; try contiguous with stride patterns
cand={}
for st in (1,2,3,5,7):
    zs=sorted({(st*i)%64 for i in range(35)})
    if len(zs)==35: cand[f'stride{st}']=len(cone(zs)[3])
print('random 35-subsets min/max',min(rs),max(rs),'strided',cand)
zs7=sorted({(7*i)%64 for i in range(35)}); k,I5_,T5_,O4_,I4_=cone(zs7); out_s7=dict(zs=zs7,chi5_in=len(I5_),chi4_out=len(O4_),chi4_in=len(I4_)); print("stride7",out_s7)
out=dict(stride7=out_s7,cones=res,empirical=E,rand35_min=min(rs),rand35_max=max(rs),strided=cand)
json.dump(out,open(__file__.replace('cone5.py','cone5_out.json'),'w'),indent=1)
