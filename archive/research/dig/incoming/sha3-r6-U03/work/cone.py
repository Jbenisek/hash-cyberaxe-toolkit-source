import numpy as np, json, sys
from kk import *
KEEP=(0,1,2,3,4,9,10,11,16,17,18,22,23,24,25,29,30,31,32,37,38,39,40,44,45,46,47,51,52,53,54,58,59,60,61)
assert len(KEEP)==35
idx=lambda x,y,z:64*(x+5*y)+z%64
def theta_dep(outset):  # set of S bits needed to get theta outputs in outset
    s=set()
    for i in outset:
        l,z=divmod(i,64); x=l%5
        s.add(i)
        for y in range(5):
            s.add(idx((x-1)%5,y,z)); s.add(idx((x+1)%5,y,z-1))
    return s
def rhopi_inv(Bset):  # B bits -> theta-output bits
    s=set()
    for x in range(5):
        for y in range(5):
            Bl=y+5*((2*x+3*y)%5); r=RHO[x+5*y]
            for z in range(64):
                if 64*Bl+z in Bset: s.add(64*(x+5*y)+(z-r)%64)
    return s
def chi_dep_bits(outset):
    s=set()
    for i in outset:
        l,z=divmod(i,64); x,y=l%5,l//5
        for k in range(3): s.add(idx((x+k)%5,y,z))
    return s
def rows_of(bits):
    return {(i//64//5, i%64) for i in bits}   # (y,z)
def back_round(Sout):
    """chi outputs needed Sout -> returns B bits (exact 3-input), rows, S_prev needed"""
    B=chi_dep_bits(Sout); rows=rows_of(Sout)
    Brow={idx(x,y,z) for (y,z) in rows for x in range(5)}
    Sprev=theta_dep(rhopi_inv(B)); Sprev_row=theta_dep(rhopi_inv(Brow))
    return B,rows,Brow,Sprev,Sprev_row
if __name__=='__main__':
    key={idx(x,0,z) for x in range(4) for z in KEEP}; assert len(key)==140
    out={}; S=key
    for r in (6,5,4,3):
        B,rows,Brow,Sp,Sprow=back_round(S)
        out[r]=dict(chi_outputs_needed=len(S),chi_rows_touched=len(rows),B_bits_exact=len(B),B_bits_rowlevel=len(Brow),
                    Sprev_needed_exact=len(Sp),Sprev_needed_rowlevel=len(Sprow),
                    theta_cols_needed=len({(i//64%5,i%64) for i in Sp}))
        print(r,out[r]); 
        out[r]['_S']=sorted(S); out[r]['_Sprev']=sorted(Sp)
        S=Sp
    json.dump({str(k):v for k,v in out.items()},open('cone.json','w'))
