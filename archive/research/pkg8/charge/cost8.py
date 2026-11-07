#!/usr/bin/env python3
# CHARGE agent, pkg8. Complete charge-per-trial-equivalent ledger for design 2
# (F = K8 in C15, G = H4, six flips e14 e30 e31 x14 x30 x31, corner 0, 63 partners).
# Cost model (COST.txt): operation/load/store = 1; lane rotation = 5; compare+branch = 2.
# All macro counts (47, 135, 134, 260, 74) are pkg7 machine COUNTS in that convention.
import math

# ---- fixed / measured shares (task-given where stated) ----
Sp        = 40.02          # S'  (MEASURE; VERDICT pooled 40.044; grok 40.027)
TE        = 1.0 + Sp       # trial-equivalents per representative = 1 + S'
pG        = 1.0/16.0       # P(H4) gate rate, structurally exact (meas 2^-4.0001)
pF        = 1.0/256.0      # P(K8), structurally exact (meas 2^-7.99999)
wpr       = 2341.0/16384.0 # representative stage-A words per representative (packing)
P_F7      = 0.02622        # rep word has a K8 lane  (MEASURE/VERDICT 0.026178-0.026236)
P_G7      = 0.2416         # rep word has a gate lane (MEASURE/VERDICT 0.24096-0.241596)
bN1       = 9.0/16.0       # partner stage-A words per rep  (meas 0.5625)
bN2       = 0.1364         # partner stage-2 words per rep  (meas 0.13639-0.13646)
Ex_G      = 2.503          # partners passing K8 per triggered rep (union budget driver)
reps_grp  = 16384.0        # representatives per canonical-X2 group

# ---- macro costs ----
a     = 47.0   # stage A per word, K8                       COUNTED (pkg7)
ap    = 47.0   # stage A per PARTNER word (loads from cache) COUNTED base + layout note
s135  = 135.0  # stage 2 per word, K8                        COUNTED (pkg7)
gate  = 12.0   # H4 predicate + A-mask evict + flag spill, per rep word (Sol U 4.3)
tail  = 4.0    # last-word valid-lane suppression, once per group (Sol U 4.3)
sel   = 29.0   # lane selection, per gate-word: 1 (zero) + 7*(load+AND+cmp&br=4)  (Sol U 4.4)
addr  = 5.0    # partner-block address base+9r, per passing gate lane (DERIVED)
spill = 4.0    # metadata spill (packet idx + cursor: 2 store+2 load) per gate-word (ESTIMATE)
mid   = 134.0  # middle step per X2 value                    COUNTED (pkg7); 8 per group
cache = 258.0  # mixed-middle blend prep, per group  6*(1+7*6) (Sol U 4.2)
setup = 16.0   # canonical-X2 advance + list reset, per group (ESTIMATE)
tbl   = (74.0*133413.0 + 260.0)   # table body (8 seqs) + outer step, per outer tuple
tbl_per_rep = tbl / (2.0**43)     # amortised over 2^43 reps per outer tuple

# ---- cheap-test stage-2 model (variant 2): "its own cost, then 135 for passers" ----
c_test   = 99.0            # compute c1,c1',x and run test (RESULTS 2a; ESTIMATE, not recounted on K8 tier)
P_cheap  = 105.0/16384.0   # per K8-passing lane pass rate (O3/O4), ~1 lane per stage-2 word
P_cheap7 = 1.0-(1.0-105.0/16384.0)**7   # union over 7 lanes (budgeted)
s_cheap_exp = c_test + P_cheap  * s135  # expected
s_cheap_bud = c_test + P_cheap7 * s135  # budgeted

