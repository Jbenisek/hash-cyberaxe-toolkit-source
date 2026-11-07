import sys,json; sys.path.insert(0,'.')
from t1_q1_chi2 import run
out={}
for d in [None,'L16','L5','L15','D3','L8']:
    r=run(d,N=512,seed=11,verbose=False); out[str(d)]=r
    print(d,json.dumps(dict(aff=r['affine_fail_pairs'],sup=r['support_words'],uni=r['uniform_allones_all_j'],rows=r['rows_touched'],o2p=r['o2p_changed_words_union_over_slices'])))
json.dump(out,open('t3_q2_drop_out.json','w'),indent=1)
