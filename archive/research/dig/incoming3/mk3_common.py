import json, os
BASE=dict(hash="blake3-r3",row_i=None,row_j=None,source="our workflow: dig-scan-b3r3",own_test=True,date="2026-10-12",lever=False,gain_bits=None)
OUT=os.path.dirname(os.path.abspath(__file__))
def ev(unit,*files): return ", ".join("research/dig/incoming3/%s/work/%s"%(unit,f) for f in files)
recs=[]
def add(unit,cell,obj,q,labels,status,number,evidence,notes,held,reopen,**kw):
    d=dict(BASE); d.update(object=obj,question=q,labels=labels,status=status,number=number,evidence=evidence,
           notes="universe cell %s. %s"%(cell,notes),held_fixed=held,reopen_if=reopen); d.update(kw)
    recs.append((unit,cell,d))
KNOWN="Known answers first (validate.out): own numpy compress == organizer verifier _compress on 1200 random calls at rounds 1/2/3/7, 0 mismatches; BLAKE3('') 7 rounds = af1349b9...f3262; rho.py digest_words == verifier blake3(0^32||x) at 7 and 3 rounds (300 each, 0 mismatches); packed 7-lane circuit == verifier at 3 rounds (700 lanes, 0 mismatches)."