def ledger(s_rep, s_par, mode):
    # mode: 'exp' expected shares, 'bud' budgeted shares
    if mode == 'exp':
        rep_s2_words = wpr * P_F7         # rep stage-2 words/rep
        gate_words   = wpr * P_G7         # rep words with a gate lane /rep
        par_s2_words = bN2                # partner stage-2 words/rep
        par_a_words  = bN1                # partner stage-A words/rep
        pass_lanes   = pG                 # passing gate lanes/rep
    elif mode == 'bud':
        rep_s2_words = wpr * (1.0/32.0)           # pkg7 2^-(n-3)=1/32 per word
        gate_words   = wpr * (7.0/16.0)           # union 7*pG
        par_s2_words = pG * Ex_G                  # union: each K8 partner its own word
        par_a_words  = bN1                        # 9/16 structural
        pass_lanes   = pG                         # 1/16 structural (H4 exact)
    it = {}
    it['rep stage A']            = a    * wpr
    it['gate H4 test + spill']   = gate * wpr + tail/reps_grp
    it['rep stage 2']            = s_rep* rep_s2_words
    it['dispatch: lane select']  = sel  * gate_words
    it['dispatch: addressing']   = addr * pass_lanes
    it['metadata spill']         = spill* gate_words
    it['partner stage A']        = ap   * par_a_words
    it['partner stage 2']        = s_par* par_s2_words
    it['middle macros 8/grp']    = (8.0*mid)/reps_grp
    it['mixed-middle cache']     = cache/reps_grp
    it['group setup/reset']      = setup/reps_grp
    it['table+outer (amort)']    = tbl_per_rep
    return it

def total(it): return sum(it.values())

def charged(K):       # pkg7: budgeted*1.04, round UP to 0.1
    return math.ceil(K*1.04*10.0 - 1e-9)/10.0

def tlog2(kept, chg):
    return 123.339 - math.log2(kept/3.75) + math.log2(chg/34.0) + 0.012

kept1 = 185358111.47   # K8 in C15
kept2 = 185351809.0    # K8 + cheap test, exact joint (O4)

print("log2(kept1/3.75) =", round(math.log2(kept1/3.75),4))
print("log2(kept2/3.75) =", round(math.log2(kept2/3.75),4))
print("baseline check pkg7: charged 7.7 ->", round(tlog2(kept1,7.7),3))
print()

def run(name, s_rep, s_par, kept, mult_neighbour=1.0):
    out = {}
    for mode in ('exp','bud'):
        it = ledger(s_rep, s_par, mode)
        if mult_neighbour != 1.0:
            for k in ('dispatch: lane select','dispatch: addressing','metadata spill',
                      'partner stage A','partner stage 2'):
                it[k] *= mult_neighbour
        K = total(it)/TE
        chg = charged(K)
        out[mode] = (it, K, chg, tlog2(kept,chg), tlog2(kept,K*1.04))
    return out

print("="*78)
for vname, s_rep, s_par, kept in [
        ("VARIANT 1  s2=135",          s135, s135, kept1),
        ("VARIANT 2  cheap-test first", s_cheap_exp, s_cheap_exp, kept2)]:
    print(vname, "  kept =", kept)
    base = run(vname, s_rep, s_par, kept)
    # expected
    it,K,chg,t,tu = base['exp']
    print("  EXPECTED : K=%.4f  charged=%.1f  tlog2=%.3f  (unrounded %.3f)"%(K,chg,t,tu))
    for k,v in it.items():
        print("        %-26s %8.4f  (/TE %.5f)"%(k,v,v/TE))
    it,K,chg,t,tu = base['bud']
    print("  BUDGETED : K=%.4f  charged=%.1f  tlog2=%.3f  (unrounded %.3f)"%(K,chg,t,tu))
    # 1.72x neighbour, yield at mean (use expected shares scaled)
    if vname.startswith("VARIANT 1"):
        s172 = run(vname, s_rep, s_par, kept, mult_neighbour=1.72)['exp']
    else:
        s172 = run(vname, s_rep, s_par, kept, mult_neighbour=1.72)['exp']
    it,K,chg,t,tu = s172
    print("  1.72x nb : K=%.4f  charged=%.1f  tlog2=%.3f  (unrounded %.3f)"%(K,chg,t,tu))
    print("-"*78)

print()
print("variant2 s_cheap: exp=%.2f  bud=%.2f  (c_test=%.0f, P=%.5f, P7=%.5f)"%(
      s_cheap_exp, s_cheap_bud, c_test, P_cheap, P_cheap7))
