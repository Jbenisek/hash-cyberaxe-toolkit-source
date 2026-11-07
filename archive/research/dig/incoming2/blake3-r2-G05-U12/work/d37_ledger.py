"""door 37 RELABEL: ledger arithmetic, fresh CV / prior block per context, with measured levers stacked.
Pure arithmetic on recorded numbers (no third-party code run). Inputs: base ledger score 58.6197 (N=190440978718867836423,
contexts 2046750299405671, 430 ops = 1 unit) from b3_layerxtech_mode_cost/RESULT.md; our stacked scores from LEVERS/HANDOFF:
57.2365 (pkgB3T), 57.0055 (coupled omega), 56.7927 (B3W). Penalty = log2(1 + added/N_stacked)."""
from math import log2
C=430; N0=190440978718867836423; rc=2046750299405671
assert abs(log2(N0/C)-58.6197)<1e-4
print("check base: penalty per ctx %.4f (record 0.0067)"%log2((N0+C*(rc+1))/N0))
for lab,sc in (("base",58.6197),("pkgB3T",57.2365),("omega",57.0055),("B3W",56.7927)):
    Ns=C*2**sc
    # case A: whole saving is in context COUNT (ops per context unchanged, added ops scale with contexts)
    rcA=rc*Ns/N0
    pA={g:log2(1+C*m*(rcA+1)/Ns) for g,m in (("ctx",1),("member",8),("block",16))}
    # case B: whole saving is per-context work (rc unchanged, added ops fixed)
    pB={g:log2(1+C*m*(rc+1)/Ns) for g,m in (("ctx",1),("member",8),("block",16))}
    print(lab,sc,"A(ctx count shrinks)",{k:round(v,4) for k,v in pA.items()},"B(per-ctx work shrinks)",{k:round(v,4) for k,v in pB.items()})
