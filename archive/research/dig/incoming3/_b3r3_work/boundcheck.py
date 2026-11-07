import sys,pickle; sys.path.insert(0,'.')
import b3core as B
def bounds(prog):
    bd={'i%d'%i:B.M32 for i in range(8,16)}; mx=0; worst=[]
    L=(1<<36)-1
    for k,o in enumerate(prog):
        a=[bd[x] for x in o['args']]; im=o['imm']; kd=o['kind']; il=(im&L) if im is not None else None
        if kd=='and': r=min(a[0],il) if True else 0; r=il if a[0]>il else a[0]  # coarse: bound of x&mask <= min(x,mask) ; for masks that are interval masks use mask
        if kd=='and' and il!=B.M32: r=il
        if kd=='add':
            r=a[0]+(a[1] if len(a)>1 else il)
            if r>=1<<36: worst.append((k,o['tag'],r/2**32))
        elif kd=='xor': r=(1<<max(a[0].bit_length(),(a[1] if len(a)>1 else il).bit_length()))-1
        elif kd=='or': r=a[0]|a[1] if False else (1<<max(a[0].bit_length(),a[1].bit_length()))-1
        elif kd=='shr': r=a[0]>>im
        elif kd=='shl': r=a[0]<<im
        bd[o['r']]=r
    return worst
prog0,out0=B.build(3); print('shipped overflow ops (bound model):',bounds(prog0))
choice,prog,out=pickle.load(open('q3_opt.pkl','rb')); print('optimum overflow ops (bound model):',bounds(prog))
