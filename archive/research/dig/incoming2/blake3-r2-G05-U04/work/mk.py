
# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, sys, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
W='research/dig/incoming2/blake3-r2-G05-U04/work/'
def rec(cell,obj,q,labels,status,number,ev,notes):
    return dict(hash='blake3-r2',row_i=None,row_j=None,object=obj,question=q,labels=labels,status=status,number=number,
      source='our workflow: scan-once-wave2',own_test=True,evidence=ev,date='2026-10-12',lever=False,gain_bits=None,
      notes=notes+' universe cell '+cell,topic=cell.split('|')[1].lower()+'.'+cell.split('|')[3].lower())
R=[]
R.append(rec('blake3-r2|INIT.v14|INIT|Q2','v14 = block_len b: is the 55/63 difference necessary (relax/replace)?',
 'Relax or replace the length pair: exact count of (w4\',w5\') pairs leaving the K2 call output (hence round-0 state X) unchanged.',['E','I'],'COMPUTED',
 'exactly 1 pair (w4\',w5\') per (w4,w5) and per partner length b\'; exhaustive 2^32 scan x\' for 55->63 and 55->54: 1 solution each (w4\'=w4+8,w5\'=w5-8 for sample 12345678/9abcdef0); same-length control: 1 (the identity); 64 of 64 partner lengths b\' equalise X in 100/100 random messages; 300 byte-level 55/63 pairs match organizer verifier r2; no cancel (control) gives X_equal 0/3000, 8 active round-1 calls',
 W+'b3.py, '+W+'t1.py, '+W+'t1_out.json, '+W+'scan.c, '+W+'scan_out.txt',
 'Reference validated first: empty-input r7 digest af1349b9..., 240 single-block r2/r7 messages equal to hash-smash/verifier/blake3.py. Inversion argument: equal G outputs fix d1,b1,c1,a2, so (x\',y\') is unique for ANY initial d\', hence the 55/63 choice is not necessary for cancellation; a length difference is only needed to have two distinct legal messages (without any v14/v15 difference the identity is the only equaliser). Legal shorter length is limited by the pinned zero bytes (W13 uses bytes 52-54). Not a gain claim.'))
R.append(rec('blake3-r2|INIT.v14|INIT|Q3','v14 = block_len b: degrees of freedom over carries of the cancelling shift w4\'-w4',
 'Exact count of the carry cases: how many values does D=w4\'-w4 take over all 2^32 w4 and how often?',['C','I'],'COMPUTED',
 'delta=55^63=8: D takes exactly 2 values, +8 and -8, 2^31 w4 each (exhaustive over 2^32); general delta takes 2^popcount(delta) values, 2^(32-popcount) w4 each (checked exhaustively for delta 8, 7, 15: 2, 8, 16 values); w5\' - w5 = -D; total 2^64 equalising (w4,w5)->(w4\',w5\') quadruples per ordered length pair',
 W+'hist.c, '+W+'t2.py, '+W+'t2_out.json',
 'The paper pin W4=97475638 has K2+W4=f33a2355 with bit 3 = 0, so D=+8 (W4\'=97475640); the -8 branch (half of all w4) fails the C3 pins with the same X3,X7,X11,X15,W13 (b and d outputs differ). So the pinned family uses the half of w4 space with bit 3 of K2+w4 = 0; no extra freedom from the other sign without re-solving the pins (not done).'))
R.append(rec('blake3-r2|INIT.v14|INIT|Q4','v14 = block_len b: alternative length pairs and whether the existing C3 pins carry over',
 'For every partner length b\' of 55 (1..64), does the existing pin set (X3,X7,X11,X15,W4,W13) still give equal C3 b and d outputs?',['K','I'],'LOCAL_ONLY',
 'only b\'=63 of 63 partners keep the pins (62 fail); D=+8 holds, D=-8, +-16 fail; 45 length pairs lie in 55..64 (W13 bytes 52-54 need shorter length >= 55)',
 W+'t2.py, '+W+'t2_out.json',
 'LOCAL_ONLY: window is the fixed pin set from pkgCK, other pairs would need new pins (Fact P re-solved for their D); that re-solve and the digest-pin count for them (door 24 bijection test on E1/E3 inputs) were NOT run. X equality itself holds for all partners (see Q2 record). Reproduced paper C3 outputs b=76f7aefd d=bbfbdffe.'))
R.append(rec('blake3-r2|INIT.v15|INIT|Q2','v15 = flags: is 11 vs 12 (delta 7) necessary / exact outcome mass of the K3 cancel',
 'Cancel flags difference in round 0 through K3 (w6,w7) and count the exact outcome mass; door 21 RELABEL test: word-level simulation of delta 7 through round 1, count active G calls.',['E','I','C'],'COMPUTED',
 'exhaustive 2^32 scan: exactly 1 (w6\',w7\') for flags 11->12 (w6\'=w6+1,w7\'=w7-1 for sample), identity-only for 11->11; all 16 partner flag values equalise X in 100/100 samples; round 1 then has 6 active G calls (C0,C2,E0,E1,E2,E3) in 3000/3000 samples, 8 differing round-1 input words (C0.y, C2.x, E0.a/c, E1.b/d, E2.a/c, E3.b/d), all 8 digest words differ; same 6 calls for partners 10,9,3,15 (word-level, cv=IV)',
 W+'t1.py, '+W+'t1_out.json, '+W+'t4.py, '+W+'scan.c, '+W+'scan_out.txt',
 'Door 21 structure confirmed (y-diff at column 0, x-diff at column 2, all four diagonals touched, 8 conditions). C0 y-difference makes all four C0 outputs differ (injectivity of the second half), so no Fact-P style pin exists there; the 256-bit residual stays DERIVED (an upper cost), not measured. Compression-level simulation: a flags-12 message needs PARENT/ROOT structure whose words are chaining values, not free words. Compare length cancel: 5 active calls (3 with pins).'))
R.append(rec('blake3-r2|INIT.v15|INIT|Q4','v15 = flags: alternative flag pairs and combination with the length line',
 'Which other flag pairs are possible and what does combining flags and length cancels cost in active round-1 calls?',['E','K'],'COMPUTED',
 'flags+length cancels together: 7 active round-1 calls (C0,C2,C3,E0-E3), 16 differing input fields, vs 5 (length only, 3 with pins) and 6 (flags only); control no cancel 8; legal root flags for cv=IV are only 11 (1-block chunk) and 12 (parent); 10 needs a chained cv (not IV); 3000/3000 samples each',
 W+'t1.py, '+W+'t1_out.json, '+W+'t4.py',
 'Confirms door 21 remark that a combined line is strictly worse. Legality of flags 10/9/3/15 not checked beyond the rule list (word-level sim only). Parent-root flags-12 line with free message words is not legal (words are chaining values), so only a message-level cost, not tested here.'))
os.makedirs('.',exist_ok=True)
ex=add_cell.load()
for r in R:
    cell=r['notes'].split('universe cell ')[1]
    fn=cell.replace('|','_')+'.json'
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    print(fn,add_cell.validate(json.load(open(fn,encoding='utf-8')),ex))
