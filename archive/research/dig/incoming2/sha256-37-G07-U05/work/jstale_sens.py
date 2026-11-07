import sys,io,contextlib,importlib.util,os
sys.argv=['x']
spec=importlib.util.spec_from_file_location('js','jstale_scan.py'); js=importlib.util.module_from_spec(spec); spec.loader.exec_module(js)
T,m=js.truth('pkgR37M3')
def tl(**kw):
    with contextlib.redirect_stdout(io.StringIO()): return m.ledger(show=False,**kw)
base=tl()
print('Q3_LOG2 default',m.Q3_LOG2,'time',base['time_log2'])
for name,want,kw in (('q3 one bit lower 2^-72.47',61.57158,dict(q3_log2=-72.47)),('Table 15 value 2^-74.03',62.76763,dict(q3_log2=-74.03)),('four patterns alone 2^-72.02',61.28957,dict(q3_log2=-72.02))):
    got=tl(**kw)['time_log2']; print('%-32s text %.5f ours %.5f %s'%(name,want,got,'MATCH' if abs(got-want)<1.5e-5 else 'DIFF'))
b=tl()['log2_T']
for q in (-71.47,-71.0,-72.47):
    print('q3 %.2f time %.5f'%(q,tl(q3_log2=q)['log2_T']))
d=(tl(q3_log2=m.Q3_LOG2-0.01)['log2_T']-b)/0.01; print('slope bit/bit at charge: %.4f'%d)
print('pcap_assumed',base.get('pcap_assumed'))
import math
nfb=base['nfb']; N=int(base['T_num'])
print('bit per +1 op/fb: %.3e'%(nfb*(1+2**-12)/N/math.log(2)))
print('memory headroom to 2^20: %d bytes (%.1f%%)'%(2**20-int(T['mem']),(2**20/int(T['mem'])-1)*100), 'log2 mem %.5f'%math.log2(int(T['mem'])))
