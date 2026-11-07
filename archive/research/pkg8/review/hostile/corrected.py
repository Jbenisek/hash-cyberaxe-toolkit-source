from math import log2, exp, ceil
TE=41.02; CL=64
f_assumed=49_400_000; f_needed_nocluster=49_323_560
r=TE/CL
print("TE/64 (text rates)        = %.6f"%r)
print("TE/64 (my 400-tuple run)  = %.6f (TE=41.202)"%(41.202/64))
# success at the printed N
for name,rr in (("text 41.02",r),("measured 41.202",41.202/64)):
    eg=0.5*rr
    print("%-16s expected good = %.4f -> success >= %.4f (claim says 0.39)"%(name,eg,1-exp(-eg)-0.003))
# factor needed
print("f needed for 0.39 with clusters = %d (text says 49,323,560; assumed 49,400,000)"%ceil(f_needed_nocluster/r))
# trials needed
base=1424468.5056207287
need=ceil(base/r)
print("C0.d1 values needed = %d (text prints 1,424,469)"%need)
print("N corrected log2 = %.6f (text 101.442)"%(log2(need)+81))
T=log2(1.71)+log2(need)+81-log2(430)
print("charged time log2 = %.4f -> claim %.1f  (text 93.5)"%(T+0.01123,94.2))
# clustering remark
print("expected good under the count = %.4f (text 1.87); m survives up to %.2f (text 3.74)"
      %(1.8760679891688667*r, 1.8760679891688667*r/0.5))
# stage-2 budget E
J=2**110/f_assumed
E=18725*J/32
print("\nE = %.4f  log2 E = %.4f"%(E,log2(E)))
reps=need*2**81/64
s2_text=0.026178/7+0.1364
s2_mine =0.026355/7+0.56428*0.24425
for nm,s in (("text rates",s2_text),("my rates",0.026355/7+0.56428*0.24425)):
    print("%-10s stage-2 words/rep %.5f -> per run 2^%.3f ; E/entries = %.3f"
          %(nm,s,log2(reps*s),E/(reps*s)))
stA=1/7+0.5625
print("E as a share of the batches of a run = %.4f (6.4 and H3 say 'one part in 32' = %.5f)"
      %(E/(reps*stA),1/32))
# memory
print("\nSection 9 data %d bytes + code 2^19 = %d < 2^23 = %d"%(4210784,4210784+2**19,2**23))
print("eight times the data: %d > 2^23"%(8*4210784))
print("133,413 one-word rows + 2 lists: %d bytes"%((133413+2*18725)*32+2**19))
