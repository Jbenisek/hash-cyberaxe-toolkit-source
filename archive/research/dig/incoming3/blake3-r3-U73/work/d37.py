# DOOR.d37 D1 at 3 rounds: ledger arithmetic. Cost of one fresh-CV prior block (638 ops = 1 unit, C(r3)) charged to the filed ledger.
import sys
from fractions import Fraction
from math import log2
from common import rho
lg=rho.ledger(256); tot=lg['total']; units=tot/638
print('filed ledger: total ops',float(tot),'units',float(units),'time_log2',log2(units))
assert abs(log2(units)-125.10856)<1e-4
p=lg['plan']; B=p['B']
from math import log1p, log
def pen(added_units): return log1p(float(Fraction(added_units)/units))/log(2)
cases={
 'once (one prior block for the whole attack)':1,
 'per trail start (tmax=%d starts)'%p['tmax']:p['tmax'],
 'per recovery (one)':1,
 'per DP event (finished trail, <=%d)'%p['tmax']:p['tmax'],
}
for k,v in cases.items(): print('%-50s added %d unit(s): penalty %.3e bit'%(k,v,pen(v)))
# per evaluation (every chain step needs its own fresh CV block): added 638 ops per evaluated point
ops_per_eval=Fraction(tot, p['Q'])
print('ops per evaluated point in the ledger: %.3f'%float(ops_per_eval))
added=Fraction(638)*p['Q']/638
print('per evaluated point: penalty %.4f bit (factor %.4f)'%(log2(1+float(638/ops_per_eval)),1+float(638/ops_per_eval)))
# per batch of 7 evaluations: one prior block shared by the 7 lanes
print('per batch of 7 lanes (one block): penalty %.4f bit'%log2(1+638/float(Fraction(tot,B))))
# stacked: with 2^-bit slack of a hypothetical saving s bits the prior block would have to buy
print('a prior block per context can only pay if it saves more than the penalty; no measured lever for blake3-r3 uses CV freedom (chain is 0^32||x, cv=IV fixed by the target)')
