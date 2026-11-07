import json, math
from g02u02 import *
lg = math.log2
B0 = bytes_base(); T0, _ = T()
S = lambda t, b: t + max(0, lg(b)-20)
base = json.load(open('base.json'))
assert abs(T0-base['T0'])<1e-12 and B0 == 1045792
out = {'T0': T0, 'B0': B0, 'S0': S(T0, B0), 'headroom': 2**20-B0}
nsurv = 3840; ncl = 90
# hold the member list: one store + one load per survivor, all 90 classes (my count)
dPRE = 2*nsurv*ncl
Th, _ = T(PREX=dPRE); 
out['hold_ops'] = dPRE; out['hold_dT'] = Th - T0
# alternative: per-class candidate scan done twice (count then fill): not needed
gmax = max(g['nodes'] for g in base['gen'].values()); gins = max(g['instrs'] for g in base['gen'].values())
out['gen_nodes_max'] = gmax; out['gen_instr_max'] = gins
sizes = {'list_packed4B': 3840*4, 'list_word32B': 3840*32, 'gen_dag': gmax*32,
         'list_packed4B+gen_dag': 3840*4+gmax*32, 'list_word32B+gen_dag': 3840*32+gmax*32}
rows = {}
for k, d in sizes.items():
    B = B0 + d; rows[k] = dict(extra=d, B=B, mem_term=lg(B)-20 if B>2**20 else 0, S=S(T0+(out['hold_dT'] if 'list' in k else 0), B), over=B-2**20)
out['variants'] = rows
out['price_per_byte_at_2e20'] = 1/(2**20*math.log(2))
out['free_scratch_dead_online'] = 7*32*32 + 40*32 + 64*32
out['reuse_budget_dead_plus_headroom'] = out['free_scratch_dead_online'] + (2**20-B0)
out['PRE_total'] = base['PRE']; out['PRE_log2'] = lg(base['PRE']); out['PRE_over_N'] = lg(base['PRE']/base['N'])
out['stream_ops_vs_ledger'] = 0
# memory-limited breakpoint: bytes of working set that pays for time dT of a hold
out['hold_gain_bits'] = -out['hold_dT']   # negative = hold is slower
json.dump(out, open('res05.json','w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
