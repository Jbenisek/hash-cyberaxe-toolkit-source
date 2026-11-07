import numpy as np
from scipy.stats import ks_2samp
a={k:np.fromfile('gd_k%d_s101.bin'%k,dtype=np.uint32) for k in (0,1,2)}
for x,y in ((0,1),(0,2),(1,2)):
    r=ks_2samp(a[x],a[y]); print('KS kind',x,'vs',y,'D=%.5f p=%.4f'%(r.statistic,r.pvalue))
