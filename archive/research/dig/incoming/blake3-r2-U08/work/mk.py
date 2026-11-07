
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

import json,sys
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dig')
sys.path.insert(0,D); import add_cell
out=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/blake3-r2-U08')
ev='research/dig/incoming/blake3-r2-U08/work/w4scan.c; research/dig/incoming/blake3-r2-U08/work/w4scan_out.txt; research/dig/incoming/blake3-r2-U08/work/w4_solutions.txt; research/dig/incoming/blake3-r2-U08/work/e1_delta.py; research/dig/incoming/blake3-r2-U08/work/e1_delta_out.txt'
ev4='research/dig/incoming/blake3-r2-U08/work/w4scan.c; research/dig/incoming/blake3-r2-U08/work/w4scan_out.txt; research/dig/incoming/blake3-r2-U08/work/w4_solutions.txt; research/dig/incoming/blake3-r2-U08/work/w4prime_solutions.txt'
ev5='research/dig/incoming/blake3-r2-U08/work/w4scan.c; research/dig/incoming/blake3-r2-U08/work/w4scan_out.txt; research/dig/incoming/blake3-r2-U08/work/e1_delta.py; research/dig/incoming/blake3-r2-U08/work/e1_delta_out.txt'
Q={1:'Q1: difference/condition count as used at this word',2:'Q2: necessity of each condition group here (relax one, recount exact outcome mass)',3:'Q3: degrees of freedom here (exact count over carries)',4:'Q4: alternative outcomes / carry patterns (75/32 effect) and whether they reach the same later differences'}
def rec(w,q,obj,labels,status,num,evid,notes):
    cid='blake3-r2|m%d|msgword|Q%d'%(w,q)
    r=dict(hash='blake3-r2',row_i=None,row_j=None,object=obj,question=Q[q],labels=labels,status=status,number=num,
      source='our workflow: scan-once',own_test=True,evidence=evid,date='2026-10-12',lever=False,gain_bits=None,
      notes='universe cell %s. '%cid+notes)
    errs=add_cell.validate(r,add_cell.load())
    assert not errs,(cid,errs)
    json.dump(r,open(out+'/'+cid.replace('|','_')+'.json','w'),indent=1)
    print('ok',cid)

c4=' Other constants held as printed (X3,X7,X11,X15,W13; proof.md 3.2); controls reproduce Fact P exactly.'
DY='dY3 xor fff8ffff (add fdb77cfd), dY11 xor fff77ffb (add 0a08818b)'
rec(4,1,'m4 = w4: pinned word W4=97475638 (A) vs W4p=97475640 (B)',['P','0'],'COMPUTED',
 'w4 PINNED: 32 of 32 bits fixed (1 value of 2^32); difference W4p-W4 = +8 additive, xor 00000078 (bits 3-6); 0 free bits. Effect at C3: b2,d2 equal (64 bit equalities hold), a2,c2 differ: '+DY,ev4,
 'Layout from proof.md 3.1-3.2: w4 is pinned, not one of the 8 free words (Lemma T2); w4p=((K+w4)^8)-K, K=IV2+IV6=5bf2cd1d; K+W4=f33a2355 has bit3=0 so XOR 8 adds +8. Package writes the difference as W4-W4p=-8. Exact C3 outputs reproduced: W4 a2=8127c181 d2=bbfbdffe c2=7af77f38 b2=76f7aefd; W4p a2=7edf3e7e d2=bbfbdffe c2=850000c3 b2=76f7aefd.'+c4)
rec(4,2,'m4 = w4: necessity of the pin (relax w4 over 2^32; relax w4p over 2^32)',['K','P'],'COMPUTED',
 'Exhaustive 2^32: (A) w4 free, w4p by the K2 rule: d2 equal for 4, b2 equal for 2, both for 2 (W4 and W4p, the same pair swapped). (B) w4=W4 fixed, w4p free: d2 equal 3, b2 equal 2, both 2 (97475638, 97475640). So the pin is necessary: relaxing it loses all but 1 unordered pair of 2^32 (mass 2^-31 of w4 values, 2^-32 of w4p)',ev4,
 'Event tested = the Fact P / Lemma H requirement that C3 gives equal b and d outputs for w4 and w4p, others fixed. Both solutions in (A) are the same pair with A/B swapped (second row has delta -8). Relaxing the other pinned constants (X3,X7,X11,X15,W13) was not scanned here (not this word).'+c4)
