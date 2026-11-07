import json,glob,collections,statistics as S
rows=[];
for f in sorted(glob.glob("conn_k*.json")):
    d=json.load(open(f)); 
    ok=[a for a in d["attempts"] if a.get("status")=="ok"]
    print(f,"advice c,j,DF",d["c"],d["j"],d["advice_DF"],"attempts",len(d["attempts"]),"ok",len(ok),collections.Counter(a["status"] for a in d["attempts"]))
    for a in ok: a["k"]=d["k"]
    rows+=ok
def rng(key): v=[a[key] for a in rows]; return (min(v),max(v),round(S.mean(v),2))
print("n ok",len(rows))
for key in ["nFIX","ED_F","inactive_rows","active_rows_alpha1","ED_after_zero","ED_after_D2","EM_M1","EM_M2","EM_M3","lin_rows","n_row_masks","n_conditions_M4","EM_M4","DF"]:
    print(key,rng(key))
for a in rows[:0]: pass
print("M2 added",[ (a["EM_M2"]-a["EM_M1"]) for a in rows][:5], "range",min(a["EM_M2"]-a["EM_M1"] for a in rows),max(a["EM_M2"]-a["EM_M1"] for a in rows))
print("M3 added",min(a["EM_M3"]-a["EM_M2"] for a in rows),max(a["EM_M3"]-a["EM_M2"] for a in rows))
print("M4 added",min(a["EM_M4"]-a["EM_M3"] for a in rows),max(a["EM_M4"]-a["EM_M3"] for a in rows))
print("DF after M3 (1600-EM_M3)",min(1600-a["EM_M3"] for a in rows),max(1600-a["EM_M3"] for a in rows))
print("DF dist",sorted(collections.Counter(a["DF"] for a in rows).items()))
print("DF<33?",sum(a["DF"]<33 for a in rows))
