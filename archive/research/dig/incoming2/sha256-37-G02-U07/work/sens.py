import sys, math, tracemalloc, importlib.util
sys.argv=['x']
spec=importlib.util.spec_from_file_location('lm','lowm_final.py'); lm=importlib.util.module_from_spec(spec); spec.loader.exec_module(lm)
for name,p in [('pre0',0),('pre2^38',1<<38),('pre2^40',1<<40),('pre2^44',1<<44),('pre2^50',1<<50)]:
    o=lm.ledger(show=False,pre_ops=p); print(name,o['time_log2'],o['log2_T'],o['preprocessing_log2'])
o=lm.ledger(show=False)
T=o['log2_T']; print('T',T,'floor', o['preprocessing_log2'],'max saving',T-o['preprocessing_log2'])
print('break-even bytes at 2^20*2^saving', 2**20*2**(T-o['preprocessing_log2']))
tab,tot=lm.memory_bytes(); print(tot, 2**20-tot, 2**20-(tot-65536))
# tracemalloc of Env build
tracemalloc.start(); env=lm.Env()
for l in sorted(set(env.lid)): env.getlist(l)
print('tracemalloc env cur/peak',tracemalloc.get_traced_memory())