rec(4,3,'m4 = w4: degrees of freedom',['K','P'],'COMPUTED',
 '0 bits in the construction (w4 = W4 exactly; Lemma T2(d) bijection onto admissible blocks pins it); exact event count over all 2^32 w4: 2 values = 1 unordered pair = log2 1 bit of choice (A/B swap only); no free carries: the K2 rule gives w4p uniquely (bit3 of K+w4 fixes the +8/-8 carry sign)',ev4,
 'DOF measured by exhaustion of the 2^32 w4 scan with the printed rule, so it is exact for the printed constants; the 4 other pinned words are not varied. No fake freedom: nothing to harvest at w4.'+c4)
rec(4,4,'m4 = w4: alternative carry patterns (sign of the +/-8) and outcomes',['C','K'],'COMPUTED',
 'Carry pattern of the 8-step: bit3 of K+w4 = 0 gives +8, =1 gives -8: 2^31 w4 each (exact). Only one w4 in each class passes the b2,d2 equality (W4 with +8; its swap W4p with -8). The swap has the same XOR differences (dY3 xor fff8ffff, dY11 xor fff77ffb) and negated additive ones (-fdb77cfd, -0a08818b): same later xor differences, mirrored A/B',ev4,
 'There is no 75/32-type extra pattern at w4: the xor pattern of the difference is 00000078 for W4 and the exhaustive scan finds no second solution class. Later differences reached: the same ones (swap of roles of the two messages, i.e. relabelling, not a new outcome).'+c4)
e5=' Delta shift measured on E1 a2 only (a-side of the L count); b1/c1/eps parts of L and the E3 side are not recomputed.'
rec(5,1,'m5 = w5: cancelling word, w5p = w5 + W4 - W4p = w5 - 8',['N','I'],'COMPUTED',
 'w5 FREE: 0 conditions on its 32 bits (2^32 values); relation only to w4: w5p-w5 = -8 additive. XOR difference w5^(w5-8) over all 2^32 w5 is exactly 00000008 (2^31), 00000018 (2^30), 00000038 (2^29) ... fffffff8 (16): 29 patterns, pattern with lowest set bit k>=3 has count 2^(31-(k-3)) ',ev5,
 'Layout from proof.md 3.1 (cancelling) and Step O (w5 is one of the six outer words). Lemma L checked exhaustively: all 2^32 w5 with w4=W4: K2(n=55,w4,w5) and K2(n=63,w4p,w5p) agree in all four outputs (0 mismatches). Exhaustive xor-pattern histogram in w4scan_out.txt (E lines).')
rec(5,2,'m5 = w5: necessity of the cancellation w5p = w5 - 8 (relax w5p; relax the shift in E1)',['I','K'],'LOCAL_ONLY',
 '(a) K2: for w5=12345678 exactly 1 of 2^32 w5p (the rule value) gives equal K2 state; (b) E1 a2-tau (tau 285020a0, beta* 18b0e098): compatible s at shift -8 = 16 of 2^11 (control table 16,32,8,16,32,8,16 reproduced); at shift 0 = 0, at +8 = 16; the maximum over all 2^32 shifts is 16 (attained at 5880 shifts), so -8 is a maximum, not above it. beta2 18d0e098: 32 at -8, max 32',ev5,
 '(a) is exhaustive. (b) is the a-side only (criterion of proof 9.7 validated against brute force at width 10, 0/400 mismatches) so LOCAL_ONLY: the full L adds the c1 cube and eps coupling. The shift is forced to -8 anyway by w4 pinned (Q2/m4), so no free alternative exists.'+e5)
rec(5,3,'m5 = w5: degrees of freedom and carries in E1.a2 = a1+b1+w5',['X','C'],'LOCAL_ONLY',
 'w5 contributes 32 free bits; inside outcome (beta*, tau 285020a0): s=b1&beta compatible for 16 of 2^11 submasks (2^-7), and for a compatible s exactly 2^25 of the 2^32 values of a2 (hence of w5 given the rest) give tau (pc(tau)=7): 25 free bits remain, P=2^-7; a-side factor 2^-14',ev5,
 'a2 = a1+b1+w5 so w5 is a direct tap on a2 (label X). Carry count is exact for the printed criterion (counts 2^(32-popcount tau) per compatible s) but only the a2 factor of L is covered.'+e5)
rec(5,4,'m5 = w5: alternative carry patterns of the -8 and shifts reaching tau 285020a0',['C','B'],'LOCAL_ONLY',
 'Over all 2^32 shifts: 33048 distinct shifts reach tau 285020a0 for beta* from some s (262144 (s,pattern) pairs = 2048 x 128); the actual shift -8 reaches it with 16 s, the +8 mirror also 16, shift 0 none; 29 xor patterns of w5^(w5-8) with counts halving (2^31 ... 16)',ev5,
 'The 8-step (-8 for the pinned W4, +8 for the swap) is the only shift the construction can produce, so the other shifts are not reachable alternatives; they are listed only to show -8 is not worse than any other shift on the a-side.'+e5)
