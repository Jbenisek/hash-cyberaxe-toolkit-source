# g07u02.py - H4a (A_C allowance) and H6 (memory) checks on the shipped R38M3 program (own code, a0lean38.py, read as module)

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

import sys, math, json, time
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/experiments'))
import a0lean38 as L
t0=time.time()
cal = L.calibrate()
print('calibrate s', round(time.time()-t0,1), 'prog', cal['prog'])
C=2728
def score(**kw):
    rows, info = L.ledger(cal=cal, show=False, **kw); N=sum(int(v) for _,v in rows)
    return math.log2(N)-math.log2(C), N, rows
base,N0,rows0 = score()
print('KNOWN ANSWER claimed config log2(N/C) = %.7f (filed 87.90374)' % base)
for k,v in rows0: print('%-70s %s  share %.3e' % (k, format(int(v),','), int(v)/N0))
print('log2 A_C = %.4f ; A_C*C / N = %.4e' % (78, 2**78*C/N0))
# R4: sensitivity
out={}
for e in (0,60,70,78,80,84,90,100):
    s,_,_ = score(A_C=2**e); out[e]=s; print('A_C=2^%d -> %.5f (delta %.5f)' % (e, s, s-base))
sNo,_,_=score(A_C=0); print('A_C=0 ->', sNo, 'delta', sNo-base)
# A_C that costs +0.01 / +0.1 / +1 bit
for d in (0.01,0.1,1.0):
    lo,hi=78.0,140.0
    for _ in range(60):
        mid=(lo+hi)/2
        s,_,_=score(A_C=int(2**mid)) if mid<120 else (None,None,None)
        if s is None: hi=mid; continue
        if s-base<d: lo=mid
        else: hi=mid
    print('A_C for +%.2f bit: 2^%.3f' % (d, lo))
# derivative d score / d log2 A_C at 78
s1,_,_=score(A_C=2**79); print('slope 78->79: %.6f bit per doubling' % (s1-base))
# charged conversion recount
cpu_prev=593858; print('2^37 * 593858 = 2^%.3f CPU-s ; 3e9 CPU-yr = 2^%.3f CPU-s ; A_C=2^78 compressions -> %.3e per CPU-s implied by 3e9 yr' % (37+math.log2(cpu_prev), math.log2(3e9*365.25*86400), 2**78/(3e9*365.25*86400)))
print('implied price from 2^37*593858 s: %.3e compressions/s' % (2**78/(2**37*cpu_prev)))
# H6
parts,tot = L.memory(cal)
for k,v in parts: print('%10d  %s' % (v,k))
print('MEMORY total', tot, 'log2 %.6f' % math.log2(tot), 'slack', 2**20-tot)
ninstr=sum(cal['prog'].values()); print('plane instr', ninstr, 'classes_of', cal['classes_of'])
# R4 H6 sensitivity: bytes per instruction
res={}
for bpi in (4,8,16,32,33,34,35,36,40,48,64):
    code=(ninstr+57+600)*bpi; other=tot-(ninstr+57+600)*32; T=other+code
    res[bpi]=(T, max(0,math.log2(T)-20)); print('B/instr %d total %d penalty %.5f bit %s' % (bpi,T,max(0,math.log2(T)-20), '(OVER 2^20)' if T>2**20 else ''))
print('instr slack at 32B:', (2**20-tot)//32, ' bits per extra byte over 2^20 at 2^20: %.3e' % (1/(2**20*math.log(2))))
# per-class marginal: bytes of one class (planes only) ; plane programs per group
print('breakeven bpi', (2**20-(tot-(ninstr+57+600)*32))/(ninstr+57+600))
print('elapsed', round(time.time()-t0,1))
