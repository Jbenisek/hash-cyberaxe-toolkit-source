import sys, math, re, io, contextlib
src = open('lowm.py', encoding='utf-8').read()
src = src.split("if __name__ == '__main__':")[0]
def load(patches):
    s = src
    for a, b in patches:
        assert a in s, a
        s = s.replace(a, b)
    ns = {'__name__': 'lowm_variant'}
    exec(compile(s, 'lowm_variant', 'exec'), ns)
    return ns
base = load([])
def run(ns):
    out = ns['ledger'](show=False)
    tab, tot = ns['memory_bytes']()
    return out, tab, tot
b, tab, tot = run(base)
print('BASE time_log2', b['time_log2'], 'log2_T', b['log2_T'], 'bytes', tot, 'vbar', b['vbar'], 'fixed', b['fixed'], 'g', b['g'])
res = {}
# REGS: one batch per sweep (needs ~28 planes < 32 regs): nsw = nb
vA = load([("nsw = (nb + 1) // 2", "nsw = nb")])
oA, _, _ = run(vA); res['REGS32_one_batch_sweep'] = oA
# PLANES recompute from the packed entries per use (naive bit insertion 3 ops, 64 word loads)
vB = load([("def sp_loads(k): return 2 * (len(MB) - k) + 2", "def sp_loads(k): return (len(MB) - k) * 256 * 3 + 64 + 2")])
oB, _, _ = run(vB); res['PLANES_recompute_per_batch_use'] = oB
# ENTRIES recompute per scan lane from the planes: extract s (3 ops/plane) + S0 (11) + pack (2) - the load (1)
vC = load([("def lane_costs(nls): return sum(SCAN_LANE + EXTR[L // 64] for nl in nls for L in range(nl))",
            "LANE_X = 0\ndef lane_costs(nls): return sum(SCAN_LANE + LANE_X + EXTR[L // 64] for nl in nls for L in range(nl))"),
           ("nr = n >> k; nb = (nr + 255) // 256; nls = [min(256, nr - 256 * b) for b in range(nb)]; j = k - bin(Q0).count('1')",
            "global LANE_X; LANE_X = 3 * (len(MB) - k) + 13 - 1\n    nr = n >> k; nb = (nr + 255) // 256; nls = [min(256, nr - 256 * b) for b in range(nb)]; j = k - bin(Q0).count('1')")])
oC, _, _ = run(vC); res['ENTRIES_recompute_per_lane'] = oC
for k, o in res.items():
    print(k, 'time_log2', o['time_log2'], 'log2_T', o['log2_T'], 'delta_bits', o['log2_T'] - b['log2_T'], 'vbar', o['vbar'], 'nfb log2', o['log2_nfb'])
print('len(MB)', base['len'](base['MB']) if False else len(base['MB']))
