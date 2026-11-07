
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

import json,sys,os
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig')); import add_cell
o=json.load(open('scan_out.json')); dep=o['dep']
OUT=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U14')
CALL={'C2':'C2 = G(2,6,10,14)','C3':'C3 = G(3,7,11,15)','E0':'E0 = G(0,5,10,15)','E1':'E1 = G(1,6,11,12)','E2':'E2 = G(2,7,8,13)','E3':'E3 = G(3,4,9,14)'}
role={
'C2.x':('free-looking solved word','N'),'C2.y':('free-looking solved word','N'),
'C3.x':('PINNED, cancelling (A and B differ by +8)','P'),'C3.y':('PINNED constant, equal in A and B','P'),
'E0.x':('free-looking solved word','N'),'E0.y':('free-looking solved word','N'),
'E1.x':('free-looking solved word (D2.a1 chain)','N'),'E1.y':('FREE word w5, cancelling at K2, differing (-8) at this read','N'),
'E2.x':('free-looking solved word','N'),'E2.y':('FORCED constant 0 (padding)','0'),
'E3.x':('FORCED constant 0 (padding)','0'),'E3.y':('free-looking solved word','N')}
r0names={'K3':'K3.y','K0':'K0','D2':'D2','D1':'D1','D0':'D0','D3':'D3','K2':'K2'}
recs=[]
for cell in ['C2.x','C2.y','C3.x','C3.y','E0.x','E0.y','E1.x','E1.y','E2.x','E2.y','E3.x','E3.y']:
    r=o[cell]; c=cell[:2]; w=r['word']; p=cell[3]
    pu=r['r1_use_perturb']; r0=r['r0_use']; n=r['nb']
    eo=r['call_outputs_equal_AB(a,b,c,d)']; ei=r['call_inputs_equal_AB(a,b,c,d)']
    ch=pu['A_digest_word_changed_counts']; chw=[i for i in range(8) if ch[i]==pu['n']]
    d_=dep[str(w)]
    typ='constant %s in %d/2000 builds'%(r['const_value'],2000) if r['const_value'] else '%d distinct values in 2000 builds, max bit bias %.3f (uniform within noise)'%(r['distinct_values'],r['maxbias'])
    num=("m%d at %s.%s (round 1, step q%d), role: %s. %s; A and B differ in this word in %d/2000 builds. At the call: inputs a,b,c,d equal A vs B %s of %d, outputs a,b,c,d equal %s of %d, x equal %d, y equal %d. "
         "Perturbing ONLY this read (xor delta in both A and B): half-collision words 0,2,5,7 kept %d/%d; digest words of A that change: %s. "
         "Round-0 use of the same word (%s.%s): same delta in both messages breaks the X3,X7,X11,X15 pins %d/%d times (pins kept %d); X after round 0 still equal A vs B %d/%d. Free inputs the word depends on: %s. Counts, 2 rounds, 12-word-level construction b3lib.build (seed 14)."
         %(w,c,cell[3],1 if p=='x' else 3,role[cell][0],typ,r['A_B_differ'],ei,n,eo,n,r['xy_equal_AB'][0],r['xy_equal_AB'][1],
           pu['H_halfcollision_kept'],pu['n'],chw,r0['call'],r0['pos'],pu['n']-r0['X3_7_11_15_pins_kept'],pu['n'],r0['X3_7_11_15_pins_kept'],r0['X_after_round0_equal_AB'],pu['n'],d_ if d_ else 'none (constant)'))
    agree={'C2.x':'Two uses: K3.y (solved so X3/X7 chain holds) and C2.x (difference-free read); same value, roles differ (forced in round 0, free ride in round 1) - they do not conflict.',
     'C2.y':'Two uses: K0.x (solved by K0 inverse, from S4,S8) and C2.y (difference-free read); same value, no conflict.',
     'C3.x':'Two uses: K2.x (the cancelling pair w4,w5 = Lemma L) and C3.x (Fact P pin); both demand the one value W4 = 97475638, no conflict; the +8 difference born at K2 is the one C3 absorbs into b,d.',
     'C3.y':'Two uses: D2.y (round 0, X13/X2 chain) and C3.y (Fact P pin); both demand W13 = 0007c006, no conflict.',
     'E0.x':'Two uses: K0.y and E0.x; value solved by K0 inverse; difference-free at E0 (E0 reads neither pinned word), no conflict.',
     'E0.y':'Two uses: D1.y and E0.y; solved by D1 inverse; difference-free at E0, no conflict.',
     'E1.x':'Two uses: D2.x and E1.x; w12 solved from X2 (D2 chain); the read itself is equal A vs B but E1 sees a differing c input (Y11) so the residual is born here.',
     'E1.y':'Two uses: K2.y (cancelling: w5p=w5+W4-W4p) and E1.y (reads w5 in A, w5-8 in B). The two uses agree on the value but NOT on the role: at K2 the -8 cancels, at E1 it is a live input difference that enters the residual words 1,3,4,6.',
     'E2.x':'Two uses: D0.y and E2.x; solved by D0 inverse; E2 reads nothing that differs, so this read is difference-free (digest words 0,2,5,7 exact).',
     'E2.y':'Two uses: D3.x and E2.y; padding zero in both; consistent, constant 0, not a degree of freedom.',
     'E3.x':'Two uses: D3.y and E3.x; padding zero in both; consistent, constant 0.',
     'E3.y':'Two uses: D0.x and E3.y; solved by D0 inverse; E3 reads differing Y3 (input a) but the word read is equal A vs B.'}[cell]
    rec=dict(hash='blake3-r2',row_i=None,row_j=None,
      object='read %s of call %s = message word m%d, round 1 (MSG.%s)'%(cell[3],c,w,cell),
      question='Q1 word role (free / pinned / cancelling / forced) at THIS use, and whether the word\'s two uses agree',
      labels=[role[cell][1]],status='COMPUTED',number=num,source='our workflow: scan-once-wave2',own_test=True,
      evidence='research/dig/incoming2/blake3-r2-G05-U14/work/scan.py; scan_out.json; make_records.py; own reference validated on 16 known vectors vs hash-smash/verifier/blake3.py (1,2,7 rounds) and the pair (digest words 0,2,5,7 equal) via the verifier',
      date='2026-10-12',lever=False,gain_bits=None,
      notes='universe cell blake3-r2|MSG.%s|MSG|Q1. %s Construction used: pkgB3U root-block variant (own b3lib.build, single block, counter 0); the pkgCK counter variant additionally solves w0 from the chunk counter t (Lemma TR), not run here. Measured on 2,000 builds (600 for perturbation tests); no gain claimed. Existing word cells (C0028-C0035, C0056-C0059, C0084-C0087 and the per-word records) not redone; this is the per-use view.'%(cell,agree))
    fn=os.path.join(OUT,'blake3-r2_MSG.%s_MSG_Q1.json'%cell)
    json.dump(rec,open(fn,'w',encoding='utf-8'),indent=1)
    errs=add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load())
    print(cell,errs)
